"use client";

import { useRef, useEffect, useState } from "react";
import { Message, Attachment } from "@/lib/types";
import { ChatInput } from "./ChatInput";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import ReactMarkdown from "react-markdown";
import { ChartRenderer } from "./ChartRenderer";
import { AttachmentView } from "./AttachmentView";
import { cn } from "@/lib/utils";
import { useAppDispatch, useAppSelector } from "@/lib/hooks";
import { addMessage, setTyping, clearChat } from "@/lib/features/chatSlice";

import { NotificationAlert, NotificationType } from "./NotificationAlert";

export function ChatInterface() {
    const dispatch = useAppDispatch();
    const { messages, isTyping } = useAppSelector((state) => state.chat);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [notification, setNotification] = useState<{ message: string; type: NotificationType; isVisible: boolean }>({
        message: "",
        type: "info",
        isVisible: false,
    });

    const showNotification = (message: string, type: NotificationType = "info") => {
        setNotification({ message, type, isVisible: true });
    };

    const handleNewChat = () => {
        dispatch(clearChat());
        showNotification("New chat session started", "success");
    };

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isTyping]);

    const handleSend = async (content: string, files: File[]) => {
        if (!content.trim() && files.length === 0) return;

        // Convert files to attachments (mock upload)
        const newAttachments: Attachment[] = files.map(file => ({
            id: Math.random().toString(36).substring(7),
            name: file.name,
            type: file.type.startsWith('image/') ? 'image' : 'file',
            url: URL.createObjectURL(file), // In real app, this would be a cloud URL
            size: file.size
        }));

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content,
            timestamp: new Date(),
            attachments: newAttachments.length > 0 ? newAttachments : undefined
        };
        dispatch(addMessage(userMessage));
        dispatch(setTyping(true));

        // Simulate AI response
        setTimeout(() => {
            const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "I received your message! This is a simulated response.",
                timestamp: new Date(),
            };
            dispatch(addMessage(aiMessage));
            dispatch(setTyping(false));
        }, 1500);
    };

    const isEmpty = messages.length === 0;

    const suggestions = [
        { label: "Analyze my spending", icon: "📊" },
        { label: "Show recent transactions", icon: "💳" },
        { label: "Set a monthly budget", icon: "💰" },
        { label: "How much did I save?", icon: "📈" },
    ];

    return (
        <div className="flex flex-col h-full relative">
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
                    </div>

                    <div className="w-full max-w-2xl">
                        <ChatInput onSend={handleSend} disabled={isTyping} centered={true} />

                        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3 px-4">
                            {suggestions.map((suggestion) => (
                                <button
                                    key={suggestion.label}
                                    onClick={() => handleSend(suggestion.label, [])}
                                    className="flex flex-col items-center gap-2 p-4 rounded-xl bg-muted/30 hover:bg-muted/50 border border-border/50 hover:border-primary/20 transition-all duration-300 group"
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
                            {isTyping && (
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
                    <ChatInput onSend={handleSend} disabled={isTyping} centered={false} onNewChat={handleNewChat} />
                </>
            )}
        </div>
    );
}

// Helper to generate mock responses with charts
function generateMockResponse(input: string): string {
    const lower = input.toLowerCase();
    if (lower.includes('spend') || lower.includes('expense')) {
        return `Here is your spending breakdown for this month:
\`\`\`chart
{
  "type": "pie",
  "title": "Spending by Category",
  "data": [
    { "name": "Food", "value": 400 },
    { "name": "Transport", "value": 300 },
    { "name": "Shopping", "value": 300 },
    { "name": "Bills", "value": 200 }
  ],
  "colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]
}
\`\`\`
You've spent the most on Food.`;
    }
    if (lower.includes('trend') || lower.includes('history')) {
        return `Here is your spending trend over the last 6 months:
\`\`\`chart
{
  "type": "bar",
  "title": "Monthly Spending",
  "data": [
    { "name": "Jul", "value": 2400 },
    { "name": "Aug", "value": 1398 },
    { "name": "Sep", "value": 9800 },
    { "name": "Oct", "value": 3908 },
    { "name": "Nov", "value": 4800 },
    { "name": "Dec", "value": 3800 }
  ],
  "colors": ["#8884d8"]
}
\`\`\`
September was a heavy month!`;
    }
    return "I can help you track your expenses, set goals, and analyze your spending habits. Try asking 'Show me my spending'.";
}
