import { test, expect } from '@playwright/test';
import { SignupStage1 } from '../pages/signupUsername';
import { SignupStage2 } from '../pages/signupPassword';
import { LoginPage } from '../pages/login';
const SCREENSHOT_SIGNUP = "screenshots/signup-test"

test("Signup Test", async({page, request})=>{
    // navigate to signup page
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.signupStartButton.click();
    await expect(page).toHaveURL("/signup");
    // ensure test db is reset
    await request.post("http://localhost:5000/api/dev/test/reset-db");
    // test signup page
    const signupPage1 = new SignupStage1(page);
    await expect(signupPage1.signupContainer).toBeVisible();
    await signupPage1.signupContainer.screenshot({path:`${SCREENSHOT_SIGNUP}/signupUsernameContainer.png`});
    await signupPage1.fillUsernameField("number18");
    await expect(signupPage1.signupUsernameField).toHaveValue("number18");
    await signupPage1.submitButton.click();
    await page.screenshot({path:`${SCREENSHOT_SIGNUP}/test1.png`})
    // Check that the password container is visible now
    await expect(page.locator("#password-input-signup")).toBeVisible();
    const signupPage2 = new SignupStage2(page);
    await signupPage2.signupContainer.screenshot({path:`${SCREENSHOT_SIGNUP}/signupPasswordContainer.png`});
    // Fill password and continue
    await signupPage2.fillPasswordField("number18");
    await signupPage2.submitButton.click();

    // check if redirection back to loginPage worked
    await expect(page).toHaveURL("/");
})