# Phase 1: Design System Foundation - Research

**Researched:** 2026-03-09
**Domain:** Design System, Theme Switching, CSS Variables, Tailwind Configuration
**Confidence:** HIGH

## Summary

This phase establishes the foundational visual language for StructureClaw frontend. The research covers design tokens implementation using CSS variables with Tailwind CSS, Geist font configuration for modern typography, next-themes for robust dark/light/system theme switching, and glassmorphism effect patterns.

**Primary recommendation:** Use shadcn/ui's CSS variable convention with next-themes for theme management, Geist font via npm package, and Tailwind's `darkMode: 'class'` configuration. This combination provides flicker-free theme switching, excellent TypeScript support, and aligns with the Linear/Notion/Vercel design aesthetic.

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DSGN-01 | Establish design tokens (colors, fonts, spacing, border-radius, shadows) | shadcn/ui CSS variable convention with `--background`/`--foreground` pairs; Tailwind theme extend |
| DSGN-02 | Configure Geist font (Sans + Mono) | `npm install geist` package with `next/font` optimization |
| DSGN-03 | Tailwind custom configuration (extend theme) | `tailwind.config.js` with CSS variable references for theme-aware colors |
| DSGN-04 | cn() utility function (clsx + tailwind-merge) | Already implemented in `src/lib/utils.ts`; pattern verified |
| DSGN-05 | Dark/Light/System tri-state theme switching | `next-themes` package with `ThemeProvider` and `useTheme` hook |
| DSGN-06 | Custom theme accent color | CSS variable `--accent` with light/dark variants in `:root` and `.dark` |
| DSGN-07 | Glassmorphism effect component variants | Tailwind `backdrop-blur-*`, `bg-white/10`, `border-white/20` patterns |

</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next-themes | ^0.4.6 | Dark/Light/System theme switching | Flicker-free SSR, tab sync, 739k+ downloads/week |
| geist | ^1.3.0 | Modern font family (Sans + Mono) | Vercel's official font, optimized for Next.js |
| clsx | ^2.1.0 | Conditional class names | Already installed, lightweight |
| tailwind-merge | ^3.5.0 | Merge Tailwind classes without conflicts | Already installed, essential for component variants |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| class-variance-authority | ^0.7.1 | Type-safe component variants | Already installed, use for button/variant patterns |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| next-themes | Custom useState + localStorage | More code, flash issues, no SSR hydration safety |
| geist | Inter, Space Grotesk | Less modern, not Vercel-native aesthetic |
| CSS variables | Tailwind theme.colors | Harder to switch themes, no runtime updates |

**Installation:**
```bash
npm install next-themes geist
```

Note: `clsx`, `tailwind-merge`, and `class-variance-authority` are already installed.

## Architecture Patterns

### Recommended Project Structure
```
src/
├── app/
│   ├── globals.css          # Design tokens (CSS variables)
│   ├── layout.tsx           # ThemeProvider wrapper
│   └── providers.tsx        # Combined providers (existing)
├── components/
│   ├── theme-provider.tsx   # next-themes wrapper
│   ├── theme-toggle.tsx     # Dark/Light/System switcher
│   └── ui/
│       ├── button.tsx       # Existing (needs theme update)
│       └── card.tsx         # Existing (needs theme update)
└── lib/
    ├── utils.ts             # cn() function (existing)
    └── fonts.ts             # Geist font configuration
```

### Pattern 1: CSS Variables with Background/Foreground Convention

**What:** shadcn/ui convention pairs each semantic color with a foreground variant for automatic text contrast.

**When to use:** All theme-aware colors should follow this pattern.

**Example:**
```css
/* Source: https://ui.shadcn.com/docs/theming */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --radius: 0.625rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --accent: oklch(0.371 0 0);
  --accent-foreground: oklch(0.985 0 0);
}
```

### Pattern 2: ThemeProvider Setup

**What:** Wrap the app with next-themes provider for automatic theme management.

**When to use:** Root layout for any app with theme switching.

**Example:**
```tsx
// Source: https://ui.shadcn.com/docs/dark-mode/next
// components/theme-provider.tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}

// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

### Pattern 3: Geist Font Configuration

**What:** Use the `geist` npm package with Next.js font optimization.

**When to use:** All projects wanting modern Vercel-style typography.

**Example:**
```tsx
// Source: https://github.com/vercel/geist-font
// lib/fonts.ts
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'

// app/layout.tsx
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className={`${GeistSans.variable} ${GeistMono.variable}`} suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}

// globals.css
:root {
  --font-sans: var(--font-geist-sans), ui-sans-serif, system-ui, sans-serif;
  --font-mono: var(--font-geist-mono), ui-monospace, monospace;
}
```

### Pattern 4: Tailwind Configuration with CSS Variables

**What:** Reference CSS variables in Tailwind config for theme-aware utilities.

**When to use:** All Tailwind projects with theme switching.

**Example:**
```js
// tailwind.config.js
// Source: https://tailwindcss.com/docs/theme
module.exports = {
  darkMode: 'class', // Required for next-themes
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... other colors
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
    },
  },
  plugins: [],
}
```

### Pattern 5: Glassmorphism Effect

**What:** Use Tailwind's backdrop-blur with semi-transparent backgrounds.

**When to use:** Cards, modals, overlays wanting depth and modern aesthetic.

**Example:**
```tsx
// Source: https://tailwindcss.com/docs/backdrop-filter-blur
// Glassmorphism card component
<div className="
  backdrop-blur-lg
  bg-white/10
  dark:bg-black/10
  border
  border-white/20
  dark:border-white/10
  rounded-xl
  shadow-lg
">
  {children}
</div>

// Variant with custom blur amount
<div className="backdrop-blur-md bg-background/80 border-border/50">
  {children}
</div>
```

### Anti-Patterns to Avoid

- **Using `darkMode: 'media'` with next-themes:** Causes conflicts; use `darkMode: 'class'` instead
- **Forgetting `suppressHydrationWarning` on `<html>`:** Causes hydration mismatch errors
- **Rendering theme-dependent UI before mount:** Use `mounted` state or `next/dynamic` with `ssr: false`
- **Hardcoding colors in components:** Always use CSS variables via Tailwind utilities
- **Using `oklch()` without fallbacks:** Older browsers may not support; consider `hsl()` as fallback

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Theme switching | Custom localStorage + useState | next-themes | Handles SSR hydration, flash prevention, tab sync |
| Class merging | Manual string concatenation | clsx + tailwind-merge | Handles conditional classes, Tailwind conflicts |
| Font loading | @font-face CSS | next/font + geist package | Automatic optimization, self-hosting, no layout shift |
| Theme toggle UI | Custom select/radio | shadcn/ui dropdown-menu | Accessible, keyboard navigation, consistent styling |

**Key insight:** Theme switching seems simple but has many edge cases (SSR hydration, flash prevention, system preference sync). next-themes handles all these out of the box.

## Common Pitfalls

### Pitfall 1: Hydration Mismatch on Theme Toggle
**What goes wrong:** `theme` is `undefined` on server, causing mismatch with client-rendered value
**Why it happens:** localStorage is not available during SSR
**How to avoid:** Use `mounted` state or render placeholder until client-side
**Warning signs:** "Text content does not match server-rendered HTML" console error

```tsx
// Correct pattern
const [mounted, setMounted] = useState(false)
const { theme } = useTheme()

useEffect(() => setMounted(true), [])

if (!mounted) return <Skeleton className="h-9 w-9" />
return <ThemeToggle />
```

### Pitfall 2: Flash of Unstyled Content (FOUC)
**What goes wrong:** Page briefly shows wrong theme before JavaScript loads
**Why it happens:** Theme is applied after hydration
**How to avoid:** next-themes injects blocking script automatically; ensure `suppressHydrationWarning` is set
**Warning signs:** White flash on dark mode pages during load

### Pitfall 3: Tailwind Dark Mode Configuration Mismatch
**What goes wrong:** Dark mode classes don't work with next-themes
**Why it happens:** Tailwind `darkMode` not set to `'class'`
**How to avoid:** Set `darkMode: 'class'` in `tailwind.config.js` and `attribute="class"` in ThemeProvider
**Warning signs:** `dark:text-white` has no effect

### Pitfall 4: Missing CSS Variable in Tailwind Config
**What goes wrong:** Tailwind class references undefined variable
**Why it happens:** CSS variable not mapped in `theme.extend.colors`
**How to avoid:** Every `--color-name` CSS variable needs `name: 'hsl(var(--name))'` in config
**Warning signs:** Colors appear transparent or wrong

## Code Examples

Verified patterns from official sources:

### Theme Toggle Component
```tsx
// Source: https://ui.shadcn.com/docs/dark-mode/next
"use client"

import * as React from "react"
import { Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => setMounted(true), [])

  if (!mounted) {
    return <Button variant="ghost" size="icon" disabled><Sun className="h-5 w-5" /></Button>
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          <Sun className="mr-2 h-4 w-4" />
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          <Moon className="mr-2 h-4 w-4" />
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          <Monitor className="mr-2 h-4 w-4" />
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Custom Accent Color Configuration
```css
/* globals.css */
:root {
  /* Custom accent - orange theme for StructureClaw */
  --accent: oklch(0.75 0.183 50);
  --accent-foreground: oklch(0.98 0.01 50);
}

.dark {
  --accent: oklch(0.70 0.183 50);
  --accent-foreground: oklch(0.15 0.02 50);
}
```

### Glassmorphism Card Variant
```tsx
// components/ui/glass-card.tsx
import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

const glassCardVariants = cva(
  "rounded-xl border transition-all",
  {
    variants: {
      variant: {
        default: "backdrop-blur-lg bg-background/80 border-border/50",
        subtle: "backdrop-blur-md bg-background/60 border-border/30",
        strong: "backdrop-blur-xl bg-background/90 border-border/70",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof glassCardVariants> {}

export function GlassCard({ className, variant, ...props }: GlassCardProps) {
  return (
    <div className={cn(glassCardVariants({ variant }), className)} {...props} />
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tailwind `darkMode: 'media'` | `darkMode: 'class'` with next-themes | 2022+ | User preference persistence, SSR-safe |
| @font-face CSS | next/font with npm packages | Next.js 13+ | Zero layout shift, automatic optimization |
| JavaScript theme config | CSS variables | 2023+ | Runtime theme updates, simpler architecture |
| HSL color format | oklch for new projects | 2024+ | Better perceptual uniformity |

**Deprecated/outdated:**
- `next/font/google` for Geist: Use `geist` npm package instead (Vercel's recommendation)
- Manual `prefers-color-scheme` listeners: Use next-themes `enableSystem` option

## Open Questions

1. **Should we use oklch or hsl for color variables?**
   - What we know: oklch has better perceptual uniformity, hsl has wider browser support
   - What's unclear: Safari support for oklch (available since Safari 15.4)
   - Recommendation: Use hsl as primary with oklch fallback, or hsl only for broader compatibility

2. **What radius value for the design aesthetic?**
   - What we know: Linear uses subtle radius (~8px), Vercel uses minimal (~4px)
   - What's unclear: User preference for StructureClaw
   - Recommendation: Start with `--radius: 0.5rem` (8px), adjust based on visual review

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Vitest (recommended for Next.js 14) |
| Config file | `vitest.config.ts` (Wave 0 creation) |
| Quick run command | `npm run test -- --run` |
| Full suite command | `npm run test` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| DSGN-01 | Design tokens defined | unit | `vitest run tests/design-tokens.test.ts` | Wave 0 |
| DSGN-02 | Geist font loaded | unit | `vitest run tests/fonts.test.ts` | Wave 0 |
| DSGN-03 | Tailwind config valid | unit | `vitest run tests/tailwind-config.test.ts` | Wave 0 |
| DSGN-04 | cn() merges classes correctly | unit | `vitest run tests/cn-utility.test.ts` | Wave 0 |
| DSGN-05 | Theme switching works | integration | `vitest run tests/theme-switch.test.tsx` | Wave 0 |
| DSGN-06 | Accent color applies | unit | `vitest run tests/accent-color.test.ts` | Wave 0 |
| DSGN-07 | Glassmorphism classes apply | unit | `vitest run tests/glassmorphism.test.ts` | Wave 0 |

### Sampling Rate
- **Per task commit:** `npm run test -- --run tests/<relevant-file>.test.ts`
- **Per wave merge:** `npm run test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `vitest.config.ts` - Vitest configuration for Next.js 14
- [ ] `tests/setup.ts` - Test setup with @testing-library/react
- [ ] `tests/design-tokens.test.ts` - CSS variable validation
- [ ] `tests/cn-utility.test.ts` - cn() function tests
- [ ] `tests/theme-switch.test.tsx` - Theme switching integration tests
- [ ] Framework install: `npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom jsdom`

## Sources

### Primary (HIGH confidence)
- [next-themes GitHub](https://github.com/pacocoursey/next-themes) - Official documentation, API reference, SSR patterns
- [shadcn/ui Dark Mode](https://ui.shadcn.com/docs/dark-mode/next) - Next.js integration guide
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming) - CSS variable convention, color system
- [Tailwind CSS Theme](https://tailwindcss.com/docs/theme) - Theme configuration, design tokens
- [Tailwind CSS Colors](https://tailwindcss.com/docs/customizing-colors) - Custom color configuration

### Secondary (MEDIUM confidence)
- [Geist Font Installation](https://peerlist.io/blog/engineering/how-to-use-vercel-geist-font-in-nextjs) - Setup guide verified against npm package
- [Tailwind Backdrop Blur](https://tailwindcss.com/docs/backdrop-filter-blur) - Official docs for glassmorphism
- [Glassmorphism with Tailwind](https://flyonui.com/blog/glassmorphism-with-tailwind-css/) - Implementation patterns

### Tertiary (LOW confidence)
- [Vitest Next.js Setup](https://medium.com/@jplaniran01/setting-up-next-js-14-with-vitest-and-typescript-71b4b67f7ce1) - Needs verification with actual Vitest setup

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - next-themes, geist, clsx, tailwind-merge are well-documented with official sources
- Architecture: HIGH - shadcn/ui patterns are industry standard, well-documented
- Pitfalls: HIGH - Common issues documented in next-themes README and shadcn docs

**Research date:** 2026-03-09
**Valid until:** 30 days - Stable patterns, no major version changes expected
