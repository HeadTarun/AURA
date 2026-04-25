import type { Metadata } from "next";
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
      <body>{children}</body>
    </html>
  );
}
