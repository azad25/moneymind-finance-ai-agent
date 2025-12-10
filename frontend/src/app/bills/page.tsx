"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { format, differenceInDays } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle2 } from "lucide-react";
import { billsApi } from "@/lib/api/client";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { setBills } from "@/lib/features/financeSlice";
import { Bill } from "@/lib/types";

export default function BillsPage() {
    const dispatch = useAppDispatch();
    const bills = useAppSelector((state) => state.finance.bills);
    const today = new Date();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        const fetchBills = async () => {
            setLoading(true);
            setError(null);
            const response = await billsApi.list();
            if (!isMounted) return;

            if (response.data) {
                const parsed = response.data.map((item) => ({
                    id: item.id,
                    name: item.name,
                    amount: Number(item.amount),
                    dueDate: new Date((item as any).due_date),
                })) as Bill[];
                dispatch(setBills(parsed));
            } else if (response.error) {
                setError(response.error);
            }
            setLoading(false);
        };

        fetchBills();
        return () => {
            isMounted = false;
        };
    }, [dispatch]);

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight">Bills & Loans</h1>
                    {loading && <span className="text-sm text-muted-foreground">Loading...</span>}
                    {error && <span className="text-sm text-destructive">Error: {error}</span>}
                </div>

                <div className="grid gap-6">
                    {bills.length === 0 && !loading && (
                        <Card>
                            <CardContent className="p-6">
                                <p className="text-sm text-muted-foreground text-center">No bills found.</p>
                            </CardContent>
                        </Card>
                    )}
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
