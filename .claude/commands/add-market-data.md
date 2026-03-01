description: "Add new market data series (FRED/yfinance) to the platform"

# This skill guides adding a new market data series to the platform
# Follow these steps:

echo "=== Adding New Market Data Series ==="
echo ""
echo "Step 1: Determine the data source"
echo "  - FRED series? Edit backend/market_data_service.py"
echo "  - yfinance ticker? Edit backend/market_data_service.py"
echo ""
echo "Step 2: Add to appropriate ticker dict in market_data_service.py"
echo "  - RATES_FRED_SERIES: for Treasury yields, inflation, policy rates"
echo "  - MACRO_FRED_SERIES: for macro indicators (GDP, unemployment, etc.)"
echo "  - FED_LIQUIDITY_SERIES: for Fed balance sheet data"
echo "  - FX_TICKERS: for forex pairs"
echo "  - EQUITY_TICKERS: for equity indices"
echo "  - COMMODITY_TICKERS: for commodities"
echo ""
echo "Step 3: Add to market_data_store.py if storing in Parquet"
echo "  - Update _ASSET_CLASS_TICKERS dict"
echo "  - Update _FRED_CATEGORY_SERIES dict"
echo ""
echo "Step 4: Add to frontend display (if needed)"
echo "  - Edit frontend/components/market_panels.py"
echo "  - Add to DEFINITIONS dict for tooltip"
echo "  - Add to CATEGORY_ORDER if new category"
echo ""
echo "Step 5: Test the data pull"
echo "  - curl http://localhost:8000/api/data/pull -X POST -d '{\"ticker\": \"YOUR_TICKER\"}'"
echo "  - Or use the Data Manager UI tab"
echo ""
echo "Example - Adding a new FRED series:"
echo '  # In market_data_service.py, add to RATES_FRED_SERIES:'
echo '  "NEW_SERIES": {"name": "New Series Name", "tenor": "1Y", "category": "treasury", "tenor_years": 1},'
echo ""
echo "Example - Adding a new yfinance ticker:"
echo '  # In market_data_service.py, add to EQUITY_TICKERS:'
echo '  "^RUT": {"name": "Russell 2000", "region": "US"},'
