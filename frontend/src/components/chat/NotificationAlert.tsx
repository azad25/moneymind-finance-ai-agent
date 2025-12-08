import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, CheckCircle, Info, X } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

export type NotificationType = "info" | "success" | "warning" | "error";

interface NotificationAlertProps {
    message: string;
    type?: NotificationType;
    isVisible: boolean;
    onClose: () => void;
    duration?: number;
}

export function NotificationAlert({
    message,
    type = "info",
    isVisible,
    onClose,
    duration = 5000
}: NotificationAlertProps) {
    useEffect(() => {
        if (isVisible && duration > 0) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [isVisible, duration, onClose]);

    const icons = {
        info: <Info className="h-5 w-5 text-blue-500" />,
        success: <CheckCircle className="h-5 w-5 text-green-500" />,
        warning: <AlertCircle className="h-5 w-5 text-yellow-500" />,
        error: <AlertCircle className="h-5 w-5 text-red-500" />,
    };

    const styles = {
        info: "bg-blue-500/10 border-blue-500/20 text-blue-700 dark:text-blue-300",
        success: "bg-green-500/10 border-green-500/20 text-green-700 dark:text-green-300",
        warning: "bg-yellow-500/10 border-yellow-500/20 text-yellow-700 dark:text-yellow-300",
        error: "bg-red-500/10 border-red-500/20 text-red-700 dark:text-red-300",
    };

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ duration: 0.3, type: "spring", stiffness: 500, damping: 30 }}
                    className={cn(
                        "absolute top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg backdrop-blur-md min-w-[300px] max-w-md",
                        styles[type]
                    )}
                >
                    <div className="shrink-0">{icons[type]}</div>
                    <p className="flex-1 text-sm font-medium">{message}</p>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-full hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
                    >
                        <X className="h-4 w-4 opacity-70" />
                    </button>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
