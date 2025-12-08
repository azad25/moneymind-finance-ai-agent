"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppSelector } from "@/lib/hooks";
import { Progress } from "@/components/ui/progress";
import { format } from "date-fns";

export function GoalsWidget() {
    const { goals } = useAppSelector((state) => state.finance);

    return (
        <Card className="hover:shadow-md transition-all duration-300 border-border/50">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Financial Goals</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {goals.slice(0, 3).map((goal) => (
                        <div key={goal.id} className="space-y-2 group">
                            <div className="flex items-center justify-between text-sm">
                                <span className="font-medium group-hover:text-primary transition-colors">{goal.name}</span>
                                <span className="text-muted-foreground text-xs">
                                    ${goal.currentAmount} / ${goal.targetAmount}
                                </span>
                            </div>
                            <Progress
                                value={(goal.currentAmount / goal.targetAmount) * 100}
                                className="h-2 bg-muted/50"
                            />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
