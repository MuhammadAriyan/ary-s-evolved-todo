import { test, expect } from '@playwright/test';

/**
 * Task Management E2E Tests
 *
 * Tests core task CRUD operations and real-time synchronization.
 */

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to tasks page
    await page.goto('/tasks');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should display tasks page', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/Tasks/i);

    // Check for main elements
    await expect(page.locator('h1')).toContainText(/tasks/i);
  });

  test('should create a new task', async ({ page }) => {
    // Click create task button
    await page.click('[data-testid="create-task-button"]');

    // Fill in task details
    await page.fill('[data-testid="task-title"]', 'E2E Test Task');
    await page.fill('[data-testid="task-description"]', 'This is a test task created by Playwright');

    // Submit form
    await page.click('[data-testid="submit-task"]');

    // Wait for task to appear in list
    await page.waitForSelector('text=E2E Test Task', { timeout: 5000 });

    // Verify task appears in list
    await expect(page.locator('text=E2E Test Task')).toBeVisible();
  });

  test('should edit a task', async ({ page }) => {
    // Create a task first
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Task to Edit');
    await page.click('[data-testid="submit-task"]');

    // Wait for task to appear
    await page.waitForSelector('text=Task to Edit');

    // Click edit button
    await page.click('[data-testid="edit-task-button"]');

    // Update task title
    await page.fill('[data-testid="task-title"]', 'Updated Task Title');
    await page.click('[data-testid="submit-task"]');

    // Verify updated title appears
    await expect(page.locator('text=Updated Task Title')).toBeVisible();
  });

  test('should complete a task', async ({ page }) => {
    // Create a task first
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Task to Complete');
    await page.click('[data-testid="submit-task"]');

    // Wait for task to appear
    await page.waitForSelector('text=Task to Complete');

    // Click checkbox to complete task
    await page.click('[data-testid="task-checkbox"]');

    // Verify task is marked as completed
    await expect(page.locator('[data-testid="task-status"]')).toContainText(/completed/i);
  });

  test('should delete a task', async ({ page }) => {
    // Create a task first
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Task to Delete');
    await page.click('[data-testid="submit-task"]');

    // Wait for task to appear
    await page.waitForSelector('text=Task to Delete');

    // Click delete button
    await page.click('[data-testid="delete-task-button"]');

    // Confirm deletion
    await page.click('[data-testid="confirm-delete"]');

    // Verify task is removed
    await expect(page.locator('text=Task to Delete')).not.toBeVisible();
  });

  test('should filter tasks by status', async ({ page }) => {
    // Create completed and pending tasks
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Completed Task');
    await page.click('[data-testid="submit-task"]');
    await page.click('[data-testid="task-checkbox"]');

    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Pending Task');
    await page.click('[data-testid="submit-task"]');

    // Filter by completed
    await page.click('[data-testid="filter-completed"]');

    // Verify only completed tasks shown
    await expect(page.locator('text=Completed Task')).toBeVisible();
    await expect(page.locator('text=Pending Task')).not.toBeVisible();

    // Filter by pending
    await page.click('[data-testid="filter-pending"]');

    // Verify only pending tasks shown
    await expect(page.locator('text=Pending Task')).toBeVisible();
    await expect(page.locator('text=Completed Task')).not.toBeVisible();
  });
});

test.describe('Real-Time Synchronization', () => {
  test('should sync tasks across multiple tabs', async ({ browser }) => {
    // Create two browser contexts (tabs)
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();

    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // Navigate both tabs to tasks page
    await page1.goto('/tasks');
    await page2.goto('/tasks');

    // Wait for pages to load
    await page1.waitForLoadState('networkidle');
    await page2.waitForLoadState('networkidle');

    // Create task in tab 1
    await page1.click('[data-testid="create-task-button"]');
    await page1.fill('[data-testid="task-title"]', 'Sync Test Task');
    await page1.click('[data-testid="submit-task"]');

    // Wait for task to appear in tab 1
    await page1.waitForSelector('text=Sync Test Task');

    // Verify task appears in tab 2 within 2 seconds (real-time sync requirement)
    await expect(page2.locator('text=Sync Test Task')).toBeVisible({ timeout: 2000 });

    // Clean up
    await context1.close();
    await context2.close();
  });
});

test.describe('Task Search', () => {
  test('should search tasks', async ({ page }) => {
    // Create multiple tasks
    const tasks = ['Meeting with client', 'Review code', 'Client presentation'];

    for (const task of tasks) {
      await page.click('[data-testid="create-task-button"]');
      await page.fill('[data-testid="task-title"]', task);
      await page.click('[data-testid="submit-task"]');
      await page.waitForSelector(`text=${task}`);
    }

    // Search for "client"
    await page.fill('[data-testid="search-input"]', 'client');
    await page.click('[data-testid="search-button"]');

    // Verify search results
    await expect(page.locator('text=Meeting with client')).toBeVisible();
    await expect(page.locator('text=Client presentation')).toBeVisible();
    await expect(page.locator('text=Review code')).not.toBeVisible();
  });

  test('should handle search with no results', async ({ page }) => {
    // Search for non-existent task
    await page.fill('[data-testid="search-input"]', 'nonexistent task xyz');
    await page.click('[data-testid="search-button"]');

    // Verify no results message
    await expect(page.locator('text=No tasks found')).toBeVisible();
  });
});

test.describe('Task Reminders', () => {
  test('should schedule a reminder', async ({ page }) => {
    // Create a task
    await page.click('[data-testid="create-task-button"]');
    await page.fill('[data-testid="task-title"]', 'Task with Reminder');
    await page.click('[data-testid="submit-task"]');

    // Open task details
    await page.click('text=Task with Reminder');

    // Add reminder
    await page.click('[data-testid="add-reminder-button"]');
    await page.fill('[data-testid="reminder-datetime"]', '2026-02-15T10:00');
    await page.click('[data-testid="save-reminder"]');

    // Verify reminder appears
    await expect(page.locator('[data-testid="reminder-list"]')).toContainText('Feb 15, 2026');
  });
});

test.describe('Accessibility', () => {
  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/tasks');

    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify focus is visible
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/tasks');

    // Check for ARIA labels
    await expect(page.locator('[aria-label="Create new task"]')).toBeVisible();
    await expect(page.locator('[role="main"]')).toBeVisible();
  });
});
