import type { Metadata } from "next";
import GlobalSoundControls from "@/components/GlobalSoundControls";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Tutor",
  description: "Gamified learning paths for the AI Tutor MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
        <GlobalSoundControls />
      </body>
    </html>
  );
}
