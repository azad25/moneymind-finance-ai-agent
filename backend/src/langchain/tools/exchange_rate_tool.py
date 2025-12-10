"""
Exchange Rate Tool - REAL IMPLEMENTATION
LangChain tool for currency conversion using ExchangeRate-API
"""
from typing import Optional
from langchain_core.tools import tool
import httpx

from src.config.settings import settings


@tool
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> str:
    """
    Convert an amount from one currency to another using real-time exchange rates.
    
    Uses ExchangeRate-API for live rates.
    
    Args:
        amount: Amount to convert (positive number)
        from_currency: Source currency code (USD, EUR, GBP, THB, JPY, etc.)
        to_currency: Target currency code
    
    Returns:
        Converted amount with exchange rate information
    
    Example:
        convert_currency(100, "USD", "EUR") -> "💱 100.00 USD = 92.00 EUR"
    """
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()
    
    # Validate currencies
    valid_currencies = [
        "USD", "EUR", "GBP", "THB", "JPY", "CNY", "KRW", "INR", "AUD", "CAD",
        "CHF", "SGD", "HKD", "NZD", "SEK", "NOK", "DKK", "MXN", "BRL", "ZAR"
    ]
    
    if from_currency not in valid_currencies:
        return f"❌ Unknown currency: {from_currency}. Supported: {', '.join(valid_currencies[:10])}..."
    
    if to_currency not in valid_currencies:
        return f"❌ Unknown currency: {to_currency}. Supported: {', '.join(valid_currencies[:10])}..."
    
    if amount <= 0:
        return "❌ Amount must be positive."
    
    if not settings.exchange_rate_api_key:
        # Fallback to approximate rates
        fallback_rates = {
            ("USD", "EUR"): 0.92,
            ("USD", "GBP"): 0.79,
            ("USD", "THB"): 35.5,
            ("USD", "JPY"): 149.5,
            ("EUR", "USD"): 1.09,
            ("EUR", "GBP"): 0.86,
            ("GBP", "USD"): 1.27,
            ("THB", "USD"): 0.028,
            ("JPY", "USD"): 0.0067,
        }
        
        if from_currency == to_currency:
            return f"💱 {amount:,.2f} {from_currency} = {amount:,.2f} {to_currency}"
        
        rate = fallback_rates.get((from_currency, to_currency))
        if not rate:
            # Try inverse
            inverse = fallback_rates.get((to_currency, from_currency))
            if inverse:
                rate = 1 / inverse
            else:
                # Try through USD
                to_usd = fallback_rates.get((from_currency, "USD"), 1)
                from_usd = fallback_rates.get(("USD", to_currency), 1)
                rate = to_usd * from_usd
        
        converted = amount * rate
        return (
            f"💱 **Currency Conversion**\n\n"
            f"**{amount:,.2f} {from_currency}** = **{converted:,.2f} {to_currency}**\n\n"
            f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}\n"
            f"*(Approximate rate - configure API key for live rates)*"
        )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://v6.exchangerate-api.com/v6/{settings.exchange_rate_api_key}/pair/{from_currency}/{to_currency}/{amount}"
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                rate = data["conversion_rate"]
                converted = data["conversion_result"]
                
                return (
                    f"💱 **Currency Conversion**\n\n"
                    f"**{amount:,.2f} {from_currency}** = **{converted:,.2f} {to_currency}**\n\n"
                    f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}\n"
                    f"*Rate updated: {data.get('time_last_update_utc', 'Recently')}*"
                )
            else:
                error_type = data.get("error-type", "Unknown error")
                return f"❌ Conversion failed: {error_type}"
                
    except httpx.TimeoutException:
        return "❌ Timeout connecting to exchange rate service. Please try again."
    except Exception as e:
        return f"❌ Currency conversion error: {str(e)}"


@tool
async def get_exchange_rate(
    from_currency: str,
    to_currency: str,
) -> str:
    """
    Get the current exchange rate between two currencies.
    
    Args:
        from_currency: Base currency code (USD, EUR, etc.)
        to_currency: Target currency code
    
    Returns:
        Current exchange rate
    """
    from_currency = from_currency.upper().strip()
    to_currency = to_currency.upper().strip()
    
    if not settings.exchange_rate_api_key:
        return f"📈 1 {from_currency} ≈ (configure API key for live rates)"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://v6.exchangerate-api.com/v6/{settings.exchange_rate_api_key}/pair/{from_currency}/{to_currency}"
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                rate = data["conversion_rate"]
                return f"📈 **Exchange Rate**\n\n1 {from_currency} = {rate:.4f} {to_currency}"
            else:
                return f"❌ Failed to get rate: {data.get('error-type', 'Unknown')}"
                
    except Exception as e:
        return f"❌ Exchange rate error: {str(e)}"


@tool
async def list_exchange_rates(base_currency: str = "USD") -> str:
    """
    List exchange rates for multiple currencies against a base currency.
    
    Args:
        base_currency: Base currency code (default: USD)
    
    Returns:
        Table of exchange rates
    """
    base_currency = base_currency.upper().strip()
    target_currencies = ["EUR", "GBP", "THB", "JPY", "CNY", "INR", "AUD", "CAD", "CHF", "SGD"]
    
    if not settings.exchange_rate_api_key:
        return f"📊 Configure ExchangeRate API key to see live rates for {base_currency}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://v6.exchangerate-api.com/v6/{settings.exchange_rate_api_key}/latest/{base_currency}"
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                
                output = f"📊 **Exchange Rates** (Base: {base_currency})\n\n"
                output += "| Currency | Rate |\n"
                output += "|----------|------|\n"
                
                for curr in target_currencies:
                    if curr in rates and curr != base_currency:
                        output += f"| {curr} | {rates[curr]:.4f} |\n"
                
                output += f"\n*Updated: {data.get('time_last_update_utc', 'Recently')}*"
                return output
            else:
                return f"❌ Failed to get rates: {data.get('error-type', 'Unknown')}"
                
    except Exception as e:
        return f"❌ Error fetching rates: {str(e)}"


# Export main tool
exchange_rate_tool = convert_currency
