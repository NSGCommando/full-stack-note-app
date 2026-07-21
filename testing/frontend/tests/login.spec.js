// @ts-check
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login';
const SCREENSHOT_LOGIN = "screenshots/login-test"

test('Login Page', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  // wait for login container to be visible
  await loginPage.waitForLoad();
  // Test whether login and signup containers are visible
  await expect(loginPage.loginContainer).toBeVisible();
  await loginPage.loginContainer.screenshot({path:`${SCREENSHOT_LOGIN}/loginContainer.png`});
  await expect(loginPage.signupContainer).toBeVisible();
  await loginPage.signupContainer.screenshot({path:`${SCREENSHOT_LOGIN}/signupContainer.png`});
});

test('Navigate to Signup', async({page})=>{
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.signupStartButton.click();
  await expect(page).toHaveURL("/signup");
})
