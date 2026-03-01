description: "Scaffold a new test file with proper structure and fixtures"

# This skill helps create a new test file with proper structure
# The user should provide: module_name (e.g., "my_module")

# Create the test directory if it doesn't exist
mkdir -p "/Users/zelin/Desktop/PA Investment/Invest_strategy/tests/unit"

# Create the test file template
cat > "/Users/zelin/Desktop/PA Investment/Invest_strategy/tests/unit/test_{{module_name}}.py" << 'EOF'
"""Unit tests for {{module_name}} module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class Test{{module_name_cap}}:
    """Test cases for {{module_name}}."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement test
        assert True

    def test_edge_case_empty_input(self):
        """Test edge case with empty input."""
        # TODO: Implement test
        pass

    def test_edge_case_invalid_input(self):
        """Test edge case with invalid input."""
        # TODO: Implement test
        pass

    def test_with_sample_data(self, sample_returns_series):
        """Test with sample returns data."""
        # Use fixture from conftest.py
        assert sample_returns_series is not None
        assert len(sample_returns_series) > 0
EOF

echo "Created test file: tests/unit/test_{{module_name}}.py"
echo ""
echo "To customize, edit the file and replace:"
echo "  - {{module_name}} with your module name"
echo "  - {{module_name_cap}} with Capitalized module name"
echo "  - Add your test implementations"
