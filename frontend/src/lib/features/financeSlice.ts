import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Expense, Subscription, Bill, Goal, DashboardStats, MonthlyData } from '@/lib/types';
import { mockExpenses, mockSubscriptions, mockBills, mockGoals, mockStats, mockMonthlyData } from '@/lib/mock-data';

interface FinanceState {
    expenses: Expense[];
    subscriptions: Subscription[];
    bills: Bill[];
    goals: Goal[];
    stats: DashboardStats;
    monthlyData: MonthlyData[];
}

const initialState: FinanceState = {
    expenses: mockExpenses,
    subscriptions: mockSubscriptions,
    bills: mockBills,
    goals: mockGoals,
    stats: mockStats,
    monthlyData: mockMonthlyData,
};

export const financeSlice = createSlice({
    name: 'finance',
    initialState,
    reducers: {
        addExpense: (state, action: PayloadAction<Expense>) => {
            state.expenses.unshift(action.payload);
            state.stats.monthlySpending += action.payload.amount;
            state.stats.totalBalance -= action.payload.amount;
        },
        addGoal: (state, action: PayloadAction<Goal>) => {
            state.goals.push(action.payload);
        },
        updateGoal: (state, action: PayloadAction<{ id: string; amount: number }>) => {
            const goal = state.goals.find(g => g.id === action.payload.id);
            if (goal) {
                goal.currentAmount = action.payload.amount;
            }
        },
        markBillPaid: (state, action: PayloadAction<string>) => {
            state.bills = state.bills.filter(b => b.id !== action.payload);
            state.stats.upcomingBillsCount = Math.max(0, state.stats.upcomingBillsCount - 1);
        },
    },
});

export const { addExpense, addGoal, updateGoal, markBillPaid } = financeSlice.actions;
export default financeSlice.reducer;
