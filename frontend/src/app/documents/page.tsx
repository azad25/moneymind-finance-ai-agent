"use client";

import { useState, useRef, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Upload, FileText, File, Image, Trash2, Search, Filter, Eye } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/components/ui/use-toast";
import { documentsApi, Document } from "@/lib/api/client";

export default function DocumentsPage() {
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
    const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);

    // Load documents on mount
    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        setIsLoading(true);
        try {
            const response = await documentsApi.list();
            if (response.data) {
                setDocuments(response.data.documents || []);
            } else if (response.error) {
                toast({
                    title: "Failed to load documents",
                    description: response.error,
                    variant: "destructive",
                });
            }
        } catch (error: any) {
            toast({
                title: "Error",
                description: error.message || "Failed to load documents",
                variant: "destructive",
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        const file = files[0];
        
        // Validate file type
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain',
            'text/csv',
        ];

        if (!allowedTypes.includes(file.type)) {
            toast({
                title: "Invalid file type",
                description: "Please upload PDF, DOCX, Excel, CSV, or TXT files only.",
                variant: "destructive",
            });
            return;
        }

        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            toast({
                title: "File too large",
                description: "Maximum file size is 10MB.",
                variant: "destructive",
            });
            return;
        }

        await uploadDocument(file);
    };

    const uploadDocument = async (file: File) => {
        setIsUploading(true);
        setUploadProgress(0);

        try {
            // Simulate progress
            const progressInterval = setInterval(() => {
                setUploadProgress(prev => Math.min(prev + 10, 90));
            }, 200);

            const response = await documentsApi.upload(file, `Uploaded ${file.name}`);

            clearInterval(progressInterval);
            setUploadProgress(100);

            if (response.error) {
                throw new Error(response.error);
            }

            toast({
                title: "Upload successful",
                description: `${file.name} has been uploaded and processed.`,
            });

            // Reload documents list
            await loadDocuments();

        } catch (error: any) {
            toast({
                title: "Upload failed",
                description: error.message || "Failed to upload document",
                variant: "destructive",
            });
        } finally {
            setIsUploading(false);
            setUploadProgress(0);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleDelete = async (id: string) => {
        try {
            const response = await documentsApi.delete(id);
            
            if (response.error) {
                throw new Error(response.error);
            }

            setDocuments(documents.filter(doc => doc.id !== id));
            toast({
                title: "Document deleted",
                description: "The document has been removed.",
            });
        } catch (error: any) {
            toast({
                title: "Delete failed",
                description: error.message || "Failed to delete document",
                variant: "destructive",
            });
        }
    };

    const getFileIcon = (contentType: string) => {
        if (contentType.includes('pdf')) return <FileText className="h-5 w-5 text-red-500" />;
        if (contentType.includes('word')) return <FileText className="h-5 w-5 text-blue-500" />;
        if (contentType.includes('excel') || contentType.includes('spreadsheet')) return <FileText className="h-5 w-5 text-green-500" />;
        if (contentType.includes('image')) return <Image className="h-5 w-5 text-purple-500" />;
        return <File className="h-5 w-5 text-gray-500" />;
    };

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const getFileExtension = (filename: string) => {
        return filename.split('.').pop()?.toUpperCase() || 'FILE';
    };

    const filteredDocuments = documents.filter(doc =>
        doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold">Documents</h1>
                        <p className="text-muted-foreground">Upload and manage your financial documents</p>
                    </div>
                    <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Document
                    </Button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        onChange={handleFileSelect}
                        accept=".pdf,.docx,.xlsx,.xls,.csv,.txt"
                    />
                </div>

                {/* Upload Progress */}
                {isUploading && (
                    <Card>
                        <CardContent className="pt-6">
                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-sm">
                                    <span>Uploading and processing...</span>
                                    <span>{uploadProgress}%</span>
                                </div>
                                <Progress value={uploadProgress} />
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Search and Filter */}
                <div className="flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search documents..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10"
                        />
                    </div>
                    <Button variant="outline">
                        <Filter className="mr-2 h-4 w-4" />
                        Filter
                    </Button>
                </div>

                {/* Documents Grid */}
                {filteredDocuments.length > 0 ? (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {filteredDocuments.map((doc) => (
                            <Card key={doc.id} className="hover:shadow-lg transition-shadow">
                                <CardHeader className="pb-3">
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 rounded-lg bg-muted">
                                                {getFileIcon(doc.content_type)}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <CardTitle className="text-sm truncate">{doc.filename}</CardTitle>
                                                <CardDescription className="text-xs">
                                                    {formatFileSize(doc.file_size)}
                                                </CardDescription>
                                            </div>
                                        </div>
                                        <Badge variant={doc.status === 'ready' ? 'default' : doc.status === 'processing' ? 'secondary' : 'destructive'}>
                                            {doc.status}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                                            <span>{getFileExtension(doc.filename)}</span>
                                            <span>{doc.chunk_count} chunks</span>
                                        </div>
                                        <div className="text-xs text-muted-foreground">
                                            Uploaded {new Date(doc.created_at).toLocaleDateString()}
                                        </div>
                                        <div className="flex gap-2 pt-2 border-t">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="flex-1"
                                                onClick={() => {
                                                    setSelectedDoc(doc);
                                                    setIsViewDialogOpen(true);
                                                }}
                                            >
                                                <Eye className="mr-2 h-3 w-3" />
                                                View
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="text-red-600 hover:text-red-700"
                                                onClick={() => handleDelete(doc.id)}
                                            >
                                                <Trash2 className="h-3 w-3" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <Card className="p-12">
                        <div className="text-center space-y-4">
                            <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
                            <div>
                                <h3 className="text-lg font-semibold">No documents yet</h3>
                                <p className="text-sm text-muted-foreground">
                                    Upload your first document to get started
                                </p>
                                <p className="text-xs text-muted-foreground mt-2">
                                    Supported formats: PDF, DOCX, Excel, CSV, TXT
                                </p>
                            </div>
                            <Button onClick={() => fileInputRef.current?.click()}>
                                <Upload className="mr-2 h-4 w-4" />
                                Upload Document
                            </Button>
                        </div>
                    </Card>
                )}

                {/* View Dialog */}
                <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
                    <DialogContent className="max-w-2xl">
                        <DialogHeader>
                            <DialogTitle>{selectedDoc?.filename}</DialogTitle>
                            <DialogDescription>
                                Document details and information
                            </DialogDescription>
                        </DialogHeader>
                        {selectedDoc && (
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm font-medium">File Type</p>
                                        <p className="text-sm text-muted-foreground">{getFileExtension(selectedDoc.filename)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">Size</p>
                                        <p className="text-sm text-muted-foreground">{formatFileSize(selectedDoc.file_size)}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">Status</p>
                                        <Badge variant={selectedDoc.status === 'ready' ? 'default' : 'secondary'}>
                                            {selectedDoc.status}
                                        </Badge>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">Chunks</p>
                                        <p className="text-sm text-muted-foreground">{selectedDoc.chunk_count} text chunks</p>
                                    </div>
                                    <div className="col-span-2">
                                        <p className="text-sm font-medium">Uploaded</p>
                                        <p className="text-sm text-muted-foreground">
                                            {new Date(selectedDoc.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                                <div className="pt-4 border-t">
                                    <p className="text-sm text-muted-foreground">
                                        This document has been processed and indexed for semantic search. 
                                        You can ask the AI assistant questions about this document in the chat.
                                    </p>
                                </div>
                            </div>
                        )}
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
                                Close
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </DashboardLayout>
    );
}
