from AlgorithmImports import *


class MomentumDemoAlgorithm(QCAlgorithm):
    """
    Dummy momentum strategy (daily):
    - Trade SPY only
    - Compute 63-trading-day ROC (approx 3 months)
    - If ROC > 0: long SPY
    - Else: stay in cash
    """

    def Initialize(self):
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        # Avoid internal benchmark subscription (which defaults to Hour resolution)
        # so we don't need intraday benchmark data in this minimal local dataset.
        self.SetBenchmark(lambda _: 1)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.roc = self.ROC(self.symbol, 63, Resolution.Daily)

        self.SetWarmUp(63, Resolution.Daily)

        # Charting
        self.PlotIndicator("Indicators", self.roc)
        self.current_state = None

    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return

        if not self.roc.IsReady:
            return

        roc_value = float(self.roc.Current.Value)
        target = 1.0 if roc_value > 0 else 0.0

        # Avoid redundant orders
        if self.current_state == target:
            return

        self.SetHoldings(self.symbol, target)
        self.current_state = target

        self.Debug(f"{self.Time.date()} ROC(63)={roc_value:.4f} -> target={target}")

