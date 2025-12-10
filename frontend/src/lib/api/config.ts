/**
 * MoneyMind API Configuration
 * Environment-based API URLs
 */

// API Base URLs - use environment variables
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8010';

// API Endpoints
export const API_ENDPOINTS = {
    // Auth
    auth: {
        login: `${API_BASE_URL}/api/auth/login`,
        register: `${API_BASE_URL}/api/auth/register`,
        refresh: `${API_BASE_URL}/api/auth/refresh`,
        me: `${API_BASE_URL}/api/auth/me`,
        logout: `${API_BASE_URL}/api/auth/logout`,
        google: `${API_BASE_URL}/api/auth/google`,
        googleCallback: `${API_BASE_URL}/api/auth/google/callback`,
    },

    // Chat
    chat: {
        websocket: `${WS_BASE_URL}/ws/chat`,
        history: (sessionId: string) => `${API_BASE_URL}/ws/chat/history/${sessionId}`,
    },

    // Expenses
    expenses: {
        list: `${API_BASE_URL}/api/expenses`,
        create: `${API_BASE_URL}/api/expenses`,
        get: (id: string) => `${API_BASE_URL}/api/expenses/${id}`,
        update: (id: string) => `${API_BASE_URL}/api/expenses/${id}`,
        delete: (id: string) => `${API_BASE_URL}/api/expenses/${id}`,
        categories: `${API_BASE_URL}/api/expenses/categories`,
        balance: `${API_BASE_URL}/api/expenses/balance`,
    },

    // Income
    income: {
        list: `${API_BASE_URL}/api/expenses/income`,
        create: `${API_BASE_URL}/api/expenses/income`,
        get: (id: string) => `${API_BASE_URL}/api/expenses/income/${id}`,
    },

    // Subscriptions
    subscriptions: {
        list: `${API_BASE_URL}/api/expenses/subscriptions`,
        create: `${API_BASE_URL}/api/expenses/subscriptions`,
        cancel: (id: string) => `${API_BASE_URL}/api/expenses/subscriptions/${id}`,
    },

    // Bills
    bills: {
        list: `${API_BASE_URL}/api/expenses/bills`,
        upcoming: `${API_BASE_URL}/api/expenses/bills/upcoming`,
        create: `${API_BASE_URL}/api/expenses/bills`,
        markPaid: (id: string) => `${API_BASE_URL}/api/expenses/bills/${id}/mark-paid`,
    },

    // Goals
    goals: {
        list: `${API_BASE_URL}/api/expenses/goals`,
        create: `${API_BASE_URL}/api/expenses/goals`,
        update: (id: string) => `${API_BASE_URL}/api/expenses/goals/${id}`,
        addContribution: (id: string) => `${API_BASE_URL}/api/expenses/goals/${id}/contribute`,
    },

    // Documents
    documents: {
        upload: `${API_BASE_URL}/api/documents/upload`,
        list: `${API_BASE_URL}/api/documents`,
        query: `${API_BASE_URL}/api/documents/query`,
    },

    // Gmail
    gmail: {
        status: `${API_BASE_URL}/api/gmail/status`,
        emails: `${API_BASE_URL}/api/gmail/emails`,
        banking: `${API_BASE_URL}/api/gmail/banking-emails`,
        sync: `${API_BASE_URL}/api/gmail/sync`,
        insights: `${API_BASE_URL}/api/gmail/insights`,
    },

    // Payments
    payments: {
        checkout: `${API_BASE_URL}/api/payments/checkout`,
        plans: `${API_BASE_URL}/api/payments/plans`,
        subscription: `${API_BASE_URL}/api/payments/subscription`,
    },

    // Health
    health: `${API_BASE_URL}/health`,
};

export default API_ENDPOINTS;
