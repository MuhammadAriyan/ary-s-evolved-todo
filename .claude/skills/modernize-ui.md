# Skill: modernize-ui

Modernize and refine the user interface only. Visual polish, not functional changes.

## Critical Rule

❌ **Do NOT modify:** business logic, data flow, API calls, state management, routing, or functionality.
✅ **Only modify:** visual structure, layout, spacing, typography, components, and interaction polish.

**Any change that alters how the app behaves is a failure.**

## When to use

Use this skill when you need to:
- Polish existing UI components without changing behavior
- Replace custom UI elements with shadcn/ui equivalents
- Improve visual hierarchy, spacing, and typography
- Add subtle interaction states (hover, focus, active)
- Clean up layout inconsistencies

## Core UI Objectives

### 1. Modern, Calm, Premium Look

- Clean, minimal, confident — no flashy gradients or childish effects
- Visual tone: focus, intelligence, reliability
- Think "high-end SaaS" rather than "landing page hype"

### 2. Clarity Over Decoration

- Every visual element must justify its presence
- Reduce noise, improve hierarchy, remove clutter
- If something doesn't improve comprehension or flow, remove it

### 3. Component System (MANDATORY)

**Use shadcn/ui components exclusively:**
- No custom UI libraries, no replacements, no exceptions
- Extend shadcn components only via Tailwind classes
- Do not create new component abstractions

**Required shadcn/ui components (where applicable):**
- `Card`, `CardHeader`, `CardContent`, `CardFooter`
- `Button` (use variants consistently)
- `Input`, `Textarea`, `Select`
- `Tabs`, `DropdownMenu`
- `Dialog`, `Popover`, `Tooltip`
- `Separator`, `Badge`
- `Checkbox`, `RadioGroup`
- `ScrollArea`

**Rule:** If a UI element exists that matches a shadcn component → replace it visually with shadcn, keeping props and logic intact.

### 4. Layout & Spacing Rules

- Use grid-based layout (not ad-hoc flex stacking)
- Apply consistent spacing using Tailwind scale (`gap-4`, `p-6`, `space-y-6`)
- Sections should breathe — no cramped blocks
- Align content vertically and horizontally with intention

### 5. Typography System

**Clear hierarchy:**
- Page titles → `text-2xl` to `text-3xl`, `font-semibold`
- Section headers → `text-lg` to `text-xl`
- Body text → `text-sm` to `text-base`

**Rules:**
- Avoid excessive font weights or sizes
- Line height optimized for readability
- No random text sizing — consistency is mandatory

### 6. Color & Theme Discipline

- Respect the existing theme (light/dark)
- No new color palettes unless absolutely required
- Use muted tones for secondary information
- Primary actions must stand out clearly, not aggressively
- Borders and separators should be subtle, not loud

### 7. Interaction & Micro-Polish

- Add subtle hover, focus, and active states using Tailwind
- Use `transition`, `duration-200`, `ease-out` where appropriate
- No animation for the sake of animation
- Feedback should feel calm and deliberate

### 8. Accessibility & UX Hygiene

- Maintain proper contrast ratios
- Click targets must be comfortable (min 44px touch targets)
- Inputs clearly labeled and grouped
- Empty states should look intentional, not broken

## What NOT To Do (Non-Negotiable)

- ❌ Do not rename variables or props
- ❌ Do not refactor logic
- ❌ Do not add or remove features
- ❌ Do not change component behavior
- ❌ Do not introduce new libraries
- ❌ Do not modify API calls or data fetching
- ❌ Do not change state management
- ❌ Do not alter routing or navigation logic
- ❌ Do not modify form submission handlers
- ❌ Do not change validation logic

**You are polishing the blade, not reforging it.**

## Modernization Checklist

### Before Starting
- [ ] Identify all files to be modified
- [ ] Verify shadcn/ui components are installed
- [ ] Review existing theme configuration
- [ ] Note all existing functionality to preserve

### During Modernization
- [ ] Replace custom elements with shadcn/ui equivalents
- [ ] Apply consistent spacing scale
- [ ] Establish clear typography hierarchy
- [ ] Add appropriate hover/focus states
- [ ] Ensure color usage follows theme
- [ ] Verify layout uses grid/flex intentionally

### After Completion
- [ ] All original functionality works identically
- [ ] No console errors introduced
- [ ] Visual hierarchy is clear
- [ ] Spacing is consistent throughout
- [ ] Theme (light/dark) works correctly
- [ ] Accessibility maintained or improved

## Example Transformations

### Button Replacement
```tsx
// Before (custom)
<button className="bg-blue-500 text-white px-4 py-2 rounded">
  Save
</button>

// After (shadcn/ui)
<Button variant="default">
  Save
</Button>
```

### Card Structure
```tsx
// Before (custom div soup)
<div className="border rounded p-4">
  <h3>Title</h3>
  <p>Content</p>
</div>

// After (shadcn/ui)
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Content</p>
  </CardContent>
</Card>
```

### Spacing Consistency
```tsx
// Before (inconsistent)
<div className="p-3 mt-2 mb-5 gap-2">

// After (consistent scale)
<div className="p-4 my-4 gap-4">
```

### Interaction States
```tsx
// Before (no states)
<div className="bg-white border">

// After (with states)
<div className="bg-white border transition-colors duration-200 hover:bg-muted/50 focus-within:ring-2 focus-within:ring-ring">
```

## Final Expectation

Deliver a UI that:
- Feels modern and professional
- Improves readability and flow
- Uses shadcn/ui correctly and consistently
- Leaves all functionality exactly as it was
