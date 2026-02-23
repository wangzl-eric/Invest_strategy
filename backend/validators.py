"""Data validation layer for IBKR data."""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Exception raised when data validation fails."""
    pass


class DataValidator:
    """Validator for IBKR account data."""
    
    @staticmethod
    def validate_account_snapshot(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate account snapshot data.
        
        Args:
            data: Dictionary containing account snapshot fields
        
        Returns:
            Validated and cleaned data dictionary
        
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["account_id"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate account_id
        account_id = str(data["account_id"]).strip()
        if not account_id:
            raise ValidationError("account_id cannot be empty")
        
        validated = {
            "account_id": account_id,
            "timestamp": data.get("timestamp", datetime.utcnow()),
        }
        
        # Validate numeric fields
        numeric_fields = [
            "total_cash_value", "net_liquidation", "buying_power",
            "gross_position_value", "available_funds", "excess_liquidity", "equity"
        ]
        
        for field in numeric_fields:
            value = data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if np.isnan(float_value) or np.isinf(float_value):
                        logger.warning(f"Invalid numeric value for {field}: {value}")
                        validated[field] = None
                    else:
                        validated[field] = float_value
                except (ValueError, TypeError):
                    logger.warning(f"Cannot convert {field} to float: {value}")
                    validated[field] = None
            else:
                validated[field] = None
        
        return validated
    
    @staticmethod
    def validate_position(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate position data.
        
        Args:
            data: Dictionary containing position fields
        
        Returns:
            Validated and cleaned data dictionary
        
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["account_id", "symbol", "quantity"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: {field}")
        
        validated = {
            "account_id": str(data["account_id"]).strip(),
            "symbol": str(data["symbol"]).strip().upper(),
            "quantity": float(data["quantity"]),
            "timestamp": data.get("timestamp", datetime.utcnow()),
        }
        
        # Validate quantity is not NaN
        if np.isnan(validated["quantity"]) or np.isinf(validated["quantity"]):
            raise ValidationError(f"Invalid quantity: {data['quantity']}")
        
        # Validate optional numeric fields
        numeric_fields = [
            "avg_cost", "market_price", "market_value", "unrealized_pnl"
        ]
        
        for field in numeric_fields:
            value = data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if np.isnan(float_value) or np.isinf(float_value):
                        validated[field] = None
                    else:
                        validated[field] = float_value
                except (ValueError, TypeError):
                    validated[field] = None
            else:
                validated[field] = None
        
        # Validate optional string fields
        string_fields = ["sec_type", "currency", "exchange"]
        for field in string_fields:
            value = data.get(field)
            validated[field] = str(value).strip() if value else None
        
        return validated
    
    @staticmethod
    def validate_trade(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate trade data.
        
        Args:
            data: Dictionary containing trade fields
        
        Returns:
            Validated and cleaned data dictionary
        
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["account_id", "exec_id", "exec_time", "symbol", "shares", "price"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: {field}")
        
        validated = {
            "account_id": str(data["account_id"]).strip(),
            "exec_id": str(data["exec_id"]).strip(),
            "symbol": str(data["symbol"]).strip().upper(),
            "exec_time": data["exec_time"],
            "shares": float(data["shares"]),
            "price": float(data["price"]),
        }
        
        # Validate shares and price
        if np.isnan(validated["shares"]) or np.isinf(validated["shares"]):
            raise ValidationError(f"Invalid shares: {data['shares']}")
        if np.isnan(validated["price"]) or np.isinf(validated["price"]) or validated["price"] <= 0:
            raise ValidationError(f"Invalid price: {data['price']}")
        
        # Validate side
        side = data.get("side", "BUY")
        if side not in ["BUY", "SELL"]:
            raise ValidationError(f"Invalid side: {side}")
        validated["side"] = side
        
        # Validate optional numeric fields
        numeric_fields = [
            "avg_price", "cum_qty", "proceeds", "commission", "taxes", "cost_basis",
            "realized_pnl"
        ]
        
        for field in numeric_fields:
            value = data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if np.isnan(float_value) or np.isinf(float_value):
                        validated[field] = None
                    else:
                        validated[field] = float_value
                except (ValueError, TypeError):
                    validated[field] = None
            else:
                validated[field] = None
        
        # Validate optional string fields
        string_fields = ["sec_type", "currency", "exchange"]
        for field in string_fields:
            value = data.get(field)
            validated[field] = str(value).strip() if value else None
        
        return validated
    
    @staticmethod
    def validate_pnl_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PnL history data.
        
        Args:
            data: Dictionary containing PnL fields
        
        Returns:
            Validated and cleaned data dictionary
        
        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["account_id", "date"]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: {field}")
        
        validated = {
            "account_id": str(data["account_id"]).strip(),
            "date": data["date"],
        }
        
        # Validate numeric fields (all optional but should be validated if present)
        numeric_fields = [
            "realized_pnl", "unrealized_pnl", "total_pnl",
            "net_liquidation", "total_cash"
        ]
        
        for field in numeric_fields:
            value = data.get(field)
            if value is not None:
                try:
                    float_value = float(value)
                    if np.isnan(float_value) or np.isinf(float_value):
                        validated[field] = None
                    else:
                        validated[field] = float_value
                except (ValueError, TypeError):
                    validated[field] = None
            else:
                validated[field] = None
        
        return validated
    
    @staticmethod
    def detect_outliers(
        series: pd.Series,
        method: str = "iqr",
        threshold: float = 3.0
    ) -> pd.Series:
        """Detect outliers in a pandas Series.
        
        Args:
            series: Series to analyze
            method: Method to use ("iqr" or "zscore")
            threshold: Threshold for outlier detection
        
        Returns:
            Boolean Series indicating outliers
        """
        if len(series) == 0:
            return pd.Series(dtype=bool, index=series.index)
        
        series_clean = series.dropna()
        if len(series_clean) == 0:
            return pd.Series(False, index=series.index)
        
        if method == "iqr":
            q1 = series_clean.quantile(0.25)
            q3 = series_clean.quantile(0.75)
            iqr = q3 - q1
            
            if iqr == 0:
                return pd.Series(False, index=series.index)
            
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            
            outliers = (series < lower_bound) | (series > upper_bound)
            return outliers.fillna(False)
        
        elif method == "zscore":
            mean = series_clean.mean()
            std = series_clean.std()
            
            if std == 0:
                return pd.Series(False, index=series.index)
            
            z_scores = (series - mean) / std
            outliers = (z_scores.abs() > threshold).fillna(False)
            return outliers
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
    
    @staticmethod
    def validate_data_quality(
        account_id: str,
        positions: Optional[List[Dict[str, Any]]] = None,
        trades: Optional[List[Dict[str, Any]]] = None,
        pnl_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive data quality checks.
        
        Args:
            account_id: Account ID
            positions: Optional list of position dictionaries
            trades: Optional list of trade dictionaries
            pnl_history: Optional list of PnL history dictionaries
        
        Returns:
            Dictionary with quality check results
        """
        quality_report = {
            "account_id": account_id,
            "checks_passed": True,
            "issues": [],
            "warnings": [],
        }
        
        # Check positions
        if positions:
            position_count = len(positions)
            quality_report["position_count"] = position_count
            
            # Check for duplicate symbols
            symbols = [p.get("symbol") for p in positions if p.get("symbol")]
            if len(symbols) != len(set(symbols)):
                quality_report["warnings"].append("Duplicate position symbols detected")
            
            # Check for invalid quantities
            invalid_quantities = [
                p for p in positions
                if p.get("quantity") is None or np.isnan(float(p.get("quantity", 0)))
            ]
            if invalid_quantities:
                quality_report["issues"].append(f"{len(invalid_quantities)} positions with invalid quantities")
                quality_report["checks_passed"] = False
        
        # Check trades
        if trades:
            trade_count = len(trades)
            quality_report["trade_count"] = trade_count
            
            # Check for duplicate exec_ids
            exec_ids = [t.get("exec_id") for t in trades if t.get("exec_id")]
            if len(exec_ids) != len(set(exec_ids)):
                quality_report["warnings"].append("Duplicate exec_ids detected")
            
            # Check for invalid prices
            invalid_prices = [
                t for t in trades
                if t.get("price") is None or float(t.get("price", 0)) <= 0
            ]
            if invalid_prices:
                quality_report["issues"].append(f"{len(invalid_prices)} trades with invalid prices")
                quality_report["checks_passed"] = False
        
        # Check PnL history
        if pnl_history:
            pnl_count = len(pnl_history)
            quality_report["pnl_count"] = pnl_count
            
            # Check for date consistency
            dates = [p.get("date") for p in pnl_history if p.get("date")]
            if dates and len(set(dates)) != len(dates):
                quality_report["warnings"].append("Duplicate dates in PnL history")
        
        return quality_report
