"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Paperclip, Plus } from "lucide-react";
import { useState, useRef } from "react";
import { FilePreview } from "./FilePreview";
import { cn } from "@/lib/utils";

interface ChatInputProps {
    onSend: (message: string, files: File[]) => void;
    disabled?: boolean;
    centered?: boolean;
    onNewChat?: () => void;
}

export function ChatInput({ onSend, disabled, centered = false, onNewChat }: ChatInputProps) {
    const [input, setInput] = useState("");
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleSend = () => {
        if (input.trim() || selectedFiles.length > 0) {
            onSend(input, selectedFiles);
            setInput("");
            setSelectedFiles([]);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setSelectedFiles(prev => [...prev, ...Array.from(e.target.files!)]);
        }
    };

    const removeFile = (index: number) => {
        setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    };

    return (
        <div className={cn(
            "px-4 pointer-events-none transition-all duration-500 ease-in-out z-10",
            centered
                ? "relative w-full"
                : "absolute bottom-6 left-0 right-0"
        )}>
            <div className={cn(
                "max-w-3xl mx-auto flex gap-2 items-center bg-background/95 backdrop-blur-xl p-2 pl-4 rounded-[24px] border border-border/40 shadow-lg pointer-events-auto transition-all duration-300 focus-within:shadow-xl focus-within:border-primary/20",
                centered && "shadow-2xl border-border/60"
            )}>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-full hover:bg-muted text-muted-foreground shrink-0"
                    onClick={() => onNewChat?.()}
                    disabled={disabled || centered}
                    title="New Chat"
                >
                    <Plus className="h-4 w-4" />
                    <span className="sr-only">New Chat</span>
                </Button>

                <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-full hover:bg-muted text-muted-foreground shrink-0"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={disabled}
                >
                    <Paperclip className="h-4 w-4" />
                    <span className="sr-only">Attach file</span>
                </Button>

                <div className="flex-1 min-w-0">
                    {selectedFiles.length > 0 && (
                        <div className="flex gap-2 mb-2 overflow-x-auto py-1 px-1">
                            <FilePreview
                                files={selectedFiles}
                                onRemove={removeFile}
                            />
                        </div>
                    )}
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={centered ? "Ask anything..." : "Message MoneyMind..."}
                        disabled={disabled}
                        className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 px-0 py-2 h-auto text-base placeholder:text-muted-foreground/40 shadow-none"
                    />
                </div>

                <Button
                    onClick={handleSend}
                    disabled={disabled || (!input.trim() && selectedFiles.length === 0)}
                    size="icon"
                    className={cn(
                        "h-8 w-8 rounded-full transition-all duration-300 shrink-0",
                        input.trim() || selectedFiles.length > 0
                            ? "bg-primary text-primary-foreground hover:bg-primary/90"
                            : "bg-muted text-muted-foreground hover:bg-muted/80"
                    )}
                >
                    <Send className="h-4 w-4" />
                    <span className="sr-only">Send message</span>
                </Button>
            </div>
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                className="hidden"
                multiple
            />
        </div>
    );
}
