"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppSelector } from "@/lib/hooks";
import { format } from "date-fns";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function SubscriptionsWidget() {
    const { subscriptions } = useAppSelector((state) => state.finance);
    const totalMonthly = subscriptions.reduce((acc, sub) => acc + sub.amount, 0);

    return (
        <Card className="hover:shadow-md transition-all duration-300 border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Active Subscriptions</CardTitle>
                <div className="text-sm font-bold text-primary">
                    ${totalMonthly}/mo
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {subscriptions.slice(0, 3).map((sub) => (
                        <div key={sub.id} className="flex items-center group">
                            <Avatar className="h-9 w-9 border group-hover:border-primary/50 transition-colors">
                                <AvatarFallback className="text-xs">{sub.name.substring(0, 2)}</AvatarFallback>
                            </Avatar>
                            <div className="ml-4 space-y-1">
                                <p className="text-sm font-medium leading-none group-hover:text-primary transition-colors">{sub.name}</p>
                                <p className="text-xs text-muted-foreground">
                                    Next: {format(new Date(sub.nextCharge), "MMM d")}
                                </p>
                            </div>
                            <div className="ml-auto font-medium text-sm">
                                ${sub.amount}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
