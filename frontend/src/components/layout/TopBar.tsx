"use client";

import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Menu, LogOut } from "lucide-react";
import { Sidebar } from "./Sidebar";
import { useAppSelector } from "@/lib/hooks";
import { useAuthContext } from "@/components/providers/AuthProvider";
import { useRouter } from "next/navigation";

export function TopBar() {
    const { stats } = useAppSelector((state) => state.finance);
    const { logout, user } = useAuthContext();
    const router = useRouter();

    const handleLogout = async () => {
        await logout();
        router.push('/login');
    };

    return (
        <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-6 lg:h-[60px]">
            <div className="flex flex-1 items-center gap-4 md:gap-8">
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="outline" size="icon" className="shrink-0 md:hidden" suppressHydrationWarning>
                            <Menu className="h-5 w-5" />
                            <span className="sr-only">Toggle navigation menu</span>
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="left" className="flex flex-col p-0 w-64">
                        <Sidebar />
                    </SheetContent>
                </Sheet>
                <span className="font-bold text-lg">MoneyMind</span>
            </div>
            <div className="flex items-center gap-4">
                <div className="text-sm font-medium hidden sm:block">
                    <span className="text-muted-foreground mr-2">Spending:</span>
                    ${(stats.monthlySpending || 0).toLocaleString()}
                </div>
                {user && (
                    <div className="text-sm text-muted-foreground hidden lg:block">
                        {user.email}
                    </div>
                )}
                <Button 
                    variant="ghost" 
                    size="sm" 
                    className="hidden md:flex gap-2"
                    onClick={handleLogout}
                >
                    <LogOut className="h-4 w-4" />
                    Logout
                </Button>
            </div>
        </header>
    );
}
