import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Contract Shield",
  description: "Upload freelance contracts and get risk-focused clause analysis.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
