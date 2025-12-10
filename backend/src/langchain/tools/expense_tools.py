"""
Expense Management Tools - REAL IMPLEMENTATION
LangChain tools with actual database operations
"""
from typing import Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from langchain_core.tools import tool
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session():
    """Get database session."""
    from src.infrastructure.database.postgres import async_session_factory
    async with async_session_factory() as session:
        return session


@tool
async def create_expense(
    amount: float,
    merchant: str,
    category: str,
    expense_date: Optional[str] = None,
    currency: str = "USD",
    description: Optional[str] = None,
) -> str:
    """
    Create a new expense entry in the database.
    
    Args:
        amount: The expense amount (positive number)
        merchant: Name of the merchant/vendor
        category: Expense category (food, transport, shopping, bills, entertainment, etc.)
        expense_date: Date of expense (YYYY-MM-DD format), defaults to today
        currency: Currency code (USD, EUR, THB, etc.), defaults to USD
        description: Optional description of the expense
    
    Returns:
        Confirmation message with expense details
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.expense import Expense
    
    # Parse date
    if expense_date:
        try:
            exp_date = datetime.strptime(expense_date, "%Y-%m-%d").date()
        except ValueError:
            exp_date = date.today()
    else:
        exp_date = date.today()
    
    try:
        async with async_session_factory() as session:
            expense = Expense(
                id=str(uuid.uuid4()),
                user_id="default_user",  # TODO: Get from context
                amount=Decimal(str(amount)),
                currency=currency.upper(),
                category=category.lower(),
                merchant=merchant,
                description=description,
                expense_date=exp_date,
                source="chat",
            )
            
            session.add(expense)
            await session.commit()
            
            return (
                f"✅ **Expense Created**\n\n"
                f"**Amount:** {amount:,.2f} {currency.upper()}\n"
                f"**Merchant:** {merchant}\n"
                f"**Category:** {category}\n"
                f"**Date:** {exp_date.strftime('%B %d, %Y')}\n"
                f"**ID:** {expense.id[:8]}..."
            )
            
    except Exception as e:
        return f"❌ Failed to create expense: {str(e)}"


@tool
async def list_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    List expenses with optional filters.
    
    Args:
        start_date: Filter expenses from this date (YYYY-MM-DD)
        end_date: Filter expenses until this date (YYYY-MM-DD)
        category: Filter by category (food, transport, shopping, etc.)
        limit: Maximum number of expenses to return (default: 10)
    
    Returns:
        List of expenses as formatted markdown table
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.expense import Expense
    
    try:
        async with async_session_factory() as session:
            query = select(Expense).where(Expense.user_id == "default_user")
            
            # Apply filters
            if start_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d").date()
                    query = query.where(Expense.expense_date >= start)
                except ValueError:
                    pass
            
            if end_date:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                    query = query.where(Expense.expense_date <= end)
                except ValueError:
                    pass
            
            if category:
                query = query.where(Expense.category == category.lower())
            
            query = query.order_by(Expense.expense_date.desc()).limit(limit)
            
            result = await session.execute(query)
            expenses = result.scalars().all()
            
            if not expenses:
                return "📋 No expenses found matching your criteria."
            
            # Calculate total
            total = sum(float(e.amount) for e in expenses)
            
            # Format as table
            output = "📋 **Your Expenses**\n\n"
            output += "| Date | Merchant | Category | Amount |\n"
            output += "|------|----------|----------|--------|\n"
            
            for exp in expenses:
                date_str = exp.expense_date.strftime("%b %d")
                output += f"| {date_str} | {exp.merchant} | {exp.category} | {float(exp.amount):,.2f} {exp.currency} |\n"
            
            output += f"\n**Total:** {total:,.2f} ({len(expenses)} expenses)"
            
            return output
            
    except Exception as e:
        return f"❌ Error listing expenses: {str(e)}"


@tool
async def get_spending_by_category(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> str:
    """
    Get spending breakdown by category.
    
    Args:
        start_date: Start date (YYYY-MM-DD), defaults to start of current month
        end_date: End date (YYYY-MM-DD), defaults to today
    
    Returns:
        Spending summary by category with totals
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.expense import Expense
    
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
            query = select(
                Expense.category,
                func.sum(Expense.amount).label("total"),
                func.count(Expense.id).label("count")
            ).where(
                Expense.user_id == "default_user",
                Expense.expense_date >= start,
                Expense.expense_date <= end,
            ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc())
            
            result = await session.execute(query)
            categories = result.all()
            
            if not categories:
                return f"📊 No spending data found for {start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
            
            # Calculate grand total
            grand_total = sum(float(c.total) for c in categories)
            
            # Format output
            output = f"📊 **Spending by Category**\n"
            output += f"*{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}*\n\n"
            
            for cat in categories:
                percentage = (float(cat.total) / grand_total * 100) if grand_total > 0 else 0
                bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
                output += f"**{cat.category.title()}**: {float(cat.total):,.2f} ({percentage:.1f}%)\n"
                output += f"`{bar}`\n\n"
            
            output += f"**Total Spending:** {grand_total:,.2f}"
            
            return output
            
    except Exception as e:
        return f"❌ Error getting spending breakdown: {str(e)}"


@tool
async def create_subscription(
    name: str,
    amount: float,
    billing_cycle: str,
    next_billing_date: str,
    currency: str = "USD",
    category: Optional[str] = None,
) -> str:
    """
    Create a recurring subscription.
    
    Args:
        name: Subscription name (Netflix, Spotify, Gym, etc.)
        amount: Billing amount per cycle
        billing_cycle: Frequency (daily, weekly, monthly, yearly)
        next_billing_date: Next charge date (YYYY-MM-DD)
        currency: Currency code (default: USD)
        category: Optional category
    
    Returns:
        Confirmation message
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.subscription import Subscription
    
    # Validate billing cycle
    valid_cycles = ["daily", "weekly", "monthly", "yearly"]
    if billing_cycle.lower() not in valid_cycles:
        return f"❌ Invalid billing cycle. Use one of: {', '.join(valid_cycles)}"
    
    # Parse date
    try:
        next_date = datetime.strptime(next_billing_date, "%Y-%m-%d").date()
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."
    
    try:
        async with async_session_factory() as session:
            subscription = Subscription(
                id=str(uuid.uuid4()),
                user_id="default_user",
                name=name,
                amount=Decimal(str(amount)),
                currency=currency.upper(),
                billing_cycle=billing_cycle.lower(),
                next_billing_date=next_date,
                category=category,
                is_active=True,
            )
            
            session.add(subscription)
            await session.commit()
            
            return (
                f"✅ **Subscription Created**\n\n"
                f"**Name:** {name}\n"
                f"**Amount:** {amount:,.2f} {currency.upper()}/{billing_cycle}\n"
                f"**Next Billing:** {next_date.strftime('%B %d, %Y')}"
            )
            
    except Exception as e:
        return f"❌ Failed to create subscription: {str(e)}"


@tool
async def list_subscriptions() -> str:
    """
    List all active subscriptions.
    
    Returns:
        List of subscriptions with amounts and billing dates
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.subscription import Subscription
    
    try:
        async with async_session_factory() as session:
            query = select(Subscription).where(
                Subscription.user_id == "default_user",
                Subscription.is_active == True,
            ).order_by(Subscription.next_billing_date)
            
            result = await session.execute(query)
            subscriptions = result.scalars().all()
            
            if not subscriptions:
                return "📋 No active subscriptions found."
            
            # Calculate monthly total
            monthly_total = 0
            for sub in subscriptions:
                amount = float(sub.amount)
                if sub.billing_cycle == "yearly":
                    monthly_total += amount / 12
                elif sub.billing_cycle == "weekly":
                    monthly_total += amount * 4.33
                elif sub.billing_cycle == "daily":
                    monthly_total += amount * 30
                else:
                    monthly_total += amount
            
            output = "📋 **Active Subscriptions**\n\n"
            output += "| Name | Amount | Cycle | Next Billing |\n"
            output += "|------|--------|-------|-------------|\n"
            
            for sub in subscriptions:
                next_date = sub.next_billing_date.strftime("%b %d")
                output += f"| {sub.name} | {float(sub.amount):,.2f} {sub.currency} | {sub.billing_cycle} | {next_date} |\n"
            
            output += f"\n**Estimated Monthly Total:** {monthly_total:,.2f}"
            
            return output
            
    except Exception as e:
        return f"❌ Error listing subscriptions: {str(e)}"


@tool
async def create_bill(
    name: str,
    amount: float,
    due_date: str,
    is_recurring: bool = False,
    currency: str = "USD",
) -> str:
    """
    Create a bill/payment reminder.
    
    Args:
        name: Bill name (Rent, Electric, Internet, etc.)
        amount: Bill amount
        due_date: Due date (YYYY-MM-DD)
        is_recurring: Whether the bill repeats monthly
        currency: Currency code (default: USD)
    
    Returns:
        Confirmation message
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.bill import Bill
    
    try:
        bill_date = datetime.strptime(due_date, "%Y-%m-%d").date()
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."
    
    try:
        async with async_session_factory() as session:
            bill = Bill(
                id=str(uuid.uuid4()),
                user_id="default_user",
                name=name,
                amount=Decimal(str(amount)),
                currency=currency.upper(),
                due_date=bill_date,
                is_recurring=is_recurring,
                is_paid=False,
            )
            
            session.add(bill)
            await session.commit()
            
            recurring_text = " (recurring monthly)" if is_recurring else ""
            return (
                f"✅ **Bill Created**\n\n"
                f"**Name:** {name}\n"
                f"**Amount:** {amount:,.2f} {currency.upper()}\n"
                f"**Due Date:** {bill_date.strftime('%B %d, %Y')}{recurring_text}"
            )
            
    except Exception as e:
        return f"❌ Failed to create bill: {str(e)}"


@tool
async def list_upcoming_bills(days: int = 30) -> str:
    """
    List bills due in the next N days.
    
    Args:
        days: Number of days to look ahead (default: 30)
    
    Returns:
        List of upcoming bills with due dates
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.bill import Bill
    
    try:
        async with async_session_factory() as session:
            today = date.today()
            end_date = today + timedelta(days=days)
            
            query = select(Bill).where(
                Bill.user_id == "default_user",
                Bill.is_paid == False,
                Bill.due_date >= today,
                Bill.due_date <= end_date,
            ).order_by(Bill.due_date)
            
            result = await session.execute(query)
            bills = result.scalars().all()
            
            if not bills:
                return f"📋 No bills due in the next {days} days."
            
            total_due = sum(float(b.amount) for b in bills)
            
            output = f"📋 **Bills Due (Next {days} Days)**\n\n"
            output += "| Bill | Amount | Due Date | Status |\n"
            output += "|------|--------|----------|--------|\n"
            
            for bill in bills:
                days_until = (bill.due_date - today).days
                if days_until == 0:
                    status = "⚠️ Today"
                elif days_until <= 3:
                    status = "🔴 Soon"
                elif days_until <= 7:
                    status = "🟡 Coming"
                else:
                    status = "🟢 OK"
                
                output += f"| {bill.name} | {float(bill.amount):,.2f} {bill.currency} | {bill.due_date.strftime('%b %d')} | {status} |\n"
            
            output += f"\n**Total Due:** {total_due:,.2f}"
            
            return output
            
    except Exception as e:
        return f"❌ Error listing bills: {str(e)}"


@tool
async def create_goal(
    name: str,
    target_amount: float,
    deadline: str,
    currency: str = "USD",
    category: Optional[str] = None,
) -> str:
    """
    Create a financial savings goal.
    
    Args:
        name: Goal name (Vacation, Emergency Fund, New Car, etc.)
        target_amount: Target amount to save
        deadline: Target date to reach goal (YYYY-MM-DD)
        currency: Currency code (default: USD)
        category: Optional category
    
    Returns:
        Confirmation with savings plan
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.goal import Goal
    
    try:
        goal_deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    except ValueError:
        return "❌ Invalid date format. Use YYYY-MM-DD."
    
    # Calculate months until deadline
    today = date.today()
    months_left = (goal_deadline.year - today.year) * 12 + (goal_deadline.month - today.month)
    if months_left <= 0:
        return "❌ Deadline must be in the future."
    
    monthly_savings = target_amount / months_left
    
    try:
        async with async_session_factory() as session:
            goal = Goal(
                id=str(uuid.uuid4()),
                user_id="default_user",
                name=name,
                target_amount=Decimal(str(target_amount)),
                current_amount=Decimal("0"),
                currency=currency.upper(),
                deadline=goal_deadline,
                category=category,
            )
            
            session.add(goal)
            await session.commit()
            
            return (
                f"✅ **Goal Created**\n\n"
                f"**Name:** {name}\n"
                f"**Target:** {target_amount:,.2f} {currency.upper()}\n"
                f"**Deadline:** {goal_deadline.strftime('%B %d, %Y')}\n"
                f"**Time Left:** {months_left} months\n\n"
                f"💡 **Suggestion:** Save **{monthly_savings:,.2f} {currency}/month** to reach your goal!"
            )
            
    except Exception as e:
        return f"❌ Failed to create goal: {str(e)}"


@tool
async def list_goals() -> str:
    """
    List all financial goals with progress.
    
    Returns:
        List of goals with current progress
    """
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models.goal import Goal
    
    try:
        async with async_session_factory() as session:
            query = select(Goal).where(
                Goal.user_id == "default_user",
            ).order_by(Goal.deadline)
            
            result = await session.execute(query)
            goals = result.scalars().all()
            
            if not goals:
                return "📋 No financial goals set yet. Create one to start tracking!"
            
            output = "🎯 **Your Financial Goals**\n\n"
            
            for goal in goals:
                current = float(goal.current_amount)
                target = float(goal.target_amount)
                progress = (current / target * 100) if target > 0 else 0
                
                # Progress bar
                filled = int(progress / 5)
                bar = "█" * filled + "░" * (20 - filled)
                
                days_left = (goal.deadline - date.today()).days
                status = "✅ Complete" if progress >= 100 else f"{days_left} days left"
                
                output += f"**{goal.name}**\n"
                output += f"Progress: {current:,.2f} / {target:,.2f} {goal.currency} ({progress:.1f}%)\n"
                output += f"`{bar}`\n"
                output += f"Deadline: {goal.deadline.strftime('%B %d, %Y')} ({status})\n\n"
            
            return output
            
    except Exception as e:
        return f"❌ Error listing goals: {str(e)}"


# Export all expense tools
expense_tools = [
    create_expense,
    list_expenses,
    get_spending_by_category,
    create_subscription,
    list_subscriptions,
    create_bill,
    list_upcoming_bills,
    create_goal,
    list_goals,
]
