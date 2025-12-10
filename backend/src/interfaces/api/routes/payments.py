"""
Stripe Payment Routes
Subscription and payment management
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel

router = APIRouter()


class CreateCheckoutSessionRequest(BaseModel):
    """Create checkout session request."""
    price_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Checkout session response."""
    session_id: str
    url: str


class SubscriptionResponse(BaseModel):
    """User subscription response."""
    subscription_id: Optional[str]
    status: str  # active, canceled, past_due, none
    tier: str  # free, pro, enterprise
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool


class PaymentMethodResponse(BaseModel):
    """Payment method response."""
    id: str
    brand: str
    last4: str
    exp_month: int
    exp_year: int


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(request: CreateCheckoutSessionRequest):
    """
    Create a Stripe checkout session for subscription.
    """
    from src.config.settings import settings
    
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")
    
    # TODO: Create Stripe checkout session
    # import stripe
    # stripe.api_key = settings.stripe_secret_key
    # session = stripe.checkout.Session.create(...)
    
    return CheckoutSessionResponse(
        session_id="mock_session_id",
        url="https://checkout.stripe.com/mock_session"
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle Stripe webhook events.
    
    Events handled:
    - checkout.session.completed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.paid
    - invoice.payment_failed
    """
    from src.config.settings import settings
    
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    payload = await request.body()
    
    # TODO: Verify webhook signature
    # TODO: Process event based on type
    # TODO: Update user subscription in database
    
    return {"received": True}


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription():
    """
    Get current user's subscription status.
    """
    # TODO: Fetch subscription from database
    return SubscriptionResponse(
        subscription_id=None,
        status="none",
        tier="free",
        current_period_start=None,
        current_period_end=None,
        cancel_at_period_end=False
    )


@router.post("/cancel-subscription")
async def cancel_subscription():
    """
    Cancel the current subscription at period end.
    """
    # TODO: Cancel subscription via Stripe API
    # TODO: Update database
    return {"message": "Subscription will be canceled at end of billing period"}


@router.get("/payment-methods")
async def get_payment_methods():
    """
    Get user's saved payment methods.
    """
    # TODO: Fetch from Stripe
    return {"payment_methods": []}


@router.get("/invoices")
async def get_invoices():
    """
    Get user's invoice history.
    """
    # TODO: Fetch from Stripe
    return {"invoices": []}


@router.get("/prices")
async def get_prices():
    """
    Get available subscription prices.
    """
    return {
        "prices": [
            {
                "id": "price_free",
                "name": "Free",
                "amount": 0,
                "currency": "usd",
                "interval": "month",
                "features": ["Basic chat", "5 documents", "Limited API calls"]
            },
            {
                "id": "price_pro",
                "name": "Pro",
                "amount": 999,
                "currency": "usd", 
                "interval": "month",
                "features": ["Unlimited chat", "50 documents", "Gmail integration", "Priority support"]
            },
            {
                "id": "price_enterprise",
                "name": "Enterprise",
                "amount": 4999,
                "currency": "usd",
                "interval": "month",
                "features": ["Everything in Pro", "Unlimited documents", "Custom integrations", "Dedicated support"]
            }
        ]
    }
