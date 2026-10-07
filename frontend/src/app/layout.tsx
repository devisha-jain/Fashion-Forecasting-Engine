import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Indian Fashion Forecasting Lab",
  description:
    "Forecasting tomorrow's Indian style through culture, identity & digital trends — powered by AI and real-time Google Trends data.",
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
