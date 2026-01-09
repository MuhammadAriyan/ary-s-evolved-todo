"use client"

import { ReactNode } from "react"
import { SidebarProvider } from "./context/SidebarContext"

export default function TodoLayout({ children }: { children: ReactNode }) {
  return <SidebarProvider>{children}</SidebarProvider>
}
