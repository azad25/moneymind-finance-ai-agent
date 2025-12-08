"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function SettingsPage() {
    const { theme, setTheme } = useTheme();

    return (
        <DashboardLayout>
            <div className="flex flex-col h-full bg-muted/10">
                <div className="border-b bg-background/50 backdrop-blur-xl p-6">
                    <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                    <p className="text-muted-foreground mt-1">Manage your account settings and preferences.</p>
                </div>

                <div className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-[250px_1fr] gap-8">
                    {/* Settings Sidebar */}
                    <nav className="space-y-1">
                        <Button variant="secondary" className="w-full justify-start font-medium bg-secondary/50">
                            General
                        </Button>
                        <Button variant="ghost" className="w-full justify-start font-medium text-muted-foreground hover:text-foreground">
                            Account
                        </Button>
                        <Button variant="ghost" className="w-full justify-start font-medium text-muted-foreground hover:text-foreground">
                            Appearance
                        </Button>
                        <Button variant="ghost" className="w-full justify-start font-medium text-muted-foreground hover:text-foreground">
                            Notifications
                        </Button>
                        <Button variant="ghost" className="w-full justify-start font-medium text-muted-foreground hover:text-foreground">
                            API Configuration
                        </Button>
                    </nav>

                    {/* Settings Content */}
                    <div className="space-y-6">
                        {/* Appearance Section */}
                        <Card className="border-border/50 shadow-sm">
                            <CardHeader>
                                <CardTitle>Appearance</CardTitle>
                                <CardDescription>Customize the look and feel of MoneyMind.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Theme</Label>
                                    <Select value={theme} onValueChange={setTheme}>
                                        <SelectTrigger className="w-[200px]">
                                            <SelectValue placeholder="Select theme" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="light">Light</SelectItem>
                                            <SelectItem value="dark">Dark</SelectItem>
                                            <SelectItem value="system">System</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Profile Section */}
                        <Card className="border-border/50 shadow-sm">
                            <CardHeader>
                                <CardTitle>Profile</CardTitle>
                                <CardDescription>Manage your personal information.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="firstName">First name</Label>
                                        <Input id="firstName" placeholder="John" />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="lastName">Last name</Label>
                                        <Input id="lastName" placeholder="Doe" />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email</Label>
                                    <Input id="email" type="email" placeholder="john@example.com" />
                                </div>
                                <div className="pt-2">
                                    <Button>Save Changes</Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* API Configuration Section */}
                        <Card className="border-border/50 shadow-sm">
                            <CardHeader>
                                <CardTitle>API Configuration</CardTitle>
                                <CardDescription>Manage your external service connections.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="stripeKey">Stripe API Key</Label>
                                    <Input id="stripeKey" type="password" placeholder="sk_test_..." className="font-mono" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="alphaVantageKey">Alpha Vantage API Key</Label>
                                    <Input id="alphaVantageKey" type="password" placeholder="Enter your Alpha Vantage key" className="font-mono" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="exchangeRateKey">Exchange Rate API Key</Label>
                                    <Input id="exchangeRateKey" type="password" placeholder="Enter your Exchange Rate API key" className="font-mono" />
                                </div>
                                <div className="pt-2">
                                    <Button variant="outline">Save API Keys</Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
