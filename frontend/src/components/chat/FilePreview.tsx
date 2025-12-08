"use client";

import { X, FileIcon, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Attachment } from "@/lib/types";

interface FilePreviewProps {
    files: File[];
    onRemove: (index: number) => void;
}

export function FilePreview({ files, onRemove }: FilePreviewProps) {
    if (files.length === 0) return null;

    return (
        <div className="flex gap-2 p-2 overflow-x-auto">
            {files.map((file, index) => (
                <div key={index} className="relative group flex-shrink-0">
                    <div className="w-16 h-16 border rounded-lg flex items-center justify-center bg-muted overflow-hidden">
                        {file.type.startsWith('image/') ? (
                            <img
                                src={URL.createObjectURL(file)}
                                alt={file.name}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <FileIcon className="h-8 w-8 text-muted-foreground" />
                        )}
                    </div>
                    <Button
                        variant="destructive"
                        size="icon"
                        className="absolute -top-1 -right-1 h-5 w-5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => onRemove(index)}
                    >
                        <X className="h-3 w-3" />
                    </Button>
                    <span className="text-[10px] truncate w-16 block mt-1 text-center text-muted-foreground">
                        {file.name}
                    </span>
                </div>
            ))}
        </div>
    );
}
