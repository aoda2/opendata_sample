import type { Metadata } from "next";
import "./globals.css";
import { ApolloWrapper } from "@/components/ApolloWrapper";

export const metadata: Metadata = {
  title: "Yokohama Transit Insight",
  description: "横浜市営バス 遅延・到着予測ビューア",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body className="antialiased bg-gray-950 text-gray-100">
        <ApolloWrapper>{children}</ApolloWrapper>
      </body>
    </html>
  );
}
