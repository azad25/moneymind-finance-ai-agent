"""
Expense Management Routes
CRUD operations for expenses, subscriptions, bills, goals, income
"""
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

router = APIRouter()


# ============== Expense Models ==============
class ExpenseCreate(BaseModel):
    """Create expense request."""
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    category: str
    merchant: str
    description: Optional[str] = None
    expense_date: date


class ExpenseResponse(BaseModel):
    """Expense response model."""
    id: str
    amount: Decimal
    currency: str
    category: str
    merchant: str
    description: Optional[str]
    expense_date: date
    created_at: datetime


class ExpenseListResponse(BaseModel):
    """List of expenses response."""
    expenses: List[ExpenseResponse]
    total: int
    total_amount: Decimal


# ============== Subscription Models ==============
class SubscriptionCreate(BaseModel):
    """Create subscription request."""
    name: str
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    billing_cycle: str = Field(
        ...,
        pattern="^(daily|weekly|monthly|yearly)$"
    )
    next_billing_date: date
    category: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """Subscription response model."""
    id: str
    name: str
    amount: Decimal
    currency: str
    billing_cycle: str
    next_billing_date: date
    category: Optional[str]
    is_active: bool
    created_at: datetime


# ============== Bill Models ==============
class BillCreate(BaseModel):
    """Create bill request."""
    name: str
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    due_date: date
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class BillResponse(BaseModel):
    """Bill response model."""
    id: str
    name: str
    amount: Decimal
    currency: str
    due_date: date
    is_recurring: bool
    is_paid: bool
    created_at: datetime


# ============== Income Models ==============
class IncomeCreate(BaseModel):
    """Create income request."""
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    source: str
    category: Optional[str] = None
    description: Optional[str] = None
    income_date: date


class IncomeResponse(BaseModel):
    """Income response model."""
    id: str
    amount: Decimal
    currency: str
    source: str
    category: Optional[str]
    description: Optional[str]
    income_date: date
    created_at: datetime


# ============== Goal Models ==============
class GoalCreate(BaseModel):
    """Create financial goal request."""
    name: str
    target_amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    deadline: date
    category: Optional[str] = None


class GoalResponse(BaseModel):
    """Goal response model."""
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    deadline: date
    category: Optional[str]
    progress_percent: float
    created_at: datetime


# ============== Expense Endpoints ==============
@router.post("", response_model=ExpenseResponse)
async def create_expense(expense: ExpenseCreate):
    """Create a new expense."""
    # TODO: Save to PostgreSQL
    return ExpenseResponse(
        id="exp_123",
        amount=expense.amount,
        currency=expense.currency,
        category=expense.category,
        merchant=expense.merchant,
        description=expense.description,
        expense_date=expense.expense_date,
        created_at=datetime.utcnow()
    )


@router.get("")
async def list_expenses(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List expenses with optional filters."""
    # TODO: Query PostgreSQL - for now return empty array
    return []


@router.get("/balance")
async def get_balance():
    """Get current account balance."""
    from sqlalchemy import func
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Account, Income, Expense
    import uuid
    
    async with async_session_factory() as session:
        try:
            # Calculate total income
            income_result = await session.execute(
                select(func.sum(Income.amount))
            )
            total_income = income_result.scalar() or Decimal("0")
            
            # Calculate total expenses
            expense_result = await session.execute(
                select(func.sum(Expense.amount))
            )
            total_expenses = expense_result.scalar() or Decimal("0")
            
            # Calculate balance
            calculated_balance = total_income - total_expenses
            
            return {
                "balance": float(calculated_balance),
                "currency": "USD",
                "last_updated": datetime.utcnow(),
                "total_income": float(total_income),
                "total_expenses": float(total_expenses)
            }
        except Exception as e:
            # Return mock data if calculation fails
            return {
                "balance": 0,
                "currency": "USD",
                "last_updated": datetime.utcnow(),
                "error": str(e)
            }


# ============== Income Endpoints (MUST BE BEFORE /{expense_id}) ==============
@router.post("/income", response_model=IncomeResponse)
async def create_income(income: IncomeCreate):
    """Create a new income record."""
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Income
    import uuid
    
    async with async_session_factory() as session:
        # TODO: Get current_user from authentication
        # For now, use a default user_id
        user_id = "default_user"
        
        income_record = Income(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=income.amount,
            currency=income.currency,
            source=income.source,
            category=income.category,
            description=income.description,
            income_date=income.income_date,
            created_at=datetime.utcnow()
        )
        
        session.add(income_record)
        await session.commit()
        await session.refresh(income_record)
        
        return IncomeResponse(
            id=income_record.id,
            amount=income_record.amount,
            currency=income_record.currency,
            source=income_record.source,
            category=income_record.category,
            description=income_record.description,
            income_date=income_record.income_date,
            created_at=income_record.created_at
        )


@router.get("/income")
async def list_income(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List income records with optional filters."""
    from src.infrastructure.database.postgres import async_session_factory
    from src.domain.models import Income
    
    async with async_session_factory() as session:
        # TODO: Filter by current_user
        query = select(Income)
        
        if start_date:
            query = query.where(Income.income_date >= start_date)
        if end_date:
            query = query.where(Income.income_date <= end_date)
        
        query = query.offset(skip).limit(limit).order_by(Income.income_date.desc())
        
        result = await session.execute(query)
        income_records = result.scalars().all()
        
        return [
            {
                "id": record.id,
                "amount": float(record.amount),
                "currency": record.currency,
                "source": record.source,
                "category": record.category,
                "description": record.description,
                "income_date": record.income_date.isoformat(),
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
            for record in income_records
        ]


# ============== Subscription Endpoints (MUST BE BEFORE /{expense_id}) ==============
@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(subscription: SubscriptionCreate):
    """Create a new subscription."""
    return SubscriptionResponse(
        id="sub_123",
        name=subscription.name,
        amount=subscription.amount,
        currency=subscription.currency,
        billing_cycle=subscription.billing_cycle,
        next_billing_date=subscription.next_billing_date,
        category=subscription.category,
        is_active=True,
        created_at=datetime.utcnow()
    )


@router.get("/subscriptions")
async def list_subscriptions():
    """List all subscriptions."""
    # TODO: Query PostgreSQL - for now return empty array
    return []


# ============== Bill Endpoints (MUST BE BEFORE /{expense_id}) ==============
@router.post("/bills", response_model=BillResponse)
async def create_bill(bill: BillCreate):
    """Create a new bill."""
    return BillResponse(
        id="bill_123",
        name=bill.name,
        amount=bill.amount,
        currency=bill.currency,
        due_date=bill.due_date,
        is_recurring=bill.is_recurring,
        is_paid=False,
        created_at=datetime.utcnow()
    )


@router.get("/bills")
async def list_bills(
    include_paid: bool = False,
    upcoming_days: Optional[int] = Query(None, ge=1)
):
    """List bills, optionally filtered by upcoming due dates."""
    # TODO: Query PostgreSQL - for now return empty array
    return []


@router.post("/bills/{bill_id}/pay")
async def mark_bill_paid(bill_id: str):
    """Mark a bill as paid."""
    return {"message": "Bill marked as paid"}


# ============== Goal Endpoints (MUST BE BEFORE /{expense_id}) ==============
@router.post("/goals", response_model=GoalResponse)
async def create_goal(goal: GoalCreate):
    """Create a financial goal."""
    return GoalResponse(
        id="goal_123",
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=Decimal("0"),
        currency=goal.currency,
        deadline=goal.deadline,
        category=goal.category,
        progress_percent=0.0,
        created_at=datetime.utcnow()
    )


@router.get("/goals")
async def list_goals():
    """List all financial goals."""
    # TODO: Query PostgreSQL - for now return empty array
    return []


@router.post("/goals/{goal_id}/contribute")
async def contribute_to_goal(goal_id: str, amount: Decimal = Query(..., gt=0)):
    """Add contribution to a goal."""
    return {"message": f"Added {amount} to goal"}


# ============== Parameterized Expense Endpoints (MUST BE LAST) ==============
@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: str):
    """Get expense by ID."""
    raise HTTPException(status_code=404, detail="Expense not found")


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: str, expense: ExpenseCreate):
    """Update an expense."""
    raise HTTPException(status_code=404, detail="Expense not found")


@router.delete("/{expense_id}")
async def delete_expense(expense_id: str):
    """Delete an expense."""
    return {"message": "Expense deleted"}


# ============== Analytics Endpoints ==============
@router.get("/analytics/summary")
async def get_spending_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get spending summary with totals and breakdowns."""
    return {
        "total_spent": Decimal("0"),
        "total_income": Decimal("0"),
        "net": Decimal("0"),
        "by_category": {},
        "by_merchant": {},
        "trends": []
    }


@router.get("/analytics/forecast")
async def get_cashflow_forecast(months: int = Query(3, ge=1, le=12)):
    """Get cashflow forecast for upcoming months."""
    return {
        "forecast": [],
        "predicted_balance": Decimal("0"),
        "confidence": 0.0
    }
