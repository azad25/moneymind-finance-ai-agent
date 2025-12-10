"""
Stock Price Tool
LangChain tool for fetching stock prices via AlphaVantage API
"""
from typing import Optional
from langchain_core.tools import tool
import httpx

from src.config.settings import settings


@tool
async def get_stock_price(symbol: str) -> str:
    """
    Get the current stock price for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA, MSFT)
    
    Returns:
        Current stock price and change information
    """
    symbol = symbol.upper().strip()
    
    if not settings.alpha_vantage_api_key:
        return f"❌ AlphaVantage API key not configured. Cannot fetch stock price for {symbol}."
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if "Global Quote" not in data or not data["Global Quote"]:
                return f"❌ No data found for symbol: {symbol}. Please check if the symbol is correct."
            
            quote = data["Global Quote"]
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = quote.get("10. change percent", "0%")
            high = float(quote.get("03. high", 0))
            low = float(quote.get("04. low", 0))
            volume = int(quote.get("06. volume", 0))
            
            # Determine emoji based on change
            trend = "📈" if change >= 0 else "📉"
            
            return (
                f"{trend} **{symbol}** Stock Price\n\n"
                f"**Current Price:** ${price:,.2f}\n"
                f"**Change:** ${change:+,.2f} ({change_percent})\n"
                f"**Day High:** ${high:,.2f}\n"
                f"**Day Low:** ${low:,.2f}\n"
                f"**Volume:** {volume:,}"
            )
            
    except httpx.TimeoutException:
        return f"❌ Timeout fetching stock price for {symbol}. Please try again."
    except Exception as e:
        return f"❌ Error fetching stock price for {symbol}: {str(e)}"


@tool
async def get_stock_quote(symbol: str) -> str:
    """
    Get a detailed stock quote including company overview.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)
    
    Returns:
        Detailed stock information including price, market cap, P/E ratio, etc.
    """
    symbol = symbol.upper().strip()
    
    if not settings.alpha_vantage_api_key:
        return f"❌ AlphaVantage API key not configured."
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get quote
            quote_response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key,
                }
            )
            quote_data = quote_response.json()
            
            # Get overview
            overview_response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "OVERVIEW",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key,
                }
            )
            overview_data = overview_response.json()
            
            if "Global Quote" not in quote_data or not quote_data["Global Quote"]:
                return f"❌ No data found for symbol: {symbol}"
            
            quote = quote_data["Global Quote"]
            price = float(quote.get("05. price", 0))
            change = float(quote.get("09. change", 0))
            change_percent = quote.get("10. change percent", "0%")
            
            trend = "📈" if change >= 0 else "📉"
            
            result = (
                f"{trend} **{symbol}** Detailed Quote\n\n"
                f"**Price:** ${price:,.2f} ({change_percent})\n"
            )
            
            if overview_data and "Symbol" in overview_data:
                name = overview_data.get("Name", symbol)
                market_cap = overview_data.get("MarketCapitalization", "N/A")
                pe_ratio = overview_data.get("PERatio", "N/A")
                dividend_yield = overview_data.get("DividendYield", "N/A")
                week_52_high = overview_data.get("52WeekHigh", "N/A")
                week_52_low = overview_data.get("52WeekLow", "N/A")
                
                # Format market cap
                if market_cap != "N/A":
                    mc = int(market_cap)
                    if mc >= 1_000_000_000_000:
                        market_cap = f"${mc/1_000_000_000_000:.2f}T"
                    elif mc >= 1_000_000_000:
                        market_cap = f"${mc/1_000_000_000:.2f}B"
                    elif mc >= 1_000_000:
                        market_cap = f"${mc/1_000_000:.2f}M"
                
                result = (
                    f"{trend} **{name}** ({symbol})\n\n"
                    f"**Price:** ${price:,.2f} ({change_percent})\n"
                    f"**Market Cap:** {market_cap}\n"
                    f"**P/E Ratio:** {pe_ratio}\n"
                    f"**Dividend Yield:** {dividend_yield}\n"
                    f"**52-Week High:** ${float(week_52_high):,.2f}\n"
                    f"**52-Week Low:** ${float(week_52_low):,.2f}"
                )
            
            return result
            
    except Exception as e:
        return f"❌ Error fetching stock quote: {str(e)}"


@tool
async def get_crypto_price(symbol: str) -> str:
    """
    Get the current cryptocurrency price.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, DOGE)
    
    Returns:
        Current crypto price in USD
    """
    symbol = symbol.upper().strip()
    
    if not settings.alpha_vantage_api_key:
        return f"❌ AlphaVantage API key not configured."
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": symbol,
                    "to_currency": "USD",
                    "apikey": settings.alpha_vantage_api_key,
                }
            )
            data = response.json()
            
            if "Realtime Currency Exchange Rate" not in data:
                return f"❌ No data found for crypto: {symbol}"
            
            rate_data = data["Realtime Currency Exchange Rate"]
            price = float(rate_data.get("5. Exchange Rate", 0))
            
            return f"🪙 **{symbol}/USD:** ${price:,.2f}"
            
    except Exception as e:
        return f"❌ Error fetching crypto price: {str(e)}"
