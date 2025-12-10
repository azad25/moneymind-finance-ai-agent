import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/components/providers/AuthProvider";
import { RouteGuard } from "@/components/providers/RouteGuard";
import StoreProvider from "./StoreProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MoneyMind - Your Personal Finance AI",
  description: "AI-powered personal finance assistant with natural language interface",
  keywords: ["finance", "AI", "money", "budget", "expenses", "savings"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <StoreProvider>
          <AuthProvider>
            <RouteGuard>
              <ThemeProvider
                attribute="class"
                defaultTheme="dark"
                enableSystem
                disableTransitionOnChange
              >
                {children}
              </ThemeProvider>
            </RouteGuard>
          </AuthProvider>
        </StoreProvider>
      </body>
    </html>
  );
}
