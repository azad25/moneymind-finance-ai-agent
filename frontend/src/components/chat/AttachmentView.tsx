"use client";

import { FileIcon } from "lucide-react";
import { Attachment } from "@/lib/types";

interface AttachmentViewProps {
    attachments: Attachment[];
}

export function AttachmentView({ attachments }: AttachmentViewProps) {
    if (!attachments || attachments.length === 0) return null;

    return (
        <div className="flex flex-wrap gap-2 mt-2">
            {attachments.map((att) => (
                <div key={att.id} className="border rounded-lg overflow-hidden bg-background/50">
                    {att.type === 'image' ? (
                        <img
                            src={att.url}
                            alt={att.name}
                            className="max-w-[200px] max-h-[200px] object-cover"
                        />
                    ) : (
                        <div className="flex items-center gap-2 p-3">
                            <FileIcon className="h-8 w-8 text-muted-foreground" />
                            <div className="flex flex-col">
                                <span className="text-sm font-medium truncate max-w-[150px]">{att.name}</span>
                                {att.size && (
                                    <span className="text-xs text-muted-foreground">
                                        {(att.size / 1024).toFixed(1)} KB
                                    </span>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
