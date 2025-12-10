"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Calendar } from "@/components/ui/calendar";
import { subscriptionsApi } from "@/lib/api/client";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { setSubscriptions } from "@/lib/features/financeSlice";
import { Subscription } from "@/lib/types";

export default function SubscriptionsPage() {
    const dispatch = useAppDispatch();
    const subscriptions = useAppSelector((state) => state.finance.subscriptions);
    const [date, setDate] = useState<Date | undefined>(new Date());
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        const fetchSubscriptions = async () => {
            setLoading(true);
            setError(null);
            const response = await subscriptionsApi.list();
            if (!isMounted) return;

            if (response.data) {
                const parsed = response.data.map((item: any) => ({
                    id: item.id,
                    name: item.name,
                    amount: Number(item.amount),
                    nextCharge: new Date(item.next_billing_date ?? item.created_at ?? Date.now()),
                    logo: item.logo,
                })) as Subscription[];
                dispatch(setSubscriptions(parsed));
            } else if (response.error) {
                setError(response.error);
            }
            setLoading(false);
        };

        fetchSubscriptions();
        return () => {
            isMounted = false;
        };
    }, [dispatch]);

    const totalMonthly = subscriptions.reduce((acc, sub) => acc + sub.amount, 0);

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight">Subscriptions</h1>
                    <div className="text-right">
                        {loading && <p className="text-sm text-muted-foreground">Loading...</p>}
                        {error && <p className="text-sm text-destructive">Error: {error}</p>}
                        {!loading && !error && (
                            <>
                                <p className="text-sm text-muted-foreground">Total Monthly</p>
                                <p className="text-2xl font-bold">${totalMonthly.toFixed(2)}</p>
                            </>
                        )}
                    </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Active Subscriptions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {subscriptions.length === 0 && !loading && (
                                <p className="text-sm text-muted-foreground">No subscriptions found.</p>
                            )}
                            {subscriptions.map((sub) => (
                                <div key={sub.id} className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <Avatar className="h-10 w-10">
                                            <AvatarFallback>{sub.logo || sub.name[0]}</AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-medium">{sub.name}</p>
                                            <p className="text-sm text-muted-foreground">
                                                Next charge: {format(sub.nextCharge, 'MMM d, yyyy')}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="font-bold">${sub.amount.toFixed(2)}</div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Renewal Calendar</CardTitle>
                        </CardHeader>
                        <CardContent className="flex justify-center">
                            <Calendar
                                mode="single"
                                selected={date}
                                onSelect={setDate}
                                className="rounded-md border"
                            />
                        </CardContent>
                    </Card>
                </div>
            </div>
        </DashboardLayout>
    );
}
