import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CineMatch - Find a movie together",
  description: "Swipe through movies with your partner and find the perfect match",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="bg-[#0a0a0a]">
        <body className={`${inter.className} bg-background`}>{children}</body>
      </html>
    </ClerkProvider>
  );
}
