"use client";

import "./globals.css";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";

export default function RootLayout({ children }: any) {
  const [dark, setDark] = useState(true);

  // Load theme
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light") setDark(false);
  }, []);

  // Apply theme
  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [dark]);

  return (
    <html lang="en">
      <body className="flex">

        {/* Sidebar */}
        <Sidebar />

        {/* Main */}
        <div className="flex-1 p-6">

          <Header dark={dark} setDark={setDark} />

          {children}

        </div>

      </body>
    </html>
  );
}