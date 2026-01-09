import type { Metadata } from "next"
import "./globals.css"
import { PageWrapper } from "@/components/layout/PageWrapper"

export const metadata: Metadata = {
  title: "Ary's Evolved Todo - Sky-Aura Glass",
  description: "Anime-inspired, nature-themed glassmorphic todo application",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Chelsea+Market&display=swap" rel="stylesheet" />
      </head>
      <body className="font-chelsea antialiased">
        <PageWrapper>{children}</PageWrapper>
      </body>
    </html>
  )
}
