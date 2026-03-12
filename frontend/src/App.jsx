import './App.css';
import {useEffect, useState,useRef} from 'react'
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import {customHeader} from "./utils/authUtils"
import LoginPage from './pages/LoginPage';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import SignUp from './pages/SignUp';

function App() {
  const navigateObject = useNavigate();
  const locationObject = useLocation();

  // State to prevent the "flicker" of protected content
  const [isVerifying, setIsVerifying] = useState(true);
  const [user, setUser] = useState(null);
  // flag for guarding against duplicate fetch calls
  const checkVerifyOnce = useRef(false);

  useEffect(()=>{
    if(!checkVerifyOnce.current){
      checkVerifyOnce.current = true;
      const verifyUser=async()=>{
        try{
          const response = await fetch("http://localhost:5000/verify_token", {
                  method: "GET",
                  headers: {
                    "Content-Type": "application/json",
                    // custom header for hardening against CSRF
                    [customHeader.CUSTOM_HEADER_FRONTEND]: customHeader.CUSTOM_HEADER_FRONTEND_RESPONSE
                  },
                  credentials:"include" // match Flask expected values, and look for the set-cookie header
                });
          if(response.ok){// shorthand for checking if status code is in success range (200-299)
            const data = await response.json();
            setUser(data);
            console.log("User session is valid");
            // send to correct dashboard after if token is valid and they're still on login page
            if (locationObject.pathname === "/"){
              data.is_admin?navigateObject("/admin/dashboard",{replace:true})
                        :navigateObject("/user/dashboard",{replace:true});
            }
          }
        }
        catch{
          setUser(null)
          navigateObject("/",{replace:true})
        }
        finally{
          setIsVerifying(false)
        }
      };
      verifyUser();
    }
    
  },[navigateObject,locationObject.pathname])

  if (isVerifying) {
  return <div className="loading-screen">Checking your session...</div>;
  }

  return(
    <Routes>  
      <Route path="/" element = {<LoginPage setUser={setUser}/>}/>
      {/*user? returns undefined if user doesn't exist, so user?.is_admin beceomes undefined and redirect happens*/}
      <Route path="/admin/dashboard" element = {user?.is_admin?<AdminDashboard user={user} setUser={setUser}/>:<Navigate to="/" />}/>
      {/*we want to kick out admins from the user-dashboard, so invert the is_admin check
      In JS, (A && B) never evaluates B if A is falsy, so we guarantee user.is_admin isn't accessed unless user exists*/}
      <Route path="/user/dashboard" element = {(user && !user.is_admin)? <UserDashboard user={user} setUser={setUser}/> : <Navigate to="/" />}/>
      <Route path="/signup" element = {<SignUp/>}/>
    </Routes>
  )
 }

export default App;