"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, CreditCard, Calendar } from "lucide-react";
import { useAppSelector } from "@/lib/hooks";
import { Line, LineChart, ResponsiveContainer } from "recharts";

export function StatsRow() {
    const { stats, monthlyData } = useAppSelector((state) => state.finance);

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
                    <div className="text-3xl font-bold tracking-tight">${stats.totalBalance.toLocaleString()}</div>
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
                    <div className="text-3xl font-bold tracking-tight text-red-500">-${stats.monthlySpending.toLocaleString()}</div>
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
                    <div className="text-3xl font-bold tracking-tight">{stats.upcomingBillsCount}</div>
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
