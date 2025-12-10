"use client";

import { useEffect, useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { expensesApi } from "@/lib/api/client";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { Expense } from "@/lib/types";
import { setExpenses, setMonthlyData } from "@/lib/features/financeSlice";

function buildMonthlyData(expenses: Expense[]) {
    const totals = new Map<string, number>();
    expenses.forEach((expense) => {
        const key = format(expense.date, "MMM yyyy");
        totals.set(key, (totals.get(key) || 0) + expense.amount);
    });
    return Array.from(totals.entries()).map(([name, amount]) => ({ name, amount }));
}

export default function ExpensesPage() {
    const dispatch = useAppDispatch();
    const expenses = useAppSelector((state) => state.finance.expenses);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        const fetchExpenses = async () => {
            setLoading(true);
            setError(null);
            const response = await expensesApi.list();
            if (!isMounted) return;

            if (response.data) {
                const parsed = response.data.map((item) => ({
                    id: item.id,
                    merchant: item.merchant,
                    amount: Number(item.amount),
                    date: new Date(item.expense_date || item.created_at),
                    category: item.category,
                })) as Expense[];

                dispatch(setExpenses(parsed));
                dispatch(setMonthlyData(buildMonthlyData(parsed)));
            } else if (response.error) {
                setError(response.error);
            }
            setLoading(false);
        };

        fetchExpenses();
        return () => {
            isMounted = false;
        };
    }, [dispatch]);

    const categoryData = useMemo(() => {
        return expenses.reduce((acc, curr) => {
            const existing = acc.find(item => item.name === curr.category);
            if (existing) {
                existing.value += curr.amount;
            } else {
                acc.push({ name: curr.category, value: curr.amount });
            }
            return acc;
        }, [] as { name: string; value: number }[]);
    }, [expenses]);

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight">Expenses</h1>
                    {loading && <span className="text-sm text-muted-foreground">Loading...</span>}
                    {error && <span className="text-sm text-destructive">Error: {error}</span>}
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                    <Card className="col-span-4">
                        <CardHeader>
                            <CardTitle>Overview</CardTitle>
                        </CardHeader>
                        <CardContent className="pl-2">
                            <ResponsiveContainer width="100%" height={350}>
                                <BarChart data={categoryData}>
                                    <XAxis
                                        dataKey="name"
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <YAxis
                                        stroke="#888888"
                                        fontSize={12}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(value) => `$${value}`}
                                    />
                                    <Tooltip
                                        cursor={{ fill: 'transparent' }}
                                        contentStyle={{ borderRadius: '8px' }}
                                    />
                                    <Bar dataKey="value" fill="currentColor" radius={[4, 4, 0, 0]} className="fill-primary" />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    <Card className="col-span-3">
                        <CardHeader>
                            <CardTitle>Recent Transactions</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {expenses.length === 0 && !loading && (
                                <p className="text-sm text-muted-foreground">No expenses yet.</p>
                            )}
                            <div className="space-y-8">
                                {expenses.map((expense) => (
                                    <div key={expense.id} className="flex items-center">
                                        <div className="ml-4 space-y-1">
                                            <p className="text-sm font-medium leading-none">{expense.merchant}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {format(expense.date, 'MMM d, yyyy')}
                                            </p>
                                        </div>
                                        <div className="ml-auto font-medium">-${expense.amount.toFixed(2)}</div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <Card>
                    <CardHeader>
                        <CardTitle>All Expenses</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Merchant</TableHead>
                                    <TableHead>Category</TableHead>
                                    <TableHead>Date</TableHead>
                                    <TableHead className="text-right">Amount</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {expenses.map((expense) => (
                                    <TableRow key={expense.id}>
                                        <TableCell className="font-medium">{expense.merchant}</TableCell>
                                        <TableCell>
                                            <Badge variant="secondary">{expense.category}</Badge>
                                        </TableCell>
                                        <TableCell>{format(expense.date, 'MMM d, yyyy')}</TableCell>
                                        <TableCell className="text-right">-${expense.amount.toFixed(2)}</TableCell>
                                    </TableRow>
                                ))}
                                {expenses.length === 0 && !loading && (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center text-sm text-muted-foreground">
                                            No expenses found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    );
}
