"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { mockBills } from "@/lib/mock-data";
import { format, differenceInDays } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";

export default function BillsPage() {
    const bills = mockBills;
    const today = new Date();

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <h1 className="text-3xl font-bold tracking-tight">Bills & Loans</h1>

                <div className="grid gap-6">
                    {bills.map((bill) => {
                        const daysLeft = differenceInDays(bill.dueDate, today);
                        const isUrgent = daysLeft <= 3 && daysLeft >= 0;

                        return (
                            <Card key={bill.id} className={isUrgent ? "border-destructive/50 bg-destructive/5" : ""}>
                                <CardContent className="p-6 flex items-center justify-between">
                                    <div className="space-y-1">
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-semibold text-lg">{bill.name}</h3>
                                            {isUrgent && <Badge variant="destructive">Due Soon</Badge>}
                                        </div>
                                        <p className="text-sm text-muted-foreground">
                                            Due on {format(bill.dueDate, 'MMMM d, yyyy')} ({daysLeft} days left)
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-6">
                                        <div className="text-right">
                                            <p className="text-sm text-muted-foreground">Amount Due</p>
                                            <p className="text-2xl font-bold">${bill.amount.toFixed(2)}</p>
                                        </div>
                                        <Button>
                                            <CheckCircle2 className="mr-2 h-4 w-4" />
                                            Mark Paid
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </DashboardLayout>
    );
}
