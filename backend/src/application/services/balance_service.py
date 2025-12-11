"""
Balance Service - Single Source of Truth
Centralized balance calculation with Redis caching
"""
from decimal import Decimal
from typing import Dict, Optional
from datetime import date, datetime
import json

from sqlalchemy import select, func

from src.infrastructure.database.postgres import async_session_factory
from src.infrastructure.database.redis_client import redis_client
from src.domain.models import Income, Expense


class BalanceService:
    """
    Centralized balance calculation service.
    
    This is the ONLY place where balance should be calculated.
    All tools and API endpoints must use this service.
    """
    
    CACHE_TTL = 60  # 1 minute cache
    
    @staticmethod
    async def get_balance(
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Get balance with optional date range filtering.
        
        Args:
            user_id: User identifier
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            use_cache: Whether to use Redis cache (default: True)
        
        Returns:
            Dictionary with balance, income, expenses, and metadata
        """
        # Generate cache key
        cache_key = f"balance:{user_id}"
        if start_date:
            cache_key += f":{start_date.isoformat()}"
        if end_date:
            cache_key += f":{end_date.isoformat()}"
        
        # Try cache first
        if use_cache:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    # Parse cached JSON
                    if isinstance(cached, str):
                        return json.loads(cached)
                    return cached
            except Exception:
                pass  # Cache miss or error, continue to database
        
        # Calculate from database
        async with async_session_factory() as session:
            # Build income query
            income_query = select(func.sum(Income.amount)).where(
                Income.user_id == user_id
            )
            if start_date:
                income_query = income_query.where(Income.income_date >= start_date)
            if end_date:
                income_query = income_query.where(Income.income_date <= end_date)
            
            income_result = await session.execute(income_query)
            total_income = income_result.scalar() or Decimal("0")
            
            # Build expense query
            expense_query = select(func.sum(Expense.amount)).where(
                Expense.user_id == user_id
            )
            if start_date:
                expense_query = expense_query.where(Expense.expense_date >= start_date)
            if end_date:
                expense_query = expense_query.where(Expense.expense_date <= end_date)
            
            expense_result = await session.execute(expense_query)
            total_expenses = expense_result.scalar() or Decimal("0")
            
            # Calculate balance
            balance = total_income - total_expenses
            
            # Build result
            result = {
                "balance": float(balance),
                "total_income": float(total_income),
                "total_expenses": float(total_expenses),
                "currency": "USD",
                "calculated_at": datetime.utcnow().isoformat(),
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "cached": False,
            }
            
            # Cache result
            if use_cache:
                try:
                    await redis_client.set(
                        cache_key,
                        json.dumps(result),
                        ex=BalanceService.CACHE_TTL
                    )
                except Exception:
                    pass  # Cache write failed, but we have the result
            
            return result
    
    @staticmethod
    async def invalidate_cache(user_id: str):
        """
        Invalidate all balance caches for a user.
        
        Call this after creating/updating/deleting income or expenses.
        """
        try:
            # Delete all keys matching pattern
            pattern = f"balance:{user_id}*"
            await redis_client.delete_pattern(pattern)
        except Exception:
            pass  # Cache invalidation failed, but not critical
    
    @staticmethod
    async def get_monthly_balance(user_id: str, year: int, month: int) -> Dict:
        """
        Get balance for a specific month.
        
        Convenience method for monthly summaries.
        """
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        
        return await BalanceService.get_balance(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    @staticmethod
    async def get_current_month_balance(user_id: str) -> Dict:
        """
        Get balance for current month.
        
        Convenience method for current month summary.
        """
        today = date.today()
        return await BalanceService.get_monthly_balance(
            user_id=user_id,
            year=today.year,
            month=today.month
        )
