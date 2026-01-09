"use client"

import React, {
  useEffect,
  useMemo,
  useRef,
  useState,
  type RefObject,
} from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { Search } from "lucide-react"

export interface EffectRendererProps {
  text: string
  isActive: boolean
  allowDelete?: boolean
  typeDurationMs: number
  deleteDurationMs: number
  pauseAfterTypeMs: number
  prefersReducedMotion?: boolean
  onDeleteComplete?: () => void
  containerRef?: RefObject<HTMLElement | null>
}

export type BuiltinEffect = "typewriter" | "slide" | "fade" | "none"

export interface SuggestiveSearchProps {
  onChange?: (val: string) => void
  onSearch?: (val: string) => void
  suggestions?: string[]
  className?: string
  Leading?: () => React.ReactElement
  showLeading?: boolean
  effect?: BuiltinEffect
  typeDurationMs?: number
  deleteDurationMs?: number
  pauseAfterTypeMs?: number
  animateMode?: "infinite" | "once"
}

const TypewriterEffect: React.FC<EffectRendererProps> = ({
  text,
  isActive,
  allowDelete = true,
  typeDurationMs,
  deleteDurationMs,
  pauseAfterTypeMs,
  prefersReducedMotion,
  onDeleteComplete,
}) => {
  const [phase, setPhase] = useState<"typing" | "paused" | "deleting">("typing")
  const timers = useRef<number[]>([])

  useEffect(() => {
    setPhase("typing")
    timers.current.forEach(clearTimeout)
    timers.current = []
    return () => {
      timers.current.forEach(clearTimeout)
      timers.current = []
    }
  }, [text, isActive, allowDelete])

  useEffect(() => {
    if (!isActive) {
      setPhase("typing")
      timers.current.forEach(clearTimeout)
      timers.current = []
    }
  }, [isActive])

  useEffect(() => {
    if (!isActive) return
    if (prefersReducedMotion) {
      if (!allowDelete) return
      const t = window.setTimeout(
        () => onDeleteComplete?.(),
        Math.max(200, pauseAfterTypeMs)
      )
      timers.current.push(t)
      return () => timers.current.forEach(clearTimeout)
    }
  }, [isActive, prefersReducedMotion, allowDelete, pauseAfterTypeMs, onDeleteComplete])

  if (!isActive) return null

  return (
    <div
      style={{
        display: "inline-block",
        overflow: "hidden",
        whiteSpace: "nowrap",
        alignItems: "center",
      }}
    >
      {prefersReducedMotion ? (
        <span className="text-sm text-white/40 select-none">{text}</span>
      ) : (
        <motion.div
          key={text}
          initial={{ width: "0%" }}
          animate={
            phase === "typing"
              ? { width: "100%" }
              : phase === "deleting"
              ? { width: "0%" }
              : { width: "100%" }
          }
          transition={
            phase === "typing"
              ? { duration: typeDurationMs / 1000, ease: "linear" }
              : phase === "deleting"
              ? { duration: deleteDurationMs / 1000, ease: "linear" }
              : {}
          }
          onAnimationComplete={() => {
            if (phase === "typing") {
              setPhase("paused")
              if (allowDelete) {
                const t = window.setTimeout(
                  () => setPhase("deleting"),
                  pauseAfterTypeMs
                )
                timers.current.push(t)
              }
            } else if (phase === "deleting") {
              onDeleteComplete?.()
            }
          }}
          style={{
            display: "inline-flex",
            alignItems: "center",
            overflow: "hidden",
            whiteSpace: "nowrap",
          }}
        >
          <span className="text-sm text-white/40 select-none">{text}</span>
          <motion.span
            aria-hidden
            style={{
              display: "inline-block",
              width: 1,
              marginLeft: 4,
              height: "1.1em",
              verticalAlign: "middle",
            }}
            className="bg-sky-cyan-500"
            animate={
              phase === "typing" || phase === "paused"
                ? { opacity: [0, 1, 0] }
                : { opacity: 0 }
            }
            transition={
              phase === "typing" || phase === "paused"
                ? { repeat: Infinity, duration: 0.9, ease: "linear" }
                : { duration: 0.1 }
            }
          />
        </motion.div>
      )}
    </div>
  )
}

export const SuggestiveSearch: React.FC<SuggestiveSearchProps> = ({
  onChange,
  onSearch,
  suggestions = ["Search tasks...", "Find by tag...", "Filter by date..."],
  className,
  Leading = () => <Search className="size-4 text-white/40" />,
  showLeading = true,
  effect = "typewriter",
  typeDurationMs = 500,
  deleteDurationMs = 300,
  pauseAfterTypeMs = 1500,
  animateMode = "infinite",
}) => {
  const [search, setSearch] = useState<string>("")
  const [isFocused, setIsFocused] = useState(false)
  const [index, setIndex] = useState<number>(0)
  const current = useMemo(() => suggestions[index] ?? "", [suggestions, index])

  const wrapperRef = useRef<HTMLDivElement | null>(null)
  const leadingRef = useRef<HTMLDivElement | null>(null)
  const overlayRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const [leftOffsetPx, setLeftOffsetPx] = useState<number | null>(null)

  useEffect(() => {
    const wrapper = wrapperRef.current
    const lead = leadingRef.current
    if (!wrapper) return

    const update = () => {
      const cs = getComputedStyle(wrapper)
      const padLeft = parseFloat(cs.paddingLeft || "0")
      const leadW = showLeading ? lead?.getBoundingClientRect().width ?? 0 : 0
      const left = padLeft + leadW + 8
      setLeftOffsetPx(left)
    }

    update()
    const ro = new ResizeObserver(update)
    ro.observe(wrapper)
    if (lead) ro.observe(lead)
    return () => ro.disconnect()
  }, [showLeading])

  const prefersReduced =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches

  function handleEffectDeleteComplete() {
    setIndex((i) => (i + 1) % suggestions.length)
  }

  const handleInputChange = (val: string) => {
    setSearch(val)
    onChange?.(val)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && search.trim()) {
      onSearch?.(search.trim())
    }
  }

  const overlayActive = !search && !isFocused
  const isLast = index === suggestions.length - 1
  const allowDelete = animateMode === "infinite" ? true : !isLast

  return (
    <div
      ref={wrapperRef}
      className={cn(
        "relative flex items-center gap-x-2 py-2.5 px-4 border border-white/20 rounded-full bg-black/30 backdrop-blur-xl transition-all focus-within:border-sky-cyan-500/50 focus-within:shadow-[0_0_20px_rgba(153,41,234,0.2)]",
        className
      )}
      style={{ maxWidth: "100%" }}
    >
      <div ref={leadingRef} className="flex-shrink-0">
        {showLeading && <Leading />}
      </div>

      <input
        ref={inputRef}
        type="text"
        value={search}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onChange={(e) => handleInputChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="bg-transparent outline-none text-sm text-white placeholder:text-transparent w-full min-w-[200px]"
        placeholder=""
        aria-label="search"
      />

      {overlayActive && (
        <div
          ref={overlayRef}
          aria-hidden
          style={{
            position: "absolute",
            left: leftOffsetPx != null ? `${leftOffsetPx}px` : "calc(0.5rem + 1.5rem + 8px)",
            right: "1rem",
            top: 0,
            bottom: 0,
            display: "flex",
            alignItems: "center",
            pointerEvents: "none",
            overflow: "hidden",
            whiteSpace: "nowrap",
          }}
        >
          <TypewriterEffect
            text={current}
            isActive={overlayActive}
            allowDelete={allowDelete}
            typeDurationMs={typeDurationMs}
            deleteDurationMs={deleteDurationMs}
            pauseAfterTypeMs={pauseAfterTypeMs}
            prefersReducedMotion={prefersReduced}
            onDeleteComplete={handleEffectDeleteComplete}
          />
        </div>
      )}
    </div>
  )
}

export default SuggestiveSearch
