import { cn } from "./utils"

// Animation timing constants (synced with globals.css)
export const TRANSITION_TIMING = {
  fast: 100,    // ms - click feedback
  normal: 150,  // ms - hover transitions
  slow: 200,    // ms - modal animations
} as const

// Easing curves
export const EASING = {
  easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
  easeOut: "cubic-bezier(0, 0, 0.2, 1)",
  easeIn: "cubic-bezier(0.4, 0, 1, 1)",
} as const

/**
 * Generates standard interaction classes for buttons and interactive elements.
 * Includes hover, active, and focus states.
 */
export function interactionClasses(className?: string): string {
  return cn(
    // Base transition for all properties
    "transition-all duration-150 ease-in-out",
    // Hover state
    "hover:bg-accent hover:text-accent-foreground",
    // Active/click state - subtle scale down
    "active:scale-[0.98]",
    // Focus state - instant for accessibility
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
    // Custom classes
    className
  )
}
