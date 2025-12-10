/**
 * MoneyMind Auth Hook
 * Authentication state management
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { authApi, User, clearTokens, setTokens } from '@/lib/api';

interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
}

export function useAuth() {
    const [state, setState] = useState<AuthState>({
        user: null,
        isLoading: true,
        isAuthenticated: false,
        error: null,
    });

    // Check authentication on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = useCallback(async () => {
        const token = typeof window !== 'undefined'
            ? localStorage.getItem('accessToken')
            : null;

        if (!token) {
            setState({
                user: null,
                isLoading: false,
                isAuthenticated: false,
                error: null,
            });
            return;
        }

        try {
            const response = await authApi.getMe();

            if (response.data) {
                setState({
                    user: response.data,
                    isLoading: false,
                    isAuthenticated: true,
                    error: null,
                });
            } else {
                clearTokens();
                setState({
                    user: null,
                    isLoading: false,
                    isAuthenticated: false,
                    error: response.error,
                });
            }
        } catch {
            clearTokens();
            setState({
                user: null,
                isLoading: false,
                isAuthenticated: false,
                error: 'Authentication failed',
            });
        }
    }, []);

    const login = useCallback(async (email: string, password: string) => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        const response = await authApi.login({ email, password });

        if (response.data) {
            await checkAuth();
            return { success: true, error: null };
        }

        setState(prev => ({
            ...prev,
            isLoading: false,
            error: response.error
        }));

        return { success: false, error: response.error };
    }, [checkAuth]);

    const register = useCallback(async (email: string, password: string, name?: string) => {
        setState(prev => ({ ...prev, isLoading: true, error: null }));

        const response = await authApi.register({ email, password, name });

        if (response.data) {
            await checkAuth();
            return { success: true, error: null };
        }

        setState(prev => ({
            ...prev,
            isLoading: false,
            error: response.error
        }));

        return { success: false, error: response.error };
    }, [checkAuth]);

    const loginWithGoogle = useCallback(async () => {
        const response = await authApi.getGoogleAuthUrl();

        if (response.data?.auth_url) {
            window.location.href = response.data.auth_url;
            return { success: true, error: null };
        }

        return { success: false, error: response.error || 'Failed to get Google auth URL' };
    }, []);

    const handleGoogleCallback = useCallback(async (params: URLSearchParams) => {
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');

        if (accessToken && refreshToken) {
            setTokens(accessToken, refreshToken);
            await checkAuth();
            return { success: true, error: null };
        }

        return { success: false, error: 'Invalid callback parameters' };
    }, [checkAuth]);

    const logout = useCallback(async () => {
        await authApi.logout();
        setState({
            user: null,
            isLoading: false,
            isAuthenticated: false,
            error: null,
        });
    }, []);

    return {
        ...state,
        login,
        register,
        loginWithGoogle,
        handleGoogleCallback,
        logout,
        checkAuth,
    };
}

export default useAuth;
