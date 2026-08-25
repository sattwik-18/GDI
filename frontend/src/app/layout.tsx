import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "GDI — Genome Document Intelligence Forensic Workstation",
  description: "Enterprise Forensic Document Genome Extraction Workstation Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`h-full bg-[#0f1115] ${inter.variable} ${ibmPlexMono.variable}`}>
      <body className="h-full w-full overflow-hidden select-none bg-[#0f1115] text-[#e2e8f0] font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
