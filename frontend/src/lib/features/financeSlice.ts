import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Expense, Subscription, Bill, Goal, DashboardStats, MonthlyData } from '@/lib/types';

interface FinanceState {
    expenses: Expense[];
    subscriptions: Subscription[];
    bills: Bill[];
    goals: Goal[];
    stats: DashboardStats;
    monthlyData: MonthlyData[];
}

const initialState: FinanceState = {
    expenses: [],
    subscriptions: [],
    bills: [],
    goals: [],
    stats: {
        totalBalance: 0,
        monthlySpending: 0,
        upcomingBillsCount: 0,
    },
    monthlyData: [],
};

export const financeSlice = createSlice({
    name: 'finance',
    initialState,
    reducers: {
        setExpenses: (state, action: PayloadAction<Expense[]>) => {
            state.expenses = action.payload;
        },
        addExpense: (state, action: PayloadAction<Expense>) => {
            state.expenses.unshift(action.payload);
            state.stats.monthlySpending = (state.stats.monthlySpending || 0) + action.payload.amount;
            state.stats.totalBalance = (state.stats.totalBalance || 0) - action.payload.amount;
        },
        setSubscriptions: (state, action: PayloadAction<Subscription[]>) => {
            state.subscriptions = action.payload;
        },
        addGoal: (state, action: PayloadAction<Goal>) => {
            state.goals.push(action.payload);
        },
        setGoals: (state, action: PayloadAction<Goal[]>) => {
            state.goals = action.payload;
        },
        updateGoal: (state, action: PayloadAction<{ id: string; amount: number }>) => {
            const goal = state.goals.find(g => g.id === action.payload.id);
            if (goal) {
                goal.currentAmount = action.payload.amount;
            }
        },
        setBills: (state, action: PayloadAction<Bill[]>) => {
            state.bills = action.payload;
        },
        markBillPaid: (state, action: PayloadAction<string>) => {
            state.bills = state.bills.filter(b => b.id !== action.payload);
            state.stats.upcomingBillsCount = Math.max(0, (state.stats.upcomingBillsCount || 0) - 1);
        },
        setStats: (state, action: PayloadAction<DashboardStats>) => {
            state.stats = action.payload;
        },
        setMonthlyData: (state, action: PayloadAction<MonthlyData[]>) => {
            state.monthlyData = action.payload;
        },
    },
});

export const {
    setExpenses,
    addExpense,
    setSubscriptions,
    addGoal,
    setGoals,
    updateGoal,
    setBills,
    markBillPaid,
    setStats,
    setMonthlyData,
} = financeSlice.actions;
export default financeSlice.reducer;
