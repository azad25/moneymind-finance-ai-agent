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
            "w-full transition-all duration-500 ease-in-out",
            centered ? "relative" : ""
        )}>
            <div className={cn(
                "flex gap-2 items-end bg-background p-2 rounded-[26px] border border-input shadow-sm transition-all duration-200 focus-within:shadow-md focus-within:border-primary/30 focus-within:ring-1 focus-within:ring-primary/20",
                centered ? "shadow-lg border-border/60 p-3" : ""
            )}>
                {!centered && (
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-9 w-9 rounded-full hover:bg-muted text-muted-foreground shrink-0 mb-0.5"
                        onClick={() => onNewChat?.()}
                        disabled={disabled}
                        title="New Chat"
                    >
                        <Plus className="h-5 w-5" />
                        <span className="sr-only">New Chat</span>
                    </Button>
                )}

                <Button
                    variant="ghost"
                    size="icon"
                    className="h-9 w-9 rounded-full hover:bg-muted text-muted-foreground shrink-0 mb-0.5"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={disabled}
                >
                    <Paperclip className="h-5 w-5" />
                    <span className="sr-only">Attach file</span>
                </Button>

                <div className="flex-1 min-w-0 py-1.5">
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
                        className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 px-2 py-0 h-auto text-base placeholder:text-muted-foreground/50 shadow-none min-h-[24px]"
                    />
                </div>

                <Button
                    onClick={handleSend}
                    disabled={disabled || (!input.trim() && selectedFiles.length === 0)}
                    size="icon"
                    className={cn(
                        "h-9 w-9 rounded-full transition-all duration-200 shrink-0 mb-0.5",
                        input.trim() || selectedFiles.length > 0
                            ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm"
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
