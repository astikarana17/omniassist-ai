import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "OmniAssist AI — AI Customer Support & Sales Platform",
    template: "%s · OmniAssist AI",
  },
  description:
    "One AI brain across chat, WhatsApp, email and voice — grounded in your knowledge, escalates to humans. Enterprise AI customer support & sales agent platform.",
  keywords: [
    "AI customer support",
    "AI sales agent",
    "WhatsApp support",
    "RAG knowledge base",
    "helpdesk",
    "SaaS",
  ],
  authors: [{ name: "OmniAssist AI" }],
  openGraph: {
    title: "OmniAssist AI",
    description: "The AI workforce for customer support & sales.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#08080A",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable} dark`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
