import {useState,useEffect,useRef} from "react";
import { useNavigate } from "react-router-dom";
import { customHeader } from "../utils/authUtils";
import { decideHost } from "../utils/utilFuncs";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import TableFactory from "../components/TableFactory";
import "../styles/UserDashboard.css";
const HOST = decideHost();

function UserDashboard({user,setUser}){
    const [notesList, setNotesList] = useState([]);
    const [error, setError] = useState("");
    const [showNoteInput, setShowNoteInput] = useState(false);
    const [newNote, setNewNote] = useState("");
    const fetchOnLogin = useRef(false);

    // load pre-existing notes list on user confirmation once after login
    useEffect(() => {
        if(user && !user.is_admin && !fetchOnLogin.current) {
            handleNotesRefresh();
            fetchOnLogin.current = true; // Use a reference to main initial note-loading idempotent to retries
        }
        }, [user]); // run once on user state change

    // navigate hook
    const navigateObject = useNavigate();

    // View Notes function
    async function handleNotesRefresh(){
        try{
                const response = await fetch(`${HOST}/api/user-view-notes`,{
                    method:"GET",
                    headers:{"Content-Type":"application/json",
                            [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE},
                    credentials:"include" // JWT token for user id
                })
                const data = await response.json();
                if(response.ok){
                    setError("");
                    setNotesList(data.notes);
                }
                else{setError(data.error);}
        }
        catch(err){
            setError("Network error", err);
        }
    }

    // Create New Note function
    async function handleShowNoteInput(){setShowNoteInput(true)}

    // Add Notes function
    async function handleAddNote(e){
        e.preventDefault();
        try{
            const response = await fetch(`${HOST}/api/user-add-note`,{
                method:"POST",
                headers:{"Content-Type":"application/json",
                        [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                        },
                body:JSON.stringify({note:newNote}),
                credentials:"include" // JWT token for user id
            })
            const data = await response.json();
            if(response.ok){
                setError("");
                setShowNoteInput(false);
                handleNotesRefresh(); // refresh the notes list
                setNewNote(""); // reset the stored note after successful submission
                
            }
            else{setError(data.error);}
        }
        catch(err){setError("Network error", err);}
    }
    
    // delete note function
    async function deleteNote(noteID){
        // handle user deletion
        try{
            const response = await fetch(`${HOST}/api/notes-delete`,{
                                            method:"DELETE", 
                                            headers:{"Content-Type":"application/json",
                                                    [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                                            },
                                            body:JSON.stringify({note_id:noteID}),
                                            credentials:"include" // JWT token for verification
                                        })
            if(response.ok){
                setError("");
                handleNotesRefresh(); // refresh the notes list
            }
            else{setError("deletion failed");}
        }
        catch(err){
            setError("Network error", err);
        }
    }

    // Logout function
    async function handleLogout(e){
            e.preventDefault();
            try {
                await fetch(`${HOST}/api/logout`, // Cookie invalid, inform the server 
                    {
                    method: "GET",
                    headers:{   "Content-Type": "application/json",
                                [customHeader.CUSTOM_HEADER_FRONTEND]:customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                            },
                    credentials: "include" 
                });
            } 
            catch(err) {setError("Server logout failed, but clearing local state anyway.", err);} 
            finally {
                setUser(null);
                navigateObject("/", { replace: true });
            }
        }
    return(
        <div id="dashboard-container">
        <h1>User Dashboard</h1>
        {error && <div className="error-banner">{error}</div>}
            <p>Login was successful, User {user.username}</p>
            {/* Notes button*/}
            <div id="notes-container">
                <button onClick={handleShowNoteInput}>Add New Note</button>
                <div id="user-note-add">
                {showNoteInput && (
                    <form id="new-note-form" onSubmit={handleAddNote}>
                        <TextInput className="text-input"
                        id="note_input"
                        label="New Note"
                        type="text"
                        required
                        placeholder="Enter your note..."
                        value={newNote}
                        onChange={(e) => setNewNote(e.target.value)}
                    />
                    <SubmitButton id="submit_button_signup_username">Enter</SubmitButton>
                    </form>
                )}
                </div>
                <div id="user-notes-container">
                    <TableFactory dataList={notesList} deleteEntry={deleteNote}/>
                </div>
            </div>
            {/* Logout button*/}
            <div id="logout-container">
                <button onClick={handleLogout}>Logout</button>
            </div>
        </div>
    )
}

export default UserDashboard;