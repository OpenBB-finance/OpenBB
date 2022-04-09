/*
 * E2E scenario for testing the Settings menu UI
 *
 * Steps:
 * - Load the extension
 * - Set a feature flag and save
 * - Restore settings menu values from user settings
 * - Unset the feature flag
*/
import { test, expect } from '@playwright/test';

const TARGET_URL = process.env.TARGET_URL ?? 'http://localhost:8888';

test('Test loading of the settings menu', async ({ page }) => {
  // Open lab
  await page.goto(`${TARGET_URL}/lab`);
  await page.waitForSelector('#jupyterlab-splash', { state: 'detached' });
  await page.waitForSelector('div[role="main"] >> text=Launcher');

  // Click the Settings button in the Launcher panel
  await page.click('text=settingsSettings >> div');

  // Verify that the extension panel is visible on the same page
  expect(page.url()).toBe('http://localhost:8888/lab');
  expect(page.isVisible('#gamestonkSettings')).toBeTruthy();

  // Click the "Clear.after.command" feature flag's checkbox
  await page.check('#featureFlags > div.fieldSetData > input.Clear.after.command');
  // Click "Update Flags" text and catch the dialog message
  page.once('dialog', dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    dialog.dismiss().catch(() => {});
  });
  await page.click('text=Update Flags');

  // Check the "Clear.after.command" feature flag's checkbox is checked
  expect(await page.isChecked('#featureFlags > div.fieldSetData > input.Clear.after.command')).toBeTruthy();

  // Reload the page
  await page.goto(`${TARGET_URL}/lab`);
  await page.waitForSelector('#jupyterlab-splash', { state: 'detached' });
  await page.waitForSelector('div[role="main"] >> text=Launcher');

  // Click the settings button in the Launcher panel
  await page.click('text=settingsSettings >> div');

  expect(page.url()).toBe('http://localhost:8888/lab');

  // Check the "Clear.after.command" feature flag's checkbox is checked (populated from the user settings)
  expect(await page.isChecked('#featureFlags > div.fieldSetData > input.Clear.after.command')).toBeTruthy();

  // Uncheck the "Clear.after.command" feature flag's checkbox
  await page.uncheck('#featureFlags > div.fieldSetData > input.Clear.after.command');
  // Click "Update Flags" text and catch the dialog message
  page.once('dialog', dialog => {
    console.log(`Dialog message: ${dialog.message()}`);
    dialog.dismiss().catch(() => {});
  });
  await page.click('text=Update Flags');

  // Check the "Clear.after.command" feature flag's checkbox is not checked (user settings changed)
  expect(await page.isChecked('#featureFlags > div.fieldSetData > input.Clear.after.command')).toBeFalsy();

  // Reload the page
  await page.goto(`${TARGET_URL}/lab`);
  await page.waitForSelector('#jupyterlab-splash', { state: 'detached' });
  await page.waitForSelector('div[role="main"] >> text=Launcher');

  // Click the settings button in the Launcher panel
  await page.click('text=settingsSettings >> div');

  expect(page.url()).toBe('http://localhost:8888/lab');

  // Check the "Clear.after.command" feature flag's checkbox is not checked (populated from the user settings)
  expect(await page.isChecked('#featureFlags > div.fieldSetData > input.Clear.after.command')).toBeFalsy();

});
