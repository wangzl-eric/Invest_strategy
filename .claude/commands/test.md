description: "Run tests with coverage report. Fails if coverage is below threshold."

# Run pytest with coverage for backend, portfolio, backtests, and execution modules
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"
python -m pytest tests/unit/ --cov=backend --cov=portfolio --cov=backtests --cov=execution --cov-report=term-missing

# Show summary
echo ""
echo "=== Coverage Summary ==="
echo "Current threshold: 10%"
echo "To increase threshold, edit pytest.ini and update --cov-fail-under value"
