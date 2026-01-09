"use client"

import { createContext, useContext, useState, ReactNode } from "react"

interface SidebarContextType {
  isOpen: boolean
  toggleSidebar: () => void
  selectedTag: string | null
  setSelectedTag: (tag: string | null) => void
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined)

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(true)
  const [selectedTag, setSelectedTag] = useState<string | null>(null)

  const toggleSidebar = () => setIsOpen(!isOpen)

  return (
    <SidebarContext.Provider
      value={{ isOpen, toggleSidebar, selectedTag, setSelectedTag }}
    >
      {children}
    </SidebarContext.Provider>
  )
}

export function useSidebar() {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within SidebarProvider")
  }
  return context
}
