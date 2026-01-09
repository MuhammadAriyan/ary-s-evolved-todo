"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Github, Linkedin, Sun, Moon, ArrowUp, Heart } from "lucide-react";
import { useTheme } from "next-themes";

function handleScrollTop() {
  window.scroll({
    top: 0,
    behavior: "smooth",
  });
}

const ThemeToggle = () => {
  const { setTheme, theme } = useTheme();

  return (
    <div className="flex items-center justify-center">
      <div className="flex items-center rounded-full border border-white/20 backdrop-blur-sm">
        <button
          onClick={() => setTheme("light")}
          className={`rounded-full p-2 transition-colors ${
            theme === "light" ? "bg-sky-cyan-500 text-white" : "text-white/60 hover:text-white"
          }`}
        >
          <Sun className="h-5 w-5" strokeWidth={1.5} />
          <span className="sr-only">Light mode</span>
        </button>

        <button type="button" onClick={handleScrollTop} className="px-3 text-white/60 hover:text-white transition-colors">
          <ArrowUp className="h-4 w-4" />
          <span className="sr-only">Scroll to top</span>
        </button>

        <button
          onClick={() => setTheme("dark")}
          className={`rounded-full p-2 transition-colors ${
            theme === "dark" ? "bg-sky-cyan-500 text-white" : "text-white/60 hover:text-white"
          }`}
        >
          <Moon className="h-5 w-5" strokeWidth={1.5} />
          <span className="sr-only">Dark mode</span>
        </button>
      </div>
    </div>
  );
};

const navigation = {
  sections: [
    {
      id: "product",
      name: "Product",
      items: [
        { name: "Features", href: "#features" },
        { name: "Calendar", href: "#calendar" },
        { name: "Tags", href: "#tags" },
      ],
    },
    {
      id: "resources",
      name: "Resources",
      items: [
        { name: "Documentation", href: "#docs" },
        { name: "API", href: "#api" },
        { name: "Support", href: "#support" },
      ],
    },
    {
      id: "company",
      name: "Company",
      items: [
        { name: "About", href: "#about" },
        { name: "Privacy", href: "#privacy" },
        { name: "Terms", href: "#terms" },
      ],
    },
  ],
};

const socialLinks = [
  {
    name: "GitHub",
    href: "https://github.com",
    icon: Github,
  },
  {
    name: "LinkedIn",
    href: "https://linkedin.com",
    icon: Linkedin,
  },
];

const Underline = "hover:-translate-y-1 border border-white/20 rounded-xl p-2.5 transition-all hover:border-sky-cyan-500/50 hover:bg-white/5 backdrop-blur-sm";

export function Footer() {
  return (
    <footer className="relative border-t border-white/10 mt-20">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />

      <div className="relative mx-auto max-w-7xl px-6 py-12">
        {/* Top section */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4 mb-12">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link href="/" className="inline-block mb-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="text-2xl font-bold bg-gradient-to-r from-sky-cyan-400 via-soft-aqua-400 to-misty-white bg-clip-text text-transparent"
              >
                Ary's Todo
              </motion.div>
            </Link>
            <p className="text-sm text-white/50 leading-relaxed max-w-xs">
              A beautiful, glassmorphic todo application designed to help you stay organized and productive.
            </p>
          </div>

          {/* Navigation */}
          {navigation.sections.map((section) => (
            <div key={section.id}>
              <h3 className="text-sm font-semibold text-white/80 mb-4">{section.name}</h3>
              <ul className="space-y-3">
                {section.items.map((item) => (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className="text-sm text-white/50 hover:text-sky-cyan-400 transition-colors"
                    >
                      {item.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-white/10 mb-8" />

        {/* Bottom section */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Social links */}
          <div className="flex items-center gap-4">
            {socialLinks.map((link) => (
              <Link
                key={link.name}
                aria-label={link.name}
                href={link.href}
                rel="noreferrer"
                target="_blank"
                className={Underline}
              >
                <link.icon className="h-5 w-5 text-white/60 hover:text-sky-cyan-400 transition-colors" strokeWidth={1.5} />
              </Link>
            ))}
          </div>

          {/* Theme toggle */}
          <ThemeToggle />

          {/* Copyright */}
          <div className="flex items-center gap-1 text-sm text-white/40">
            <span>© {new Date().getFullYear()}</span>
            <span>Made with</span>
            <Heart className="h-4 w-4 text-soft-aqua-400 mx-1 animate-pulse" fill="currentColor" />
            <span>by</span>
            <span className="text-white/60 hover:text-sky-cyan-400 transition-colors cursor-pointer font-medium">
              Ary
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
