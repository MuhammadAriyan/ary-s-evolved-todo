---
name: modernize-ui
description: Modernize and refine UI components visually without changing functionality. Use when polishing existing UI, replacing custom elements with shadcn/ui, or improving visual hierarchy and spacing.
---

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

### 2. Component System (MANDATORY)
**Use shadcn/ui components exclusively:**
- `Card`, `CardHeader`, `CardContent`, `CardFooter`
- `Button` (use variants consistently)
- `Input`, `Textarea`, `Select`
- `Tabs`, `DropdownMenu`, `Dialog`, `Popover`, `Tooltip`

### 3. Layout & Spacing Rules
- Use grid-based layout (not ad-hoc flex stacking)
- Apply consistent spacing using Tailwind scale (`gap-4`, `p-6`, `space-y-6`)
- Sections should breathe — no cramped blocks

### 4. Typography System
- Page titles → `text-2xl` to `text-3xl`, `font-semibold`
- Section headers → `text-lg` to `text-xl`
- Body text → `text-sm` to `text-base`

## What NOT To Do (Non-Negotiable)
- ❌ Do not rename variables or props
- ❌ Do not refactor logic
- ❌ Do not add or remove features
- ❌ Do not change component behavior
- ❌ Do not introduce new libraries

**You are polishing the blade, not reforging it.**
