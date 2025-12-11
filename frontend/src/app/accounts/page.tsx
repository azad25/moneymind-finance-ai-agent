"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Wallet, TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { expensesApi, incomeApi } from "@/lib/api/client";
import { useToast } from "@/components/ui/use-toast";

export default function AccountsPage() {
    const { toast } = useToast();
    const [balance, setBalance] = useState(0);
    const [totalIncome, setTotalIncome] = useState(0);
    const [totalExpenses, setTotalExpenses] = useState(0);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadAccountData();
    }, []);

    const loadAccountData = async () => {
        setIsLoading(true);
        try {
            const balanceResponse = await expensesApi.getBalance();
            if (balanceResponse.data) {
                setBalance(balanceResponse.data.balance);
                setTotalIncome(balanceResponse.data.total_income || 0);
                setTotalExpenses(balanceResponse.data.total_expenses || 0);
            }
        } catch (error: any) {
            toast({
                title: "Error loading data",
                description: error.message || "Failed to load account data",
                variant: "destructive",
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold">Account Overview</h1>
                    <p className="text-muted-foreground">Your financial summary</p>
                </div>

                {/* Summary Cards */}
                {isLoading ? (
                    <div className="text-center py-12">
                        <p className="text-muted-foreground">Loading...</p>
                    </div>
                ) : (
                    <div className="grid gap-4 md:grid-cols-3">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Current Balance</CardTitle>
                                <DollarSign className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    ${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Total available funds
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Income</CardTitle>
                                <TrendingUp className="h-4 w-4 text-green-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-green-600">
                                    ${totalIncome.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    All time income
                                </p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
                                <TrendingDown className="h-4 w-4 text-red-500" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-red-600">
                                    ${totalExpenses.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    All time expenses
                                </p>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Info Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>Account Management</CardTitle>
                        <CardDescription>
                            Your financial overview is calculated from your income and expenses
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Track your finances by adding income and expenses through the chat interface or dedicated pages.
                            Your balance is automatically calculated based on all transactions.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    );
}
