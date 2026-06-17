import type { Metadata, Viewport } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import { Providers } from "@/components/providers";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000"),
  title: {
    default: "OmniAssist Health — Understand Your Prescriptions & Lab Reports",
    template: "%s · OmniAssist Health",
  },
  description:
    "Upload a prescription or lab report and get a clear, simple explanation of every medicine and result — plus an AI health assistant for your questions. Not a diagnosis.",
  keywords: [
    "prescription AI",
    "lab report analyzer",
    "medicine information",
    "AI health assistant",
    "healthcare AI copilot",
    "understand your health",
  ],
  authors: [{ name: "OmniAssist Health" }],
  openGraph: {
    title: "OmniAssist Health",
    description: "Understand your prescriptions, lab reports and health — in plain language.",
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
