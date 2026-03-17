import {useState} from "react";
import {useNavigate} from "react-router-dom";
import TextInput from "../components/TextInput";
import SubmitButton from "../components/SubmitButton";
import {customHeader} from "../utils/authUtils"
import { decideHost } from "../utils/utilFuncs";
import "../styles/LoginPage.css";
const HOST = decideHost();

function LoginPage({setUser}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("")
  const navigateObject = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    try {
      const response = await fetch(`${HOST}/api/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // custom header for hardening against CSRF
          [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
        },
        body: JSON.stringify({ username: username, password: password }),
        credentials:"include" // match Flask expected values, and look for the set-cookie header
        });
      const data = await response.json(); // convert json string to object via parsing; assumes that backend ALWAYS RETURNS JSON
      if (response.ok) {
        setError("");
        console.log("Login successful!", data);
        setUser(data);
        // send to correct dashboard after authorisation data 'is_admin' is returned
        data.is_admin?navigateObject("/admin/dashboard")
                     :navigateObject("/user/dashboard");
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      console.error("Network error:", err);
      setError("Network error");
    }
  }

  // Handle signup button click
  function handleSignUp(e){
    e.preventDefault();
    navigateObject("/signup");
  }

  return (
    <div className="login-container">
      <h2>Login Page</h2>

      <form onSubmit={handleLogin}>
        <TextInput
          id = "username_input"
          label="Username"
          type="text"
          required
          pattern="^[a-zA-Z0-9]{5,10}$" // Reglar Expression allowing letters, numbers and length b/w 5 and 10
          title="Username must be at between 5 and 10 alphanumeric characters."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <TextInput
          id = "password_input"
          label="Password"
          type="password"
          required
          pattern="^\S{8,20}$"
          title="Password must be between 8 and 20 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <SubmitButton id="submit_button_login">Login</SubmitButton>
      </form>
      {/*If error has been set (truthy value) '&&' makes the expression default to the <p> element, making react render the error text
      If error is not set (falsy value), '&&' defaults to the preceding expression 'error' so react will not render the <p>*/}
      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
      <div  className="signup-container">
        <button className="submit-button" onClick={handleSignUp}>Sign Up</button>
      </div>
    </div>
  );
}

export default LoginPage;