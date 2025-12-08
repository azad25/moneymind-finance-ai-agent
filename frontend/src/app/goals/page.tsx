"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { mockGoals } from "@/lib/mock-data";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { format } from "date-fns";

export default function GoalsPage() {
    const goals = mockGoals;

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6 overflow-y-auto h-full">
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold tracking-tight">Financial Goals</h1>
                    <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        New Goal
                    </Button>
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
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
