export class LoginPage{
    constructor(page){
        this.page = page;
        this.loadingAnim = page.locator("#loading-screen");
        this.loginContainer = page.locator("#login-container");
        this.signupContainer = page.locator("#signup-button-container");
        this.loginUsernameField = page.locator("#username-input-login");
        this.loginPasswordField = page.locator("#password-input-login");
        this.signupStartButton = page.locator("#signup-start-button");
    }
    /**
     * Function to wait till load animation is not visible after 2 seconds and login container is.
     */
    async waitForLoad(){
        await this.loginContainer.waitFor({ state:'visible'});
    }

    async goto(){
        await this.page.goto('/');
    }
}