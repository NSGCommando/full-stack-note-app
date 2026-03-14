import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { customHeader } from "../utils/authUtils";
import { decideHost } from "../utils/utilFuncs";
import "../styles/AdminDashboard.css";
const HOST = decideHost();

function AdminDashboard({user:adminUser,setUser}){
    // navigate(routing) and location(state) hook
    const navigateObject = useNavigate();
    // admin dashboard states
    const [userList, setUserList] = useState([]) // set initial vaflue to [] so the userList.map() doesn't crash on first render
    const [error, setError] = useState("");
    const adminName = adminUser?.username
    
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
        catch(err) {setError("Server logout failed, but clearing local state anyway.",err);} 
        finally {
            setUser(null);
            navigateObject("/", { replace: true });
        }
    }

    // delete user function
    async function deleteUser(targetID){
        // handle user deletion
        try{
            const response = await fetch(`${HOST}/api/users-delete`,{
                                            method:"DELETE", 
                                            headers:{"Content-Type":"application/json",
                                                    [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                                            },
                                            body:JSON.stringify({target_id:targetID}),
                                            credentials:"include" // JWT token for verification
                                        })
            if(response.ok){
                setError("");
                setUserList(prevList => prevList.filter(user=>user.id!==targetID)) // prevList is declared right here
                // to apply the filter on most recent version of userList stored in RAM
                // we only named prevList so as to apply the filter to the data
            }
            else{setError("deletion failed");}
        }
        catch(err){
            setError("Network error", err);
        }
    }
    
    async function showUsers(){
        try{
                const response = await fetch(`${HOST}/api/show-users`,{
                    method:"GET",
                    headers:{"Content-Type":"application/json",
                            [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE},
                    credentials:"include" // JWT token for verification
                })
                const data = await response.json();
                if(response.ok){
                    setError("");
                    setUserList(data.users);
                }
                else{setError(data.error);}
        }
        catch(err){
            setError("Network error", err);
        }
    }
    return(
        <div id="dashboard-container">
            <h1>Admin Dashboard</h1>
            {error && <div className="error-banner">{error}</div>}
                <p>Login was successful, Admin {adminName}</p>
                    <button onClick={showUsers}>View Users</button>
                    {/* display user list, giving a style to div is needed to reserve space below the view button, 
                        or the table would be sent below everything else */}
                    <div className = "user-list-container"> 
                        {userList.length>0?
                        (   <table>
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Username</th>
                                        <th>Role</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {userList.map((user, index)=>(
                                        <tr key={user.id}>
                                            <td>{index+1}</td>
                                            <td>{user.user_name}</td>
                                            <td>{user.is_admin?"Admin":"User"}</td>
                                            <td> 
                                                {/* don't allow admins to delete admins*/}
                                                {!user.is_admin?(
                                                    <button className="user-delete-button" onClick={()=>deleteUser(user.id)}>
                                                    Delete
                                                    </button>
                                                ):
                                                (<span>Protected</span>)
                                                }
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ):
                        (<p>No users loaded</p>)
                        }
                    </div>

            {/* Logout button*/}
            <div id="logout-container">
                <button onClick={handleLogout}>Logout</button>
            </div>
        </div>
        

    )
}

export default AdminDashboard;