"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { format } from "date-fns";
import { goalsApi } from "@/lib/api/client";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { setGoals } from "@/lib/features/financeSlice";
import { Goal } from "@/lib/types";

export default function GoalsPage() {
    const dispatch = useAppDispatch();
    const goals = useAppSelector((state) => state.finance.goals);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isMounted = true;
        const fetchGoals = async () => {
            setLoading(true);
            setError(null);
            const response = await goalsApi.list();
            if (!isMounted) return;

            if (response.data) {
                const parsed = response.data.map((item: any) => ({
                    id: item.id,
                    name: item.name,
                    targetAmount: Number(item.target_amount ?? item.targetAmount ?? 0),
                    currentAmount: Number(item.current_amount ?? item.currentAmount ?? 0),
                    deadline: new Date(item.deadline ?? Date.now()),
                })) as Goal[];
                dispatch(setGoals(parsed));
            } else if (response.error) {
                setError(response.error);
            }
            setLoading(false);
        };

        fetchGoals();
        return () => {
            isMounted = false;
        };
    }, [dispatch]);

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight">Financial Goals</h1>
                    <div className="flex items-center gap-4">
                        {loading && <span className="text-sm text-muted-foreground">Loading...</span>}
                        {error && <span className="text-sm text-destructive">Error: {error}</span>}
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            New Goal
                        </Button>
                    </div>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {goals.length === 0 && !loading && (
                        <Card>
                            <CardContent className="p-6">
                                <p className="text-sm text-muted-foreground text-center">No goals found.</p>
                            </CardContent>
                        </Card>
                    )}
                    {goals.map((goal) => {
                        const percent = Math.min(100, (goal.currentAmount / goal.targetAmount) * 100);
                        return (
                            <Card key={goal.id}>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">{goal.name}</CardTitle>
                                    <span className="text-xs text-muted-foreground">
                                        Target: {format(goal.deadline, 'MMM yyyy')}
                                    </span>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">${goal.currentAmount.toLocaleString()}</div>
                                    <p className="text-xs text-muted-foreground mb-4">
                                        of ${goal.targetAmount.toLocaleString()}
                                    </p>
                                    <Progress value={percent} className="h-2" />
                                    <p className="text-xs text-muted-foreground mt-2 text-right">
                                        {Math.round(percent)}%
                                    </p>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </DashboardLayout>
    );
}
