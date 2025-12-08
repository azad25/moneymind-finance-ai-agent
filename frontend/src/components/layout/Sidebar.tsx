"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, LayoutDashboard, Receipt, CreditCard, Wallet, Target, LogOut, Settings } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { toggleSidebar } from "@/lib/features/uiSlice";

export function Sidebar() {
    const pathname = usePathname();
    const dispatch = useAppDispatch();
    const { isSidebarCollapsed } = useAppSelector((state) => state.ui);

    const links = [
        { href: "/", label: "Overview", icon: LayoutDashboard },
        { href: "/expenses", label: "Expenses", icon: Receipt },
        { href: "/subscriptions", label: "Subscriptions", icon: CreditCard },
        { href: "/bills", label: "Bills & Loans", icon: Wallet },
        { href: "/goals", label: "Goals", icon: Target },
    ];

    return (
        <div className={cn(
            "h-full flex flex-col border-r bg-background/50 backdrop-blur-xl transition-all duration-300 relative group",
            isSidebarCollapsed ? "w-[80px]" : "w-[280px]"
        )}>
            <Button
                variant="ghost"
                size="icon"
                className="absolute -right-3 top-6 h-6 w-6 rounded-full border bg-background shadow-md opacity-0 group-hover:opacity-100 transition-opacity z-50 hidden md:flex"
                onClick={() => dispatch(toggleSidebar())}
            >
                {isSidebarCollapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </Button>

            <div className={cn(
                "p-6 font-bold text-2xl border-b border-border/50 flex items-center gap-3 overflow-hidden whitespace-nowrap",
                isSidebarCollapsed && "px-4 justify-center"
            )}>
                <div className="h-8 w-8 min-w-8 bg-gradient-to-br from-primary to-blue-600 rounded-xl shadow-lg shadow-primary/20" />
                <span className={cn(
                    "bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70 transition-all duration-300",
                    isSidebarCollapsed ? "opacity-0 w-0" : "opacity-100"
                )}>
                    MoneyMind
                </span>
            </div>

            <div className="flex-1 py-6 px-3">
                <nav className="space-y-2">
                    {links.map((link) => {
                        const Icon = link.icon;
                        const isActive = pathname === link.href;
                        return (
                            <Button
                                key={link.href}
                                variant={isActive ? "secondary" : "ghost"}
                                className={cn(
                                    "w-full h-11 text-base font-medium transition-all duration-200 overflow-hidden",
                                    isSidebarCollapsed ? "justify-center px-0" : "justify-start px-4",
                                    isActive
                                        ? "bg-primary/10 text-primary hover:bg-primary/15 shadow-sm"
                                        : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                                )}
                                asChild
                                title={isSidebarCollapsed ? link.label : undefined}
                            >
                                <Link href={link.href}>
                                    <Icon className={cn("h-5 w-5 min-w-5", isActive ? "text-primary" : "text-muted-foreground", !isSidebarCollapsed && "mr-3")} />
                                    {!isSidebarCollapsed && link.label}
                                </Link>
                            </Button>
                        );
                    })}
                </nav>
            </div>

            <div className="p-4 border-t border-border/50 space-y-2">
                <Button
                    variant={pathname === "/settings" ? "secondary" : "ghost"}
                    className={cn(
                        "w-full h-11 text-base font-medium transition-all duration-200 overflow-hidden",
                        isSidebarCollapsed ? "justify-center px-0" : "justify-start px-4",
                        pathname === "/settings"
                            ? "bg-primary/10 text-primary hover:bg-primary/15"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    )}
                    asChild
                    title={isSidebarCollapsed ? "Settings" : undefined}
                >
                    <Link href="/settings">
                        <Settings className={cn("h-5 w-5 min-w-5", !isSidebarCollapsed && "mr-3")} />
                        {!isSidebarCollapsed && "Settings"}
                    </Link>
                </Button>
                <Button
                    variant="ghost"
                    className={cn(
                        "w-full h-11 text-base font-medium text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors overflow-hidden",
                        isSidebarCollapsed ? "justify-center px-0" : "justify-start px-4"
                    )}
                    asChild
                    title={isSidebarCollapsed ? "Logout" : undefined}
                >
                    <Link href="/login">
                        <LogOut className={cn("h-5 w-5 min-w-5", !isSidebarCollapsed && "mr-3")} />
                        {!isSidebarCollapsed && "Logout"}
                    </Link>
                </Button>
            </div>
        </div>
    );
}
