"use client";

import { useMemo, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, CreditCard, Calendar } from "lucide-react";
import { useAppSelector, useAppDispatch } from "@/lib/hooks";
import { Line, LineChart, ResponsiveContainer } from "recharts";
import { differenceInDays, isSameMonth } from "date-fns";
import { expensesApi } from "@/lib/api/client";
import { setStats } from "@/lib/features/financeSlice";

export function StatsRow() {
    const dispatch = useAppDispatch();
    const { expenses, bills, stats, monthlyData } = useAppSelector((state) => state.finance);
    const today = new Date();
    const [loadingBalance, setLoadingBalance] = useState(false);

    const derivedMonthlySpending = useMemo(() => {
        return expenses
            .filter((expense) => isSameMonth(expense.date, today))
            .reduce((sum, expense) => sum + expense.amount, 0);
    }, [expenses, today]);

    const derivedUpcomingBills = useMemo(() => {
        return bills.filter((bill) => {
            const days = differenceInDays(bill.dueDate, today);
            return days >= 0 && days <= 7;
        }).length;
    }, [bills, today]);

    useEffect(() => {
        const fetchBalance = async () => {
            setLoadingBalance(true);
            const response = await expensesApi.getBalance();
            if (response.data) {
                dispatch(setStats({
                    ...stats,
                    totalBalance: Number(response.data.balance),
                }));
            }
            setLoadingBalance(false);
        };
        fetchBalance();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [dispatch]);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 p-6 pb-0">
            <Card className="bg-gradient-to-br from-primary/10 to-blue-500/5 border-primary/20 shadow-lg shadow-primary/5 hover:shadow-primary/10 transition-all duration-300">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Balance</CardTitle>
                    <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                        <DollarSign className="h-4 w-4 text-primary" />
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-3xl font-bold tracking-tight">${(stats.totalBalance || 0).toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground mt-1">+2.5% from last month</p>
                </CardContent>
            </Card>
            <Card className="hover:shadow-md transition-all duration-300 border-border/50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Monthly Spending</CardTitle>
                    <div className="h-8 w-8 rounded-full bg-red-500/10 flex items-center justify-center">
                        <CreditCard className="h-4 w-4 text-red-500" />
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-3xl font-bold tracking-tight text-red-500">
                        -${(stats.monthlySpending || derivedMonthlySpending).toLocaleString()}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">12% more than average</p>
                </CardContent>
            </Card>
            <Card className="hover:shadow-md transition-all duration-300 border-border/50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Upcoming Bills</CardTitle>
                    <div className="h-8 w-8 rounded-full bg-orange-500/10 flex items-center justify-center">
                        <Calendar className="h-4 w-4 text-orange-500" />
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="text-3xl font-bold tracking-tight">{stats.upcomingBillsCount || derivedUpcomingBills}</div>
                    <p className="text-xs text-muted-foreground mt-1">Due in next 7 days</p>
                </CardContent>
            </Card>
            <Card className="hover:shadow-md transition-all duration-300 border-border/50">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Spending Trend</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-[60px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={monthlyData}>
                                <Line
                                    type="monotone"
                                    dataKey="amount"
                                    stroke="hsl(var(--primary))"
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
