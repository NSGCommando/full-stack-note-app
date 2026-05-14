import { useState } from "react";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import { useNavigate } from "react-router-dom";
import {customHeader} from "../utils/authUtils";
import { decideHost } from "../utils/utilFuncs";
import "../styles/LoginPage.css";
const HOST = decideHost();

function SignUp(){
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [signupStage, setSignupStage] = useState(1);
    const navigateObject = useNavigate(); // navigate hook

    async function checkUsernameSignUp(e){
        e.preventDefault();
        try{
            const response = await fetch(`${HOST}/api/check_username`, 
                {method:"POST", 
                    headers:{"Content-Type": "application/json",
                            [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE}, 
                        body:JSON.stringify({username:username})});
            if(response.status === 409){
                setError("Username is already taken. Please try another!")
            }
            else{setSignupStage(2);}
        }
        catch(err){
            console.error("Network error:", err);
            setError("Network error");
        }
    }

    async function handleFinalSignUp(e){
        e.preventDefault();
        try{
            const response = await fetch(`${HOST}/api/signup`, {method:"POST", 
                                            headers:{"Content-Type": "application/json",
                                                    [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE},  
                                            body:JSON.stringify({username:username, password:password})});
            const data = await response.json();
            if(response.status===201){
                setError("");
                console.log("Signup successful!");
                navigateObject("/",{replace:true})
            }
            else{
                console.log("Signup failed!");
                setError(data.error);
            }
        }
        catch(err){
            console.error("Network error:", err);
            setError("Network error");
        }
    }

    return (
        // Ensure to use 'className' and not 'classname'
        // tag or attribute mistakes leaves the render to be ignored, and no error warnings either
        // maybe think of making an html parser for this sort of things
        <div id="signup-container">
            <h1>Signup Page</h1>
            {
                signupStage===1? // conditional rendering using signupStage
                (<form id="signup-username-form" onSubmit={checkUsernameSignUp}>
                    <TextInput className="text-input"
                    id = "username-input-signup"
                    label="Username"
                    type="text"
                    required
                    pattern="[a-zA-Z0-9]{5,10}" // Reglar Expression allowing letters, numbers and length b/w 5 and 10
                    title="Username must be between 5 and 10 alphanumeric characters."
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    />
                    <SubmitButton id="submit-button-signup-username">Enter</SubmitButton>
                </form>)
                :(
                    <form id="signup-password-form" onSubmit={handleFinalSignUp}>
                        <TextInput className="text-input"
                        id = "password-input-signup"
                        label="Password"
                        type="password"
                        required
                        pattern="^\S{8,20}$"
                        title="Password must be between 8 and 20 characters"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        />
                        <SubmitButton id="submit-button-signup-password">Enter</SubmitButton>
                    </form>
                ) 
            }
            
            {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
        </div>
    );
}

export default SignUp;