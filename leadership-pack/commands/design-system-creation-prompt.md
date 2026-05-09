# Prompt: Create a Comprehensive Design System & Style Guide

Create a complete design system similar to CutTheEdge with organized color management, typography hierarchy, and component consistency that enables quick platform-wide changes. Follow this structure:

## 1. Core Foundation Files

**Create these essential files:**

### `STYLE-GUIDE.md` - Single Source of Truth
Create a comprehensive style guide documenting:
- **3-color palette** with specific hex values and Tailwind utilities
- **Typography hierarchy** (3 tiers: Display/Condensed, Body/Sans, Technical/Mono)
- **Spacing system** based on 4px grid
- **Component patterns** with exact Tailwind classes
- **Animation standards** with keyframes
- **Mobile-specific rules** and responsive patterns

### `globals.css` - CSS Variables & Utilities
Structure the CSS with:
```css
@theme {
  /* Color variables */
  --color-primary: #F5F5F5;
  --color-secondary: #111111; 
  --color-accent: #00D46A;
  --color-muted: #7A7A7A;
  
  /* Font variables */
  --font-sans: [your-sans-font];
  --font-condensed: [your-display-font];
  --font-mono: [your-mono-font];
}

/* Typography utility classes */
.text-eyebrow { /* status labels */ }
.text-terminal { /* technical text */ }
.text-subtext { /* metadata */ }
/* etc. */
```

## 2. Strict Design Constraints

**Implement these rules for consistency:**

### Color Palette (3 colors maximum)
- **Primary:** Background/container color
- **Secondary:** Main text color  
- **Accent:** CTAs, highlights, interactive states
- Reference all colors via CSS variables only
- Never use arbitrary colors

### Typography System (3 font families)
- **Display/Headlines:** Condensed font for authority
- **Body/Content:** Sans-serif for readability  
- **Technical/Data:** Monospace for precision
- Create semantic utility classes for each use case

### Component Standards
- **No border radius** (`rounded-none` everywhere)
- **No box shadows** (use borders and accent glows only)
- **Consistent spacing** using 4px grid system
- **Sharp, geometric precision**

## 3. Organized Class Structure

**Create semantic utility classes like:**

```css
/* Status/Label text */
.text-eyebrow {
  font-family: var(--font-mono);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.1em;
  color: var(--color-accent);
}

/* Metadata/discrete text */
.text-subtext {
  font-size: 0.75rem;
  color: var(--color-muted);
  letter-spacing: 0.02em;
}

/* Clickable accent links */
.text-accent-bold {
  color: var(--color-accent);
  font-weight: 600;
}
```

## 4. Component Patterns

**Document reusable patterns:**

### Button Variants
```jsx
// Primary CTA
className="bg-accent text-secondary px-8 py-3 rounded-none hover:shadow-[0_0_15px_rgba(accent-color,0.6)]"

// Secondary CTA  
className="bg-transparent border-2 border-accent text-accent px-8 py-3 rounded-none hover:bg-accent hover:text-secondary"
```

### Card Patterns
```jsx
className="bg-primary border border-muted p-8 rounded-none"
```

## 5. Mobile-First Responsive Rules

**Establish mobile patterns:**
- CTAs must never stretch full-width on mobile
- Always center buttons: `<div className="flex justify-center">`
- Use `clamp()` for fluid typography
- Container padding: `px-6 sm:px-8 lg:px-12`
- Touch targets minimum 44px

## 6. Animation System

**Create signature transitions:**
- Define keyframes for page transitions
- Standard transition utilities: `transition-all duration-300 ease-in-out`
- Hover effects using accent color glows
- Respect `prefers-reduced-motion`

## 7. Quick Reference Table

**Include in your style guide:**

| Goal | Tailwind Classes |
|------|------------------|
| Page Section | `py-24 sm:py-32` |
| Main Container | `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` |
| Hero Headline | `font-condensed font-bold text-accent text-5xl md:text-7xl` |
| Body Text | `font-sans text-lg text-secondary leading-relaxed` |
| Technical Label | `font-mono font-bold uppercase text-accent` |

## 8. Integration Requirements

**Set up your build system:**
- Use Tailwind CSS v4+ with CSS theme variables
- Configure font loading in layout file
- Map CSS variables to component props
- Create TypeScript interfaces for design tokens

## 9. Documentation Standards

**Maintain your system:**
- Version your style guide
- Include copy-paste code examples
- Document mobile-specific patterns
- Create component usage examples
- Establish update workflow for changes

## 10. Enforcement Approach

**Ensure consistency:**
- Lint rules preventing arbitrary values
- Component library with pre-defined variants
- Design token validation
- Regular style guide reviews

The goal is a system where changing one CSS variable updates colors across the entire platform, and every component follows consistent patterns documented in your style guide.

---

This approach creates the organized, maintainable styling system you saw in CutTheEdge, where the entire visual identity is controlled through a small set of variables and documented patterns.