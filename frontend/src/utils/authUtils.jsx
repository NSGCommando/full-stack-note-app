export const clearSessionData = () => {
    window.history.replaceState?.({}, document.title);
}

export const customHeader = Object.freeze({
    CUSTOM_HEADER_FRONTEND:"R-Application-Service",
    CUSTOM_HEADER_FRONTEND_RESPONSE:"Frontend-Service-R"
})

export const HOST = "http://localhost:5000";