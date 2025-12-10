/**
 * MoneyMind API Client
 * HTTP client for REST API calls with authentication
 */

import { API_ENDPOINTS } from './config';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface RequestOptions {
    method?: HttpMethod;
    body?: unknown;
    headers?: Record<string, string>;
    token?: string;
}

interface ApiResponse<T> {
    data: T | null;
    error: string | null;
    status: number;
}

/**
 * Get auth token from localStorage and cookies
 */
function getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('accessToken');
}

/**
 * Set auth tokens in localStorage
 */
export function setTokens(accessToken: string, refreshToken: string) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
}

/**
 * Clear auth tokens from localStorage
 */
export function clearTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
}

/**
 * Make an authenticated API request
 */
export async function apiRequest<T>(
    url: string,
    options: RequestOptions = {}
): Promise<ApiResponse<T>> {
    const { method = 'GET', body, headers = {}, token } = options;

    const authToken = token || getToken();

    const requestHeaders: Record<string, string> = {
        'Content-Type': 'application/json',
        ...headers,
    };

    if (authToken) {
        requestHeaders['Authorization'] = `Bearer ${authToken}`;
    }

    try {
        const response = await fetch(url, {
            method,
            headers: requestHeaders,
            body: body ? JSON.stringify(body) : undefined,
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            // Handle token refresh on 401
            if (response.status === 401 && !url.includes('/refresh')) {
                const refreshed = await refreshAccessToken();
                if (refreshed) {
                    // Retry the request with new token
                    return apiRequest<T>(url, options);
                }
            }

            return {
                data: null,
                error: data?.detail || data?.message || 'Request failed',
                status: response.status,
            };
        }

        return {
            data,
            error: null,
            status: response.status,
        };

    } catch (error) {
        return {
            data: null,
            error: error instanceof Error ? error.message : 'Network error',
            status: 0,
        };
    }
}

/**
 * Refresh the access token using refresh token
 */
async function refreshAccessToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return false;

    try {
        const response = await fetch(API_ENDPOINTS.auth.refresh, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            setTokens(data.access_token, data.refresh_token);
            return true;
        }

        // Refresh failed - clear tokens
        clearTokens();
        return false;

    } catch {
        clearTokens();
        return false;
    }
}

// ===========================================
// Auth API
// ===========================================

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    name?: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

export interface User {
    id: string;
    email: string;
    name?: string;
    picture?: string;
    subscription_tier: string;
    gmail_connected: boolean;
}

export const authApi = {
    login: async (data: LoginRequest) => {
        const response = await apiRequest<AuthResponse>(API_ENDPOINTS.auth.login, {
            method: 'POST',
            body: data,
        });

        if (response.data) {
            setTokens(response.data.access_token, response.data.refresh_token);
        }

        return response;
    },

    register: async (data: RegisterRequest) => {
        const response = await apiRequest<AuthResponse>(API_ENDPOINTS.auth.register, {
            method: 'POST',
            body: data,
        });

        if (response.data) {
            setTokens(response.data.access_token, response.data.refresh_token);
        }

        return response;
    },

    getMe: () => apiRequest<User>(API_ENDPOINTS.auth.me),

    logout: async () => {
        await apiRequest(API_ENDPOINTS.auth.logout, { method: 'POST' });
        clearTokens();
    },

    getGoogleAuthUrl: () => apiRequest<{ auth_url: string }>(API_ENDPOINTS.auth.google),
};

// ===========================================
// Expenses API
// ===========================================

export interface Expense {
    id: string;
    amount: number;
    currency: string;
    category: string;
    merchant: string;
    description?: string;
    expense_date: string;
    created_at: string;
}

export interface Income {
    id: string;
    amount: number;
    currency: string;
    source: string;
    category?: string;
    description?: string;
    income_date: string;
    created_at: string;
}

export const expensesApi = {
    list: (params?: { start_date?: string; end_date?: string; category?: string }) =>
        apiRequest<Expense[]>(`${API_ENDPOINTS.expenses.list}${params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : ''}`),

    create: (data: Omit<Expense, 'id' | 'created_at'>) =>
        apiRequest<Expense>(API_ENDPOINTS.expenses.create, { method: 'POST', body: data }),

    getCategories: () => apiRequest<{ category: string; total: number }[]>(API_ENDPOINTS.expenses.categories),
    
    getBalance: () => apiRequest<{ balance: number; currency: string; last_updated: string; total_income?: number; total_expenses?: number }>(API_ENDPOINTS.expenses.balance),
};

// Income API
export const incomeApi = {
    list: (params?: { start_date?: string; end_date?: string }) =>
        apiRequest<Income[]>(`${API_ENDPOINTS.income.list}${params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : ''}`),
    
    create: (data: Omit<Income, 'id' | 'created_at'>) =>
        apiRequest<Income>(API_ENDPOINTS.income.create, { method: 'POST', body: data }),
};

// ===========================================
// Subscriptions API
// ===========================================

export interface Subscription {
    id: string;
    name: string;
    amount: number;
    currency: string;
    billing_cycle: string;
    next_billing_date: string;
    is_active: boolean;
}

export const subscriptionsApi = {
    list: () => apiRequest<Subscription[]>(API_ENDPOINTS.subscriptions.list),
    create: (data: Omit<Subscription, 'id' | 'is_active'>) =>
        apiRequest<Subscription>(API_ENDPOINTS.subscriptions.create, { method: 'POST', body: data }),
    cancel: (id: string) =>
        apiRequest(API_ENDPOINTS.subscriptions.cancel(id), { method: 'DELETE' }),
};

// ===========================================
// Bills API
// ===========================================

export interface Bill {
    id: string;
    name: string;
    amount: number;
    currency: string;
    due_date: string;
    is_recurring: boolean;
    is_paid: boolean;
}

export const billsApi = {
    list: () => apiRequest<Bill[]>(API_ENDPOINTS.bills.list),
    upcoming: (days?: number) =>
        apiRequest<Bill[]>(`${API_ENDPOINTS.bills.upcoming}${days ? `?days=${days}` : ''}`),
    create: (data: Omit<Bill, 'id' | 'is_paid'>) =>
        apiRequest<Bill>(API_ENDPOINTS.bills.create, { method: 'POST', body: data }),
    markPaid: (id: string) =>
        apiRequest(API_ENDPOINTS.bills.markPaid(id), { method: 'POST' }),
};

// ===========================================
// Goals API
// ===========================================

export interface Goal {
    id: string;
    name: string;
    target_amount: number;
    current_amount: number;
    currency: string;
    deadline: string;
    is_completed: boolean;
}

export const goalsApi = {
    list: () => apiRequest<Goal[]>(API_ENDPOINTS.goals.list),
    create: (data: Omit<Goal, 'id' | 'current_amount' | 'is_completed'>) =>
        apiRequest<Goal>(API_ENDPOINTS.goals.create, { method: 'POST', body: data }),
    addContribution: (id: string, amount: number) =>
        apiRequest(API_ENDPOINTS.goals.addContribution(id), { method: 'POST', body: { amount } }),
};

// ===========================================
// Gmail API
// ===========================================

export const gmailApi = {
    getStatus: () => apiRequest<{ connected: boolean; email?: string }>(API_ENDPOINTS.gmail.status),
    getEmails: (query?: string) =>
        apiRequest<{ emails: unknown[] }>(`${API_ENDPOINTS.gmail.emails}${query ? `?query=${encodeURIComponent(query)}` : ''}`),
    getBankingEmails: (days?: number) =>
        apiRequest(`${API_ENDPOINTS.gmail.banking}${days ? `?days=${days}` : ''}`),
    sync: () => apiRequest(API_ENDPOINTS.gmail.sync, { method: 'POST' }),
    getInsights: () => apiRequest(API_ENDPOINTS.gmail.insights),
};

// ===========================================
// Health API
// ===========================================

export const healthApi = {
    check: () => apiRequest<{ status: string }>(API_ENDPOINTS.health),
};

export default {
    auth: authApi,
    expenses: expensesApi,
    income: incomeApi,
    subscriptions: subscriptionsApi,
    bills: billsApi,
    goals: goalsApi,
    gmail: gmailApi,
    health: healthApi,
};
