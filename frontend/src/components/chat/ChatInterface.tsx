"use client";

import { useRef, useEffect, useState, useCallback } from "react";
import { Message, Attachment } from "@/lib/types";
import { ChatInput } from "./ChatInput";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import ReactMarkdown from "react-markdown";
import { ChartRenderer } from "./ChartRenderer";
import { AttachmentView } from "./AttachmentView";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { addMessage, setTyping, clearChat, setStreamingMessage } from "@/lib/features/chatSlice";
import { NotificationAlert, NotificationType } from "./NotificationAlert";
import { useWebSocket, ChatMessage } from "@/lib/hooks/useWebSocket";
import { Wifi, WifiOff, Loader2 } from "lucide-react";

export function ChatInterface() {
    const dispatch = useAppDispatch();
    const { messages, isTyping, streamingMessage } = useAppSelector((state) => state.chat);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [notification, setNotification] = useState<{ message: string; type: NotificationType; isVisible: boolean }>({
        message: "",
        type: "info",
        isVisible: false,
    });

    // WebSocket connection
    const {
        isConnected,
        isConnecting,
        sendMessage: wsSendMessage,
        onMessage,
        clearChat: wsClearChat,
    } = useWebSocket({ autoConnect: true });

    // Handle WebSocket messages
    useEffect(() => {
        const unsubscribe = onMessage((message: ChatMessage) => {
            switch (message.type) {
                case 'system':
                    // Welcome message
                    if (message.content) {
                        showNotification(message.content, "success");
                    }
                    break;

                case 'status':
                    // Status update (thinking, using tools, etc.)
                    if (message.content) {
                        dispatch(setTyping(true));
                        dispatch(setStreamingMessage(message.content));
                    }
                    break;

                case 'stream':
                    // Streaming response content
                    if (message.content) {
                        dispatch(setStreamingMessage(message.content));
                    }
                    break;

                case 'complete':
                    // Final response
                    dispatch(setTyping(false));
                    if (message.content) {
                        const aiMessage: Message = {
                            id: Date.now().toString(),
                            role: 'assistant',
                            content: message.content,
                            timestamp: new Date(),
                        };
                        dispatch(addMessage(aiMessage));
                    }
                    dispatch(setStreamingMessage(null));
                    break;

                case 'chart':
                    // Chart data - embed in message
                    if (message.chart) {
                        const chartContent = `\`\`\`chart\n${JSON.stringify(message.chart)}\n\`\`\``;
                        const chartMessage: Message = {
                            id: Date.now().toString(),
                            role: 'assistant',
                            content: chartContent,
                            timestamp: new Date(),
                        };
                        dispatch(addMessage(chartMessage));
                    }
                    break;

                case 'error':
                    dispatch(setTyping(false));
                    dispatch(setStreamingMessage(null));
                    showNotification(message.content || 'An error occurred', 'error');
                    break;
            }
        });

        return unsubscribe;
    }, [dispatch, onMessage]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping, streamingMessage]);

    const showNotification = (message: string, type: NotificationType = "info") => {
        setNotification({ message, type, isVisible: true });
    };

    const handleNewChat = () => {
        dispatch(clearChat());
        wsClearChat();
        showNotification("New chat session started", "success");
    };

    const handleSend = useCallback(async (content: string, files: File[]) => {
        if (!content.trim() && files.length === 0) return;

        // Check connection
        if (!isConnected) {
            showNotification("Connecting to server...", "warning");
            return;
        }

        // Convert files to attachments (for display only - upload handled separately)
        const newAttachments: Attachment[] = files.map(file => ({
            id: Math.random().toString(36).substring(7),
            name: file.name,
            type: file.type.startsWith('image/') ? 'image' : 'file',
            url: URL.createObjectURL(file),
            size: file.size
        }));

        // Add user message to state
        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
            attachments: newAttachments.length > 0 ? newAttachments : undefined
        };
        dispatch(addMessage(userMessage));
        dispatch(setTyping(true));

        // Send to backend via WebSocket
        const sent = wsSendMessage(content);
        if (!sent) {
            dispatch(setTyping(false));
            showNotification("Failed to send message", "error");
        }
    }, [dispatch, isConnected, wsSendMessage]);

    const isEmpty = messages.length === 0;

    const suggestions = [
        { label: "Analyze my spending", icon: "📊" },
        { label: "Show recent transactions", icon: "💳" },
        { label: "Convert 100 USD to EUR", icon: "💱" },
        { label: "What's the price of AAPL?", icon: "📈" },
    ];

    // Connection status indicator
    const ConnectionStatus = () => (
        <div className={cn(
            "fixed top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all z-50",
            isConnected
                ? "bg-green-500/10 text-green-500"
                : isConnecting
                    ? "bg-yellow-500/10 text-yellow-500"
                    : "bg-red-500/10 text-red-500"
        )}>
            {isConnecting ? (
                <>
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Connecting...
                </>
            ) : isConnected ? (
                <>
                    <Wifi className="h-3 w-3" />
                    Connected
                </>
            ) : (
                <>
                    <WifiOff className="h-3 w-3" />
                    Disconnected
                </>
            )}
        </div>
    );

    return (
        <div className="flex flex-col h-full relative">
            <ConnectionStatus />
            <NotificationAlert
                message={notification.message}
                type={notification.type}
                isVisible={notification.isVisible}
                onClose={() => setNotification(prev => ({ ...prev, isVisible: false }))}
            />
            {isEmpty ? (
                <div className="flex-1 flex flex-col items-center justify-center p-4 space-y-8">
                    <div className="flex flex-col items-center space-y-4 animate-in fade-in zoom-in duration-500">
                        <div className="h-16 w-16 bg-gradient-to-br from-primary to-blue-600 rounded-2xl shadow-2xl shadow-primary/20 flex items-center justify-center">
                            <span className="text-3xl font-bold text-white">M</span>
                        </div>
                        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                            MoneyMind <span className="text-primary">Finance AI Assistant</span>
                        </h2>
                        <p className="text-sm text-muted-foreground text-center max-w-md">
                            Ask me about expenses, currency rates, stock prices, or anything finance-related!
                        </p>
                    </div>

                    <div className="w-full max-w-2xl">
                        <ChatInput onSend={handleSend} disabled={isTyping || !isConnected} centered={true} />

                        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3 px-4">
                            {suggestions.map((suggestion) => (
                                <button
                                    key={suggestion.label}
                                    onClick={() => handleSend(suggestion.label, [])}
                                    disabled={!isConnected}
                                    className="flex flex-col items-center gap-2 p-4 rounded-xl bg-muted/30 hover:bg-muted/50 border border-border/50 hover:border-primary/20 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <span className="text-2xl group-hover:scale-110 transition-transform duration-300">{suggestion.icon}</span>
                                    <span className="text-xs font-medium text-muted-foreground group-hover:text-foreground text-center">{suggestion.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    <ScrollArea className="flex-1 p-4 pb-24">
                        <div className="max-w-3xl mx-auto space-y-6 pb-4">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={cn(
                                        "flex gap-3",
                                        message.role === 'user' ? "flex-row-reverse" : "flex-row"
                                    )}
                                >
                                    <Avatar className="h-8 w-8">
                                        <AvatarFallback>{message.role === 'user' ? 'ME' : 'AI'}</AvatarFallback>
                                        {message.role === 'assistant' && <AvatarImage src="/bot-avatar.png" />}
                                    </Avatar>
                                    <div
                                        className={cn(
                                            "flex w-max max-w-[80%] flex-col gap-2 rounded-2xl px-5 py-3 text-sm shadow-sm",
                                            message.role === "user"
                                                ? "ml-auto bg-primary text-primary-foreground rounded-br-none"
                                                : "bg-muted/50 backdrop-blur-sm border border-border/50 rounded-bl-none"
                                        )}
                                    >
                                        <ReactMarkdown
                                            components={{
                                                code({ node, className, children, ...props }) {
                                                    const match = /language-(\w+)/.exec(className || "");
                                                    const isChart = match && match[1] === "chart";

                                                    if (isChart) {
                                                        try {
                                                            const config = JSON.parse(String(children).replace(/\n$/, ""));
                                                            return <ChartRenderer config={config} />;
                                                        } catch (e) {
                                                            return <code className={className} {...props}>{children}</code>;
                                                        }
                                                    }

                                                    return (
                                                        <code className={className} {...props}>
                                                            {children}
                                                        </code>
                                                    );
                                                },
                                                // Style tables
                                                table({ children }) {
                                                    return (
                                                        <div className="overflow-x-auto my-2">
                                                            <table className="min-w-full text-sm border-collapse">
                                                                {children}
                                                            </table>
                                                        </div>
                                                    );
                                                },
                                                th({ children }) {
                                                    return <th className="border-b border-border px-3 py-2 text-left font-semibold">{children}</th>;
                                                },
                                                td({ children }) {
                                                    return <td className="border-b border-border/50 px-3 py-2">{children}</td>;
                                                },
                                            }}
                                        >
                                            {message.content}
                                        </ReactMarkdown>
                                        {message.attachments && message.attachments.length > 0 && (
                                            <AttachmentView attachments={message.attachments} />
                                        )}
                                    </div>
                                </div>
                            ))}
                            {/* Streaming message */}
                            {isTyping && streamingMessage && (
                                <div className="flex gap-3">
                                    <Avatar className="h-8 w-8">
                                        <AvatarFallback>AI</AvatarFallback>
                                    </Avatar>
                                    <div className="bg-muted/50 backdrop-blur-sm border border-border/50 rounded-2xl rounded-bl-none px-5 py-3 text-sm">
                                        <p className="text-muted-foreground animate-pulse">{streamingMessage}</p>
                                    </div>
                                </div>
                            )}
                            {/* Typing indicator */}
                            {isTyping && !streamingMessage && (
                                <div className="flex gap-3">
                                    <Avatar className="h-8 w-8">
                                        <AvatarFallback>AI</AvatarFallback>
                                    </Avatar>
                                    <div className="bg-muted rounded-lg p-4">
                                        <div className="flex gap-1">
                                            <span className="animate-bounce">.</span>
                                            <span className="animate-bounce delay-100">.</span>
                                            <span className="animate-bounce delay-200">.</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={scrollRef} />
                        </div>
                    </ScrollArea>
                    <ChatInput
                        onSend={handleSend}
                        disabled={isTyping || !isConnected}
                        centered={false}
                        onNewChat={handleNewChat}
                    />
                </>
            )}
        </div>
    );
}
