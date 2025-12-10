"""
Chart Generation Tool
LangChain tool for generating chart data for frontend rendering
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
import json


@tool
def generate_chart(
    chart_type: str,
    title: str,
    data: List[Dict[str, Any]],
    colors: List[str] = None,
) -> str:
    """
    Generate a chart for display in the chat interface.
    
    The chart will be rendered by the frontend using Recharts.
    Returns a markdown code block with chart configuration.
    
    Args:
        chart_type: Type of chart (pie, bar, line)
        title: Chart title
        data: List of data points, each with 'name' and 'value' keys
        colors: Optional list of hex colors for the chart
    
    Returns:
        Markdown code block with chart JSON configuration
    
    Example:
        generate_chart(
            chart_type="pie",
            title="Spending by Category",
            data=[
                {"name": "Food", "value": 400},
                {"name": "Transport", "value": 300},
            ],
            colors=["#0088FE", "#00C49F"]
        )
    """
    default_colors = [
        "#0088FE",  # Blue
        "#00C49F",  # Green
        "#FFBB28",  # Yellow
        "#FF8042",  # Orange
        "#8884d8",  # Purple
        "#82ca9d",  # Light green
        "#ffc658",  # Gold
        "#ff7c43",  # Coral
    ]
    
    chart_config = {
        "type": chart_type,
        "title": title,
        "data": data,
        "colors": colors or default_colors[:len(data)],
    }
    
    chart_json = json.dumps(chart_config, indent=2)
    return f"```chart\n{chart_json}\n```"


@tool
def generate_spending_pie_chart(
    category_data: Dict[str, float],
    title: str = "Spending by Category",
) -> str:
    """
    Generate a pie chart showing spending distribution by category.
    
    Args:
        category_data: Dictionary mapping category names to amounts
        title: Chart title
    
    Returns:
        Markdown chart block for pie chart
    """
    data = [{"name": k, "value": v} for k, v in category_data.items()]
    return generate_chart.invoke({
        "chart_type": "pie",
        "title": title,
        "data": data,
    })


@tool
def generate_monthly_trend_chart(
    monthly_data: Dict[str, float],
    title: str = "Monthly Spending Trend",
) -> str:
    """
    Generate a bar chart showing monthly spending trend.
    
    Args:
        monthly_data: Dictionary mapping month names to amounts
        title: Chart title
    
    Returns:
        Markdown chart block for bar chart
    """
    data = [{"name": k, "value": v} for k, v in monthly_data.items()]
    return generate_chart.invoke({
        "chart_type": "bar",
        "title": title,
        "data": data,
    })


# Export chart tool
chart_tool = generate_chart
