import {useRef,useState,useEffect} from "react";
import { useLocation } from "react-router-dom";
import {customHeader} from "../utils/authUtils"
import { decideHost } from "../utils/utilFuncs";
const HOST = decideHost();

export function useAuthVerify(navigateObject){
    const locationObject = useLocation();
    // flag for guarding against duplicate fetch calls
    const checkVerifyOnce = useRef(false);
    const [user, setUser] = useState(null);
    // State to prevent the "flicker" of protected content
    const [isVerifying, setIsVerifying] = useState(true);
    useEffect(()=>{
    if(!checkVerifyOnce.current){
      checkVerifyOnce.current = true;
      const verifyUser=async()=>{
        try{
          const response = await fetch(`${HOST}/api/verify_token`, {
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
            if (window.location.pathname === "/") {
               navigateObject(data.is_admin?"/admin/dashboard":"/user/dashboard",{replace:true});
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
    
  },[navigateObject]);

  // second useEffect to dynamically redirect existing users after the user has been confirmed
  useEffect(()=>{
    if (!user) return;
    if(locationObject.pathname==="/"){
      navigateObject(user.is_admin?"/admin/dashboard":"/user/dashboard",{replace:true});
    }
  },[user, locationObject.pathname, navigateObject]) // Only run this useEffect if specific variables change to save unnecessary calls

  return {user,setUser,isVerifying}
}