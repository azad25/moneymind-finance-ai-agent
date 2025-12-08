"use client";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { cn } from "@/lib/utils";

import { useAppSelector } from "@/lib/hooks";

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const { isSidebarCollapsed } = useAppSelector((state) => state.ui);

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {/* Desktop Sidebar */}
            <aside className={cn(
                "hidden md:block flex-shrink-0 h-full transition-all duration-300",
                isSidebarCollapsed ? "w-[80px]" : "w-[280px]"
            )}>
                <Sidebar />
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-full overflow-hidden">
                <TopBar />
                <main className="flex-1 overflow-hidden relative flex flex-col">
                    {children}
                </main>
            </div>
        </div>
    );
}
