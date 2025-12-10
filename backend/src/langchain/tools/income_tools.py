"""
Income and Balance Tools - REAL IMPLEMENTATION
LangChain tools for income tracking and balance management
"""
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
import uuid

from langchain_core.tools import tool
from sqlalchemy import select, func


@tool
async def create_income(
    amount: float,
    source: str,
    income_date: Optional[str] = None,
    currency: str = "USD",
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Create a new income entry in the database.
    
    Args:
        amount: The income amount (positive number)
        source: Source of income (salary, freelance, investment, bonus, etc.)
        income_date: Date of income (YYYY-MM-DD format), defaults to today
        currency: Currency code (USD, EUR, THB, etc.), defaults to USD
        category: Optional category (wages, business, passive, etc.)
        description: Optional description
    
    Returns:
        Confirmation message with income details
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.income import Income
    
    # Parse date
    if income_date:
        try:
            inc_date = datetime.strptime(income_date, "%Y-%m-%d").date()
        except ValueError:
            inc_date = date.today()
    else:
        inc_date = date.today()
    
    try:
        async with async_session_factory() as session:
            income = Income(
                id=str(uuid.uuid4()),
                user_id="default_user",  # TODO: Get from context
                amount=Decimal(str(amount)),
                currency=currency.upper(),
                source=source,
                category=category,
                description=description,
                income_date=inc_date,
            )
            
            session.add(income)
            await session.commit()
            
            return (
                f"✅ **Income Added**\n\n"
                f"**Amount:** {amount:,.2f} {currency.upper()}\n"
                f"**Source:** {source}\n"
                f"**Date:** {inc_date.strftime('%B %d, %Y')}\n"
                f"**ID:** {income.id[:8]}...\n\n"
                f"💰 Your balance has been updated!"
            )
            
    except Exception as e:
        return f"❌ Failed to add income: {str(e)}"


@tool
async def list_income(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    List income records with optional filters.
    
    Args:
        start_date: Filter income from this date (YYYY-MM-DD)
        end_date: Filter income until this date (YYYY-MM-DD)
        limit: Maximum number of records to return (default: 10)
    
    Returns:
        List of income records as formatted markdown table
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.income import Income
    
    try:
        async with async_session_factory() as session:
            query = select(Income).where(Income.user_id == "default_user")
            
            # Apply filters
            if start_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d").date()
                    query = query.where(Income.income_date >= start)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                    query = query.where(Income.income_date <= end)
                except ValueError:
                    pass
            
            query = query.order_by(Income.income_date.desc()).limit(limit)
            
            result = await session.execute(query)
            income_records = result.scalars().all()
            
            if not income_records:
                return "📋 No income records found matching your criteria."
            
            # Calculate total
            total = sum(float(i.amount) for i in income_records)
            
            # Format as table
            output = "💰 **Your Income**\n\n"
            output += "| Date | Source | Amount |\n"
            output += "|------|--------|--------|\n"
            
            for inc in income_records:
                date_str = inc.income_date.strftime("%b %d")
                output += f"| {date_str} | {inc.source} | {float(inc.amount):,.2f} {inc.currency} |\n"
            
            output += f"\n**Total:** {total:,.2f} ({len(income_records)} records)"
            
            return output
            
    except Exception as e:
        return f"❌ Error listing income: {str(e)}"


@tool
async def get_balance() -> str:
    """
    Get current account balance (total income - total expenses).
    
    Returns:
        Current balance with breakdown of income and expenses
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Income, Expense
    
    try:
        async with async_session_factory() as session:
            # Calculate total income
            income_result = await session.execute(
                select(func.sum(Income.amount)).where(Income.user_id == "default_user")
            )
            total_income = income_result.scalar() or Decimal("0")
            
            # Calculate total expenses
            expense_result = await session.execute(
                select(func.sum(Expense.amount)).where(Expense.user_id == "default_user")
            )
            total_expenses = expense_result.scalar() or Decimal("0")
            
            # Calculate balance
            balance = total_income - total_expenses
            
            # Format output
            output = "💰 **Your Financial Summary**\n\n"
            output += f"**Total Income:** {float(total_income):,.2f} USD\n"
            output += f"**Total Expenses:** {float(total_expenses):,.2f} USD\n"
            output += f"**Current Balance:** {float(balance):,.2f} USD\n\n"
            
            if balance > 0:
                output += "✅ You're in the positive! Keep it up! 🎉"
            elif balance == 0:
                output += "⚖️ You're breaking even."
            else:
                output += "⚠️ You're spending more than you earn. Consider reviewing your expenses."
            
            return output
            
    except Exception as e:
        return f"❌ Error calculating balance: {str(e)}"


@tool
async def get_income_vs_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    Compare income vs expenses for a date range.
    
    Args:
        start_date: Start date (YYYY-MM-DD), defaults to start of current month
        end_date: End date (YYYY-MM-DD), defaults to today
    
    Returns:
        Comparison of income vs expenses with net amount
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Income, Expense
    
    # Default to current month
    if not start_date:
        today = date.today()
        start = date(today.year, today.month, 1)
    else:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            start = date.today().replace(day=1)
    
    if not end_date:
        end = date.today()
    else:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            end = date.today()
    
    try:
        async with async_session_factory() as session:
            # Get income for period
            income_result = await session.execute(
                select(func.sum(Income.amount)).where(
                    Income.user_id == "default_user",
                    Income.income_date >= start,
                    Income.income_date <= end,
                )
            )
            period_income = income_result.scalar() or Decimal("0")
            
            # Get expenses for period
            expense_result = await session.execute(
                select(func.sum(Expense.amount)).where(
                    Expense.user_id == "default_user",
                    Expense.expense_date >= start,
                    Expense.expense_date <= end,
                )
            )
            period_expenses = expense_result.scalar() or Decimal("0")
            
            # Calculate net
            net = period_income - period_expenses
            savings_rate = (net / period_income * 100) if period_income > 0 else 0
            
            # Format output
            output = f"📊 **Income vs Expenses**\n"
            output += f"*{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}*\n\n"
            
            output += f"**Income:** {float(period_income):,.2f} USD\n"
            output += f"**Expenses:** {float(period_expenses):,.2f} USD\n"
            output += f"**Net:** {float(net):,.2f} USD\n"
            output += f"**Savings Rate:** {float(savings_rate):.1f}%\n\n"
            
            if net > 0:
                output += f"✅ You saved {float(net):,.2f} USD this period!"
            elif net == 0:
                output += "⚖️ You broke even this period."
            else:
                output += f"⚠️ You overspent by {float(abs(net)):,.2f} USD this period."
            
            return output
            
    except Exception as e:
        return f"❌ Error comparing income vs expenses: {str(e)}"


@tool
async def get_monthly_summary() -> str:
    """
    Get a complete financial summary for the current month.
    
    Returns:
        Comprehensive monthly financial summary with income, expenses, and balance
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Income, Expense
    
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    try:
        async with async_session_factory() as session:
            # Get monthly income
            income_result = await session.execute(
                select(func.sum(Income.amount)).where(
                    Income.user_id == "default_user",
                    Income.income_date >= start_of_month,
                    Income.income_date <= today,
                )
            )
            monthly_income = income_result.scalar() or Decimal("0")
            
            # Get monthly expenses
            expense_result = await session.execute(
                select(func.sum(Expense.amount)).where(
                    Expense.user_id == "default_user",
                    Expense.expense_date >= start_of_month,
                    Expense.expense_date <= today,
                )
            )
            monthly_expenses = expense_result.scalar() or Decimal("0")
            
            # Get expense breakdown by category
            category_result = await session.execute(
                select(
                    Expense.category,
                    func.sum(Expense.amount).label("total")
                ).where(
                    Expense.user_id == "default_user",
                    Expense.expense_date >= start_of_month,
                    Expense.expense_date <= today,
                ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).limit(5)
            )
            top_categories = category_result.all()
            
            # Calculate net
            net = monthly_income - monthly_expenses
            
            # Format output
            output = f"📊 **Monthly Financial Summary**\n"
            output += f"*{start_of_month.strftime('%B %Y')}*\n\n"
            
            output += f"💰 **Income:** {float(monthly_income):,.2f} USD\n"
            output += f"💸 **Expenses:** {float(monthly_expenses):,.2f} USD\n"
            output += f"💵 **Net:** {float(net):,.2f} USD\n\n"
            
            if top_categories:
                output += "**Top Spending Categories:**\n"
                for cat in top_categories:
                    percentage = (float(cat.total) / float(monthly_expenses) * 100) if monthly_expenses > 0 else 0
                    output += f"• {cat.category.title()}: {float(cat.total):,.2f} ({percentage:.1f}%)\n"
            
            return output
            
    except Exception as e:
        return f"❌ Error generating monthly summary: {str(e)}"


# Export all income and balance tools
income_tools = [
    create_income,
    list_income,
    get_balance,
    get_income_vs_expenses,
    get_monthly_summary,
]
