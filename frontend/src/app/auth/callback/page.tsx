'use client';

import { useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthContext } from '@/components/providers/AuthProvider';
import { Loader2 } from 'lucide-react';

function CallbackHandler() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { handleGoogleCallback } = useAuthContext();

    useEffect(() => {
        const processCallback = async () => {
            const result = await handleGoogleCallback(searchParams);
            
            if (result.success) {
                router.push('/');
            } else {
                router.push('/login?error=oauth_failed');
            }
        };

        processCallback();
    }, [searchParams, handleGoogleCallback, router]);

    return (
        <div className="flex items-center justify-center min-h-screen bg-background">
            <div className="flex flex-col items-center gap-4">
                <div className="h-16 w-16 bg-gradient-to-br from-primary to-blue-600 rounded-2xl shadow-2xl shadow-primary/20 flex items-center justify-center">
                    <span className="text-3xl font-bold text-white">M</span>
                </div>
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-sm text-muted-foreground">Completing sign in...</p>
            </div>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center min-h-screen">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        }>
            <CallbackHandler />
        </Suspense>
    );
}
