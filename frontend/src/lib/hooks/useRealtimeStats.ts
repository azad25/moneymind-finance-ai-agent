/**
 * MoneyMind Real-time Stats Hook
 * Automatically updates stats when data changes
 */
'use client';

import { useEffect, useCallback } from 'react';
import { useAppDispatch } from '@/lib/hooks';
import { setStats } from '@/lib/features/financeSlice';
import { expensesApi, subscriptionsApi, billsApi, goalsApi } from '@/lib/api';

export function useRealtimeStats() {
    const dispatch = useAppDispatch();

    const fetchAndUpdateStats = useCallback(async () => {
        try {
            // Fetch all data in parallel including balance
            const [expensesRes, subscriptionsRes, billsRes, goalsRes, balanceRes] = await Promise.all([
                expensesApi.list(),
                subscriptionsApi.list(),
                billsApi.list(),
                goalsApi.list(),
                expensesApi.getBalance(),
            ]);

            // Calculate stats
            const expenses = expensesRes.data || [];
            const subscriptions = subscriptionsRes.data || [];
            const bills = billsRes.data || [];
            const goals = goalsRes.data || [];
            const balance = balanceRes.data?.balance || 0;

            // Calculate monthly spending (current month)
            const now = new Date();
            const currentMonth = now.getMonth();
            const currentYear = now.getFullYear();

            const monthlySpending = expenses
                .filter(exp => {
                    const expDate = new Date(exp.expense_date);
                    return expDate.getMonth() === currentMonth && expDate.getFullYear() === currentYear;
                })
                .reduce((sum, exp) => sum + exp.amount, 0);

            // Calculate total subscriptions
            const totalSubscriptions = subscriptions
                .filter(sub => sub.is_active)
                .reduce((sum, sub) => sum + sub.amount, 0);

            // Count upcoming bills (next 30 days)
            const thirtyDaysFromNow = new Date();
            thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);

            const upcomingBills = bills.filter(bill => {
                const dueDate = new Date(bill.due_date);
                return !bill.is_paid && dueDate <= thirtyDaysFromNow && dueDate >= now;
            }).length;

            // Calculate savings progress (average of all goals)
            const savingsProgress = goals.length > 0
                ? goals.reduce((sum, goal) => {
                    const progress = goal.target_amount > 0
                        ? (goal.current_amount / goal.target_amount) * 100
                        : 0;
                    return sum + progress;
                }, 0) / goals.length
                : 0;

            // Update Redux store
            dispatch(setStats({
                monthlySpending,
                totalSubscriptions,
                upcomingBills,
                upcomingBillsCount: upcomingBills,
                savingsProgress: Math.round(savingsProgress),
                totalBalance: Number(balance),
            }));

        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    }, [dispatch]);

    // Fetch stats on mount
    useEffect(() => {
        fetchAndUpdateStats();
    }, [fetchAndUpdateStats]);

    // Set up polling for real-time updates (every 30 seconds)
    useEffect(() => {
        const interval = setInterval(fetchAndUpdateStats, 30000);
        return () => clearInterval(interval);
    }, [fetchAndUpdateStats]);

    // Return manual refresh function
    return { refreshStats: fetchAndUpdateStats };
}
