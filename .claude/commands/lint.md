description: "Run full linting suite: flake8, black, isort"

cd "/Users/zelin/Desktop/PA Investment/Invest_strategy"

echo "=== Running Flake8 ==="
flake8 backend/ frontend/ portfolio/ backtests/ execution/ --max-line-length=120 --ignore=E501,W503 || true

echo ""
echo "=== Running Black Check ==="
black --check backend/ frontend/ portfolio/ backtests/ execution/ --diff || true

echo ""
echo "=== Running isort Check ==="
isort --check-only backend/ frontend/ portfolio/ backtests/ execution/ --profile black || true

echo ""
echo "=== Linting Complete ==="
echo "To auto-fix issues, run: make format"
