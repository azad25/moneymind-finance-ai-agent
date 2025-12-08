import { Bill, DashboardStats, Expense, Goal, Subscription } from './types';

export const mockStats: DashboardStats = {
    totalBalance: 12450.80,
    monthlySpending: 3240.50,
    upcomingBillsCount: 3,
};

export const mockExpenses: Expense[] = [
    { id: '1', merchant: 'Starbucks', amount: 5.50, date: new Date('2025-12-07T08:30:00'), category: 'Food' },
    { id: '2', merchant: 'Uber', amount: 18.20, date: new Date('2025-12-06T18:15:00'), category: 'Transport' },
    { id: '3', merchant: 'Amazon', amount: 45.99, date: new Date('2025-12-05T14:20:00'), category: 'Shopping' },
    { id: '4', merchant: 'Whole Foods', amount: 120.45, date: new Date('2025-12-04T17:45:00'), category: 'Groceries' },
    { id: '5', merchant: 'Netflix', amount: 15.99, date: new Date('2025-12-03T09:00:00'), category: 'Entertainment' },
];

export const mockSubscriptions: Subscription[] = [
    { id: '1', name: 'Netflix', amount: 15.99, nextCharge: new Date('2026-01-03'), logo: 'N' },
    { id: '2', name: 'Spotify', amount: 9.99, nextCharge: new Date('2025-12-15'), logo: 'S' },
    { id: '3', name: 'Adobe CC', amount: 52.99, nextCharge: new Date('2025-12-20'), logo: 'A' },
];

export const mockBills: Bill[] = [
    { id: '1', name: 'Rent', amount: 1500.00, dueDate: new Date('2026-01-01') },
    { id: '2', name: 'Electricity', amount: 85.40, dueDate: new Date('2025-12-12') },
    { id: '3', name: 'Internet', amount: 60.00, dueDate: new Date('2025-12-18') },
];

export const mockGoals: Goal[] = [
    { id: '1', name: 'Vacation', targetAmount: 5000, currentAmount: 2350, deadline: new Date('2026-06-01') },
    { id: '2', name: 'New Laptop', targetAmount: 2000, currentAmount: 1800, deadline: new Date('2026-01-15') },
];

export const mockMonthlyData = [
    { name: "Jan", amount: 2400 },
    { name: "Feb", amount: 1398 },
    { name: "Mar", amount: 9800 },
    { name: "Apr", amount: 3908 },
    { name: "May", amount: 4800 },
    { name: "Jun", amount: 3800 },
    { name: "Jul", amount: 4300 },
];
