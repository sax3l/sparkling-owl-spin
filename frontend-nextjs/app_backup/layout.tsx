import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECaDP - Enhanced Crawler and Data Processing Platform",
  description: "Advanced web crawling and data processing platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="dark">
        {children}
      </body>
    </html>
  );
}