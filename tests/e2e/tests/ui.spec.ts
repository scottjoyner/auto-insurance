import { test, expect } from '@playwright/test';

test('homepage shows title', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.locator('h1')).toHaveText('Auto Insurance — Demo UI');
});
