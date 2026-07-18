import { Page, Locator } from '@playwright/test';

export class {Feature}Page {
  readonly page: Page;

  // Header elements
  readonly pageTitle: Locator;
  readonly createButton: Locator;

  // List elements
  readonly tableRows: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;

  // Create/Edit modal elements
  readonly nameInput: Locator;
  readonly codeInput: Locator;
  readonly statusSelect: Locator;
  readonly submitButton: Locator;
  readonly cancelButton: Locator;

  // Pagination
  readonly paginationInfo: Locator;

  constructor(page: Page) {
    this.page = page;

    // Header
    this.pageTitle = page.getByTestId('page-title');
    this.createButton = page.getByTestId('btn-create');

    // List
    this.tableRows = page.getByTestId('data-table').locator('tbody tr');
    this.searchInput = page.getByTestId('input-search');
    this.searchButton = page.getByTestId('btn-search');

    // Modal
    this.nameInput = page.getByTestId('input-name');
    this.codeInput = page.getByTestId('input-code');
    this.statusSelect = page.getByTestId('select-status');
    this.submitButton = page.getByTestId('btn-submit');
    this.cancelButton = page.getByTestId('btn-cancel');

    // Pagination
    this.paginationInfo = page.getByTestId('pagination-info');
  }

  async navigate() {
    await this.page.goto('/{entities}');
  }

  async create(data: { name: string; code: string; status?: string }) {
    await this.createButton.click();
    await this.nameInput.fill(data.name);
    await this.codeInput.fill(data.code);
    if (data.status) {
      await this.statusSelect.click();
      await this.page.getByRole('option', { name: data.status }).click();
    }
    await this.submitButton.click();
  }

  async editFirstRow(update: { name?: string; code?: string }) {
    const editButton = this.tableRows.first().getByTestId('btn-edit');
    await editButton.click();
    if (update.name) {
      await this.nameInput.clear();
      await this.nameInput.fill(update.name);
    }
    if (update.code) {
      await this.codeInput.clear();
      await this.codeInput.fill(update.code);
    }
    await this.submitButton.click();
  }

  async deleteFirstRow() {
    const deleteButton = this.tableRows.first().getByTestId('btn-delete');
    await deleteButton.click();
    await this.page.getByTestId('btn-confirm-delete').click();
  }

  async getRowCount(): Promise<number> {
    return this.tableRows.count();
  }

  async goToPage(pageNumber: number) {
    await this.page.getByRole('listitem').filter({ hasText: String(pageNumber) }).click();
  }

  async getPaginationText(): Promise<string> {
    return this.paginationInfo.textContent() ?? '';
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
  }
}
