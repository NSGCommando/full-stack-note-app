export class SignupStage1{
    constructor(page){
        this.page = page;
        this.signupContainer = page.locator("#signup-container");
        this.signupUsernameField = page.locator("#username-input-signup");
        this.submitButton = page.locator("#submit-button-signup-username");
    }
    /**
     * Function to check if required field is visible now.
     */
    async fillUsernameField(username){
        await this.signupUsernameField.fill(username);
    }
}