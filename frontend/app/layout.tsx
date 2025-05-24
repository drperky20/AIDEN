import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: '--font-inter',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  display: "swap",
  variable: '--font-space',
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "AIDEN - AI Agent Platform",
  description: "An intelligent AI agent platform with memory, tools, and web search capabilities",
  keywords: ["AI", "assistant", "agent", "Gemini", "web search", "tools", "memory", "AIDEN"],
  authors: [{ name: "AIDEN Platform Team" }],
  icons: {
    icon: "/favicon.ico",
  },
  openGraph: {
    type: "website",
    title: "AIDEN - AI Agent Platform",
    description: "An intelligent AI agent platform with memory, tools, and web search capabilities",
    siteName: "AIDEN",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
