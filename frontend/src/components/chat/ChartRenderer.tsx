"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartData } from "@/lib/types";
import {
    Bar,
    BarChart,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface ChartRendererProps {
    config: ChartData;
}

export function ChartRenderer({ config }: ChartRendererProps) {
    const { type, title, data, colors, dataKey, nameKey, category } = config;

    const renderChart = () => {
        switch (type) {
            case "pie":
                return (
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                            ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                    </PieChart>
                );
            case "bar":
                return (
                    <BarChart data={data}>
                        <XAxis dataKey={category || "name"} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey={dataKey || "value"} fill={colors[0]} radius={[4, 4, 0, 0]} />
                    </BarChart>
                );
            case "line":
                return (
                    <LineChart data={data}>
                        <XAxis dataKey={category || "name"} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey={dataKey || "value"}
                            stroke={colors[0]}
                            strokeWidth={2}
                        />
                    </LineChart>
                );
            default:
                return <div>Unsupported chart type</div>;
        }
    };

    return (
        <Card className="w-full max-w-md mx-auto my-4">
            <CardHeader>
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                    {renderChart()}
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
