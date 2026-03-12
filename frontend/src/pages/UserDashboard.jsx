import {useState,useEffect,useRef} from "react";
import { useNavigate } from "react-router-dom";
import { customHeader,HOST } from "../utils/authUtils";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import "../styles/UserDashboard.css"

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
    
    // Logout function
    async function handleLogout(e){
            e.preventDefault();
            try {
                await fetch(`${HOST}/logout`, // Cookie invalid, inform the server 
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
                        label="new_note"
                        type="text"
                        placeholder="Enter your note..."
                        value={newNote}
                        onChange={(e) => setNewNote(e.target.value)}
                    />
                    <SubmitButton id="submit_button_signup_username">Enter</SubmitButton>
                    </form>
                )}
                </div>
                <div id="user-notes-container">
                    {notesList.length>0?
                    (
                        <table class="user-notes">
                            <thead>
                                <tr>
                                    <th>No.</th>
                                    <th>Note</th>
                                    <th>Date Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {notesList.map((note,index)=>(
                                    <tr key={note.id}>
                                        <td>{index+1}</td>
                                        <td>{note.note}</td>
                                        <td>{note.timestamp}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ):
                    (<span>No notes found for user {user.username}</span>)
                    }
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