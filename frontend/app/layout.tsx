import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Home, Briefcase, FileText, Settings, User } from "lucide-react";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "CareerOS | AI Job Search Agent",
  description: "Automate your job search with CareerOS.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Toaster position="top-right" />
        <div className="flex min-h-screen bg-slate-50/50">
          {/* Sidebar */}
          <aside className="w-64 glass fixed h-full border-r border-slate-200 p-6 flex flex-col justify-between hidden md:flex">
            <div>
              <div className="flex items-center gap-2 mb-10">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">
                  C
                </div>
                <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
                  CareerOS
                </span>
              </div>
              
              <nav className="space-y-2">
                <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-all-ease font-medium">
                  <Home className="w-5 h-5" />
                  Dashboard
                </Link>
                <Link href="/jobs" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-all-ease font-medium">
                  <Briefcase className="w-5 h-5" />
                  Job Tracker
                </Link>
                <Link href="/profile" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-all-ease font-medium">
                  <User className="w-5 h-5" />
                  My Profile
                </Link>
                <Link href="/resumes" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-indigo-50 text-slate-600 hover:text-indigo-600 transition-all-ease font-medium">
                  <FileText className="w-5 h-5" />
                  Resumes
                </Link>
              </nav>
            </div>
            
            <div>
              <Link href="/settings" className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-100 text-slate-500 transition-all-ease font-medium">
                <Settings className="w-5 h-5" />
                Settings
              </Link>
            </div>
          </aside>
          
          {/* Main Content */}
          <main className="flex-1 md:ml-64 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
