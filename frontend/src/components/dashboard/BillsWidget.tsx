"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppSelector } from "@/lib/hooks";
import { format, differenceInDays } from "date-fns";
import { Badge } from "@/components/ui/badge";

export function BillsWidget() {
    const { bills } = useAppSelector((state) => state.finance);
    const today = new Date();

    return (
        <Card className="hover:shadow-md transition-all duration-300 border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Upcoming Bills</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {bills.slice(0, 3).map((bill) => {
                        const daysLeft = differenceInDays(new Date(bill.dueDate), today);
                        return (
                            <div key={bill.id} className="flex items-center justify-between group">
                                <div className="space-y-1">
                                    <p className="text-sm font-medium leading-none group-hover:text-primary transition-colors">{bill.name}</p>
                                    <p className="text-xs text-muted-foreground">
                                        Due {format(new Date(bill.dueDate), "MMM d")}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="font-medium text-sm">${bill.amount}</span>
                                    {daysLeft <= 3 && (
                                        <Badge variant="destructive" className="text-[10px] px-1 py-0 h-5">
                                            {daysLeft === 0 ? "Today" : `${daysLeft}d`}
                                        </Badge>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
