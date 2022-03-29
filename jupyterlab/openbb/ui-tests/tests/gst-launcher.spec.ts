/*
 * Simple scenario placeholder for testing the Gamestonk Launcher
 *
 * Steps:
 * - Wait for the launcher panel to load
 * - Launch the terminal
 * - Wait for the terminal to initialize
 * - Press "return" three times
 *
 * This is a placeholder for the test.
 * Depending on the future testing/QA decisions this test can be expanded.
*/
import { test, expect } from '@playwright/test';

const TARGET_URL = process.env.TARGET_URL ?? 'http://localhost:8888';

test('Should open a panel with the GamestonkTerminal and send "Enter" three times', async ({ page }) => {
  await page.goto(`${TARGET_URL}/lab`);
  await page.waitForSelector('#jupyterlab-splash', { state: 'detached' });
  await page.waitForSelector('div[role="main"] >> text=Launcher');

  await Promise.all([
    page.waitForNavigation(/*{ url: 'http://localhost:8888/lab' }*/),
    page.click('p:has-text("OpenBB Terminal")')
  ]);

  expect(
      await page.waitForSelector('[aria-label="Terminal input"]', { timeout: 1000 })
      ).toBeTruthy();

  // Press Enter a couple of times
  await page.waitForTimeout(3000)
  await page.press('[aria-label="Terminal input"]', 'Enter');
  await page.press('[aria-label="Terminal input"]', 'Enter');
  await page.press('[aria-label="Terminal input"]', 'Enter');
  await page.waitForTimeout(1000)
});
