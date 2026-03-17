import { HOST } from "./authUtils";

/**
 * A helper function to decide what the base URL should be
 * @param {str} host - default HOST URL to fallback to
 * @returns {str} Returns either the fallback HOST or empty string if running in Docker
 */
export function decideHost(){
    const isDocker = import.meta.env.VITE_IS_DOCKER === "true";
    return isDocker ? "" : HOST;
}

export function titleCaseFormat(str) {
  return str.toLowerCase().split(" ").map((word)=>(
      word.charAt(0).toUpperCase()+word.slice(1))).join(" ")
}