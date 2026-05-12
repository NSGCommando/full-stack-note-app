export class LoginPage{
    constructor(page){
        this.page = page;
        this.loadingAnim = page.locator("#loading-screen");
        this.loginContainer = page.locator("#login-container");
        this.signupContainer = page.locator("#signup-button-container");
    }
    /**
     * Function to wait till load animation is not visible after 2 seconds and login container is.
     */
    async waitForLoad(){
        await this.loginContainer.waitFor({ state:'visible'});
    }
}