import {useRef,useEffect} from "react";
import { decideHost } from "../utils/utilFuncs";
const HOST = decideHost();

/**
 * @description This is a React Hook to load the list of user's notes once when the User Dashboard is mounted
 * @param {*} user Object representing logged in user
 * @param {*} notesRefresher Callback function for refreshing the user's notes list
 */
export function useUserNotesLoadOnce(user,notesRefresher){
    const fetchOnLogin = useRef(false);
    useEffect(() => {
        if(user && !user.is_admin && !fetchOnLogin.current) {
            notesRefresher();
            fetchOnLogin.current = true; // Use a reference to make initial note-loading idempotent to retries
        }
        }, [user, notesRefresher]); // run once on user state change
}