/**
 * Icon Mapping Constants
 *
 * Nature-aligned Lucide icon mappings for Sky-Aura Glass aesthetic.
 * Uses growth metaphor system: Seed → Sprout → Leaf → Flower → Mountain
 */

import {
  Leaf,
  Mountain,
  Sprout,
  Flower,
  Sun,
  Cloud,
  Droplet,
  Wind,
  Waves,
  TreePine,
  Sparkles,
  CircleDot,
  Circle,
  CheckCircle2,
  Plus,
  X,
  Edit,
  Trash2,
  Calendar,
  Tag,
  Filter,
  Search,
  User,
  LogOut,
  Settings,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  type LucideIcon,
} from 'lucide-react';

/**
 * Nature Metaphor Icons
 * Represents growth cycle and natural elements
 */
export const NATURE_ICONS = {
  // Growth Cycle
  seed: CircleDot,
  sprout: Sprout,
  leaf: Leaf,
  flower: Flower,
  mountain: Mountain,

  // Natural Elements
  sun: Sun,
  cloud: Cloud,
  water: Droplet,
  wind: Wind,
  waves: Waves,
  tree: TreePine,
  sparkle: Sparkles,
} as const;

/**
 * Task Status Icons
 * Maps task states to nature metaphors
 */
export const TASK_STATUS_ICONS = {
  incomplete: Circle,           // Empty circle - potential
  new: Sprout,                  // New growth - just created
  inProgress: Leaf,             // Growing - in progress
  complete: Mountain,           // Peak achieved - completed
  checked: CheckCircle2,        // Verified completion
} as const;

/**
 * Action Icons
 * Common UI actions with nature-inspired alternatives where possible
 */
export const ACTION_ICONS = {
  add: Plus,
  remove: X,
  edit: Edit,
  delete: Trash2,
  calendar: Calendar,
  tag: Tag,
  filter: Filter,
  search: Search,
  user: User,
  logout: LogOut,
  settings: Settings,
  externalLink: ExternalLink,
} as const;

/**
 * Navigation Icons
 */
export const NAVIGATION_ICONS = {
  down: ChevronDown,
  up: ChevronUp,
  left: ChevronLeft,
  right: ChevronRight,
} as const;

/**
 * Complete icon map combining all categories
 */
export const ICON_MAP = {
  ...NATURE_ICONS,
  ...TASK_STATUS_ICONS,
  ...ACTION_ICONS,
  ...NAVIGATION_ICONS,
} as const;

/**
 * Icon sizes following Sky-Aura Glass design system
 */
export const ICON_SIZES = {
  xs: 14,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

/**
 * Icon stroke widths for mature aesthetic
 */
export const ICON_STROKE_WIDTHS = {
  thin: 1.5,
  normal: 2,
  medium: 2.5,
} as const;

/**
 * Helper function to get icon by name
 */
export function getIcon(name: keyof typeof ICON_MAP): LucideIcon {
  return ICON_MAP[name];
}

/**
 * Helper function to get task status icon
 */
export function getTaskStatusIcon(status: 'incomplete' | 'new' | 'inProgress' | 'complete' | 'checked'): LucideIcon {
  return TASK_STATUS_ICONS[status];
}

/**
 * Helper function to get nature icon
 */
export function getNatureIcon(element: keyof typeof NATURE_ICONS): LucideIcon {
  return NATURE_ICONS[element];
}

/**
 * Default icon props for consistent styling
 */
export const DEFAULT_ICON_PROPS = {
  size: ICON_SIZES.md,
  strokeWidth: ICON_STROKE_WIDTHS.thin,
  className: 'text-sky-cyan-700',
} as const;
