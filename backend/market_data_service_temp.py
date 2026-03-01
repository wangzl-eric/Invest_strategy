def _fetch_ibkr_rates_futures() -> List[dict]:
    """Fetch treasury futures data - currently uses yfinance for reliability.
    
    Returns list of rate data with yields.
    
    Note: IBKR integration is deferred due to asyncio event loop complexity
    in the ThreadPoolExecutor context. The infrastructure is in place for
    future implementation when a more robust async solution is available.
    """
    # IBKR futures tickers mapped to yfinance yield tickers
    # ZB (30Y) -> ^TYX, ZN (10Y) -> ^TNX, ZF (5Y) -> ^FVX, ZT (2Y) -> ^IRX
    futures_to_yield = {
        "ZB": "^TYX",  # 30Y Treasury
        "ZN": "^TNX",  # 10Y Treasury  
        "ZF": "^FVX",  # 5Y Treasury
        "ZT": "^IRX",  # 2Y Treasury
    }
    
    logger.info("Using yfinance for treasury yields")
    return _fetch_yfinance_rates(futures_to_yield)


def _fetch_yfinance_rates(futures_to_yield: dict) -> List[dict]:
    """Fetch rates from yfinance."""
    results = []
    
    try:
        yield_tickers = list(futures_to_yield.values())
        df = _yf_download(yield_tickers, period="5d")
        
        if df is None or df.empty:
            return results
        
        if isinstance(df.columns, pd.MultiIndex):
            close_data = df.xs("Close", level=0, axis=1) if "Close" in df.columns.get_level_values(0) else pd.DataFrame()
        else:
            close_data = df[["Close"]] if "Close" in df.columns else pd.DataFrame()
        
        if close_data.empty:
            return results
            
        for fut_ticker, yield_ticker in futures_to_yield.items():
            try:
                if yield_ticker not in close_data.columns:
                    continue
                    
                ticker_data = close_data[yield_ticker].dropna()
                if ticker_data.empty:
                    continue
                    
                latest_value = ticker_data.iloc[-1]
                latest_date = ticker_data.index[-1]
                
                meta = IBKR_RATES_FUTURES.get(fut_ticker, {})
                
                history = []
                for idx, val in ticker_data.items():
                    if not pd.isna(val):
                        history.append({"date": str(idx.date()), "value": round(float(val), 3)})
                
                chg = None
                if len(ticker_data) >= 2:
                    prev_value = ticker_data.iloc[-2]
                    if not pd.isna(prev_value):
                        chg = round(float(latest_value - prev_value), 3)
                
                results.append({
                    "series": fut_ticker,
                    "ticker": fut_ticker,
                    "name": meta.get("name", fut_ticker),
                    "tenor": meta.get("tenor", ""),
                    "value": round(float(latest_value), 3),
                    "change": chg,
                    "date": str(latest_date.date()),
                    "source": "yfinance",
                    "category": "treasury",
                    "history": history,
                })
                
            except Exception as e:
                logger.debug(f"Error processing {fut_ticker}: {e}")
                continue
                
    except Exception as e:
        logger.debug(f"Rates fetch error: {e}")
    
    return results
