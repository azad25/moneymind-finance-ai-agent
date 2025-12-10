/**
 * MoneyMind WebSocket Hook
 * Real-time chat connection with the backend
 */
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { API_ENDPOINTS } from '@/lib/api/config';

// Message types from backend
export interface ChatMessage {
    type: 'status' | 'stream' | 'complete' | 'error' | 'system' | 'chart' | 'pong';
    content?: string;
    session_id?: string;
    chart?: {
        type: string;
        title: string;
        data: unknown[];
        colors?: string[];
    };
}

interface UseWebSocketOptions {
    autoConnect?: boolean;
    reconnectInterval?: number;
    maxReconnectAttempts?: number;
}

interface WebSocketState {
    isConnected: boolean;
    isConnecting: boolean;
    sessionId: string | null;
    error: string | null;
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
    const {
        autoConnect = true,
        reconnectInterval = 3000,
        maxReconnectAttempts = 5,
    } = options;

    const [state, setState] = useState<WebSocketState>({
        isConnected: false,
        isConnecting: false,
        sessionId: null,
        error: null,
    });

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectAttemptsRef = useRef(0);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const messageHandlersRef = useRef<((message: ChatMessage) => void)[]>([]);

    // Connect to WebSocket
    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setState(prev => ({ ...prev, isConnecting: true, error: null }));

        try {
            // Get token from localStorage
            const token = typeof window !== 'undefined'
                ? localStorage.getItem('accessToken')
                : null;

            const wsUrl = token
                ? `${API_ENDPOINTS.chat.websocket}?token=${token}`
                : API_ENDPOINTS.chat.websocket;

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('✅ WebSocket connected');
                setState(prev => ({ ...prev, isConnected: true, isConnecting: false }));
                reconnectAttemptsRef.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const message: ChatMessage = JSON.parse(event.data);

                    // Handle system messages
                    if (message.type === 'system' && message.session_id) {
                        setState(prev => ({ ...prev, sessionId: message.session_id || null }));
                    }

                    // Notify all handlers
                    messageHandlersRef.current.forEach(handler => handler(message));
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                setState(prev => ({ ...prev, error: 'Connection error' }));
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setState(prev => ({ ...prev, isConnected: false, isConnecting: false }));
                wsRef.current = null;

                // Attempt reconnect
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    reconnectAttemptsRef.current++;
                    console.log(`Reconnecting... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
                    reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
                } else {
                    setState(prev => ({
                        ...prev,
                        error: 'Failed to connect after multiple attempts'
                    }));
                }
            };

        } catch (error) {
            setState(prev => ({
                ...prev,
                isConnecting: false,
                error: error instanceof Error ? error.message : 'Failed to connect'
            }));
        }
    }, [reconnectInterval, maxReconnectAttempts]);

    // Disconnect
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setState(prev => ({ ...prev, isConnected: false, sessionId: null }));
    }, []);

    // Send message
    const sendMessage = useCallback((content: string) => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not connected');
            return false;
        }

        try {
            wsRef.current.send(JSON.stringify({
                type: 'message',
                content,
            }));
            return true;
        } catch (error) {
            console.error('Failed to send message:', error);
            return false;
        }
    }, []);

    // Clear chat
    const clearChat = useCallback(() => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) return;

        wsRef.current.send(JSON.stringify({ type: 'clear' }));
    }, []);

    // Ping
    const ping = useCallback(() => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) return;

        wsRef.current.send(JSON.stringify({ type: 'ping' }));
    }, []);

    // Subscribe to messages
    const onMessage = useCallback((handler: (message: ChatMessage) => void) => {
        messageHandlersRef.current.push(handler);

        return () => {
            messageHandlersRef.current = messageHandlersRef.current.filter(h => h !== handler);
        };
    }, []);

    // Auto-connect on mount
    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [autoConnect, connect, disconnect]);

    return {
        ...state,
        connect,
        disconnect,
        sendMessage,
        clearChat,
        ping,
        onMessage,
    };
}

export default useWebSocket;
