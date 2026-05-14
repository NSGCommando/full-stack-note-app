export class SignupStage2{
    constructor(page){
        this.page = page;
        this.signupContainer = page.locator("#signup-container");
        this.signupPasswordField = page.locator("#password-input-signup");
        this.submitButton = page.locator("#submit-button-signup-password");
    }
    /**
     * Function to check if required field is visible now.
     */
    async fillPasswordField(username){
        await this.signupPasswordField.fill(username);
    }
}