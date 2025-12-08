"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppSelector } from "@/lib/hooks";
import { format } from "date-fns";
import { Line, LineChart, ResponsiveContainer, Tooltip } from "recharts";

export function ExpensesWidget() {
    const { expenses } = useAppSelector((state) => state.finance);

    // Prepare data for sparkline (last 7 expenses)
    const chartData = expenses.slice(0, 7).map((e, i) => ({
        i,
        amount: e.amount,
    })).reverse();

    return (
        <Card className="hover:shadow-md transition-all duration-300 border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Expenses Trend</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[80px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                            <Tooltip
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        return (
                                            <div className="rounded-lg border bg-background p-2 shadow-sm">
                                                <div className="grid grid-cols-2 gap-2">
                                                    <div className="flex flex-col">
                                                        <span className="text-[0.70rem] uppercase text-muted-foreground">
                                                            Amount
                                                        </span>
                                                        <span className="font-bold text-muted-foreground">
                                                            ${payload[0].value}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
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
    );
}
