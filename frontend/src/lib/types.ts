export type MessageRole = 'user' | 'assistant';

export interface Attachment {
  id: string;
  name: string;
  type: 'image' | 'file';
  url: string;
  size?: number;
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  attachments?: Attachment[];
}

export interface ChartData {
  type: 'pie' | 'bar' | 'line';
  title: string;
  data: Record<string, any>[];
  colors: string[];
  dataKey?: string; // For bar/line charts
  nameKey?: string; // For pie charts
  category?: string; // X-axis key for bar/line
}

export interface Expense {
  id: string;
  merchant: string;
  amount: number;
  date: Date;
  category: string;
}

export interface Subscription {
  id: string;
  name: string;
  amount: number;
  nextCharge: Date;
  logo?: string;
}

export interface Bill {
  id: string;
  name: string;
  amount: number;
  dueDate: Date;
}

export interface Goal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  deadline: Date;
}

export interface MonthlyData {
  name: string;
  amount: number;
}

export interface DashboardStats {
  totalBalance: number;
  monthlySpending: number;
  upcomingBillsCount: number;
}
