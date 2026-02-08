# WCAG Accessibility Compliance

## WCAG 2.1 Level AA Requirements

### Text Contrast Ratios

**Normal Text (< 18pt or < 14pt bold):**
- Minimum contrast ratio: 4.5:1

**Large Text (≥ 18pt or ≥ 14pt bold):**
- Minimum contrast ratio: 3:1

### Color System Implementation

Create WCAG AA compliant color variables:

```css
/* globals.css */
:root {
  /* Text Color System - WCAG AA Compliant */
  --text-primary: rgba(255, 255, 255, 1);        /* 21:1 on dark bg */
  --text-secondary: rgba(255, 255, 255, 0.85);   /* 17.85:1 */
  --text-tertiary: rgba(255, 255, 255, 0.70);    /* 14.7:1 */
  --text-muted: rgba(255, 255, 255, 0.60);       /* 12.6:1 */
  --text-disabled: rgba(255, 255, 255, 0.40);    /* 8.4:1 */
}
```

Configure Tailwind:

```typescript
// tailwind.config.ts
colors: {
  text: {
    primary: 'var(--text-primary)',
    secondary: 'var(--text-secondary)',
    tertiary: 'var(--text-tertiary)',
    muted: 'var(--text-muted)',
    disabled: 'var(--text-disabled)',
  }
}
```

### Systematic Color Replacement

Replace non-compliant colors:

```bash
# Find all instances
grep -r "text-white/50" frontend/

# Replace systematically
find . -type f \( -name "*.tsx" -o -name "*.ts" \) \
  -not -path "./node_modules/*" \
  -exec sed -i 's/text-white\/50/text-text-muted/g' {} \;

find . -type f \( -name "*.tsx" -o -name "*.ts" \) \
  -not -path "./node_modules/*" \
  -exec sed -i 's/text-white\/60/text-text-muted/g' {} \;

find . -type f \( -name "*.tsx" -o -name "*.ts" \) \
  -not -path "./node_modules/*" \
  -exec sed -i 's/text-white\/70/text-text-tertiary/g' {} \;

find . -type f \( -name "*.tsx" -o -name "*.ts" \) \
  -not -path "./node_modules/*" \
  -exec sed -i 's/text-white\/80/text-text-secondary/g' {} \;
```

## Keyboard Navigation

### Requirements

All interactive elements must be:
1. Reachable via Tab key
2. Activatable via Enter/Space
3. Visible when focused
4. In logical tab order

### Implementation

```typescript
// Ensure proper focus styles
<button
  className="focus:outline-none focus:ring-2 focus:ring-sky-cyan-400"
  onClick={handleClick}
>
  Click Me
</button>

// Skip links for screen readers
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0"
>
  Skip to main content
</a>
```

## Semantic HTML

Use proper HTML elements:

```typescript
// ✅ Good - Semantic HTML
<nav>
  <ul>
    <li><a href="/home">Home</a></li>
  </ul>
</nav>

<main id="main-content">
  <article>
    <h1>Page Title</h1>
    <p>Content</p>
  </article>
</main>

// ❌ Bad - Non-semantic
<div className="nav">
  <div className="link">Home</div>
</div>
```

## ARIA Labels

Add labels for screen readers:

```typescript
<button aria-label="Close dialog" onClick={onClose}>
  <X className="h-4 w-4" />
</button>

<input
  type="text"
  aria-label="Search tasks"
  placeholder="Search..."
/>
```

## Testing

### 1. axe DevTools

Install browser extension and run audit:
- Zero violations for WCAG AA
- Fix all critical and serious issues
- Document moderate issues

### 2. Lighthouse Accessibility

```bash
lighthouse https://yourapp.com --only-categories=accessibility
```

Target score: 100

### 3. Keyboard Navigation Test

Manual testing:
- Tab through all interactive elements
- Verify focus indicators visible
- Test Enter/Space activation
- Check Escape key for modals

### 4. Screen Reader Test

Test with:
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS/iOS)
- TalkBack (Android)

### 5. Contrast Checker

Use browser DevTools:
- Inspect element
- Check computed contrast ratio
- Verify meets 4.5:1 (normal) or 3:1 (large)

## Accessibility Checklist

- [ ] All text meets contrast requirements (4.5:1 or 3:1)
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible on all focusable elements
- [ ] Proper heading hierarchy (h1 → h2 → h3)
- [ ] All images have alt text
- [ ] Forms have proper labels
- [ ] ARIA labels for icon-only buttons
- [ ] Skip links for screen readers
- [ ] No keyboard traps
- [ ] Logical tab order
- [ ] Error messages associated with form fields
- [ ] Color not sole means of conveying information
- [ ] Sufficient touch target sizes (44x44px minimum)
- [ ] No auto-playing audio/video
- [ ] Captions for video content
- [ ] axe DevTools: Zero violations
- [ ] Lighthouse Accessibility: Score 100

## Common Issues

1. **Low Contrast Text** - Use color system variables
2. **Missing Alt Text** - Add descriptive alt to all images
3. **Keyboard Traps** - Ensure modals can be closed with Escape
4. **Poor Focus Indicators** - Add visible focus styles
5. **Non-Semantic HTML** - Use proper HTML elements
6. **Missing Labels** - Add aria-label to icon buttons

## Tools

- axe DevTools browser extension
- Lighthouse accessibility audit
- WAVE browser extension
- Color Contrast Analyzer
- Screen readers (NVDA, JAWS, VoiceOver)
- Keyboard navigation testing
