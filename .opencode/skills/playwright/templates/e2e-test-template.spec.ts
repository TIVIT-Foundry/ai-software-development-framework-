import { test, expect } from '@playwright/test';
import { {Feature}Page } from '../pages/{Feature}Page';

test.describe('{Feature} @regression', () => {
  test.beforeEach(async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.navigate();
  });

  test('should display the {feature} list page @smoke', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await expect({Feature}Page.pageTitle).toBeVisible();
    await expect({Feature}Page.createButton).toBeVisible();
  });

  test('should create a new {entity} @smoke', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.create({ name: 'Test {Entity}', code: 'TEST001' });

    await expect(page.getByText('Created successfully')).toBeVisible();
    await expect(page.getByText('Test {Entity}')).toBeVisible();
  });

  test('should show validation errors on empty form', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.createButton.click();
    await {Feature}Page.submitButton.click();

    await expect(page.getByText('Name is required')).toBeVisible();
  });

  test('should edit an existing {entity} @critical', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.editFirstRow({ name: 'Updated {Entity}' });

    await expect(page.getByText('Updated successfully')).toBeVisible();
  });

  test('should delete an {entity} @regression', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    const initialCount = await {Feature}Page.getRowCount();

    await {Feature}Page.deleteFirstRow();

    await expect(page.getByText('Deleted successfully')).toBeVisible();
    const newCount = await {Feature}Page.getRowCount();
    expect(newCount).toBe(initialCount - 1);
  });

  test('should paginate through records @regression', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.goToPage(2);

    const paginationText = await {Feature}Page.getPaginationText();
    expect(paginationText).toContain('Page 2');
  });

  test('should search {entities} by name @regression', async ({ page }) => {
    const {Feature}Page = new {Feature}Page(page);
    await {Feature}Page.search('Test');

    const rows = await {Feature}Page.getRowCount();
    expect(rows).toBeGreaterThanOrEqual(1);
  });
});
