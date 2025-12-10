/**
 * MoneyMind Route Guard
 * Client-side route protection with loading states
 */
'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { useAuthContext } from './AuthProvider';
import { Loader2 } from 'lucide-react';

const publicRoutes = ['/login', '/signup'];

function RouteGuardInner({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const { isAuthenticated, isLoading } = useAuthContext();
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {
        const checkAuth = () => {
            const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

            // If still loading, don't make any decisions yet
            if (isLoading) {
                setAuthorized(false);
                return;
            }

            // If on a public route
            if (isPublicRoute) {
                // If authenticated, redirect to dashboard or redirect param
                if (isAuthenticated) {
                    const redirect = searchParams.get('redirect');
                    router.push(redirect || '/');
                } else {
                    setAuthorized(true);
                }
                return;
            }

            // Protected route
            if (!isAuthenticated) {
                // Not authenticated, redirect to login
                const loginUrl = `/login?redirect=${encodeURIComponent(pathname)}`;
                router.push(loginUrl);
                setAuthorized(false);
            } else {
                // Authenticated, allow access
                setAuthorized(true);
            }
        };

        checkAuth();
    }, [isAuthenticated, isLoading, pathname, router, searchParams]);

    // Show loading spinner while checking authentication
    if (isLoading || !authorized) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-16 w-16 bg-gradient-to-br from-primary to-blue-600 rounded-2xl shadow-2xl shadow-primary/20 flex items-center justify-center">
                        <span className="text-3xl font-bold text-white">M</span>
                    </div>
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Loading...</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}

export function RouteGuard({ children }: { children: React.ReactNode }) {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center min-h-screen bg-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-16 w-16 bg-gradient-to-br from-primary to-blue-600 rounded-2xl shadow-2xl shadow-primary/20 flex items-center justify-center">
                        <span className="text-3xl font-bold text-white">M</span>
                    </div>
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Loading...</p>
                </div>
            </div>
        }>
            <RouteGuardInner>{children}</RouteGuardInner>
        </Suspense>
    );
}
