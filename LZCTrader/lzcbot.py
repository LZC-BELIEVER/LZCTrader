import os
import time
from datetime import datetime
from LZCTrader.strategy import Strategy
from LZCTrader.order import Order


class LZCBot:
    """AutoTrader Trading Bot, responsible for a trading strategy."""

    def __init__(
        self,
        strategy: Strategy
    ) -> None:
        """Instantiates an AutoTrader Bot.

        Parameters
        ----------
        strategy : Strategy
            The strategy.

        Raises
        ------
        Exception
            When there is an error retrieving the instrument data.
        """
        self.instrument = strategy.instrument
        self.broker = strategy.broker
        self.strategy = strategy
        self.run_thread = None
        self.stop_flag = None
        self.stop_thread = None

    def __repr__(self):
        if isinstance(self.instrument, list):
            return "Portfolio AutoTraderBot"
        else:
            return f"{self.instrument} AutoTraderBot"

    def __str__(self):
        return "AutoTraderBot instance"

    def update(self, timestamp: datetime) -> None:
        """Update strategy with the latest data and generate a trade signal.

        Parameters
        ----------
        timestamp : datetime, optional
            The current update time.
        """
        try:
            strategy_orders = self.strategy.generate_signal(timestamp)
        except Exception as e:
            print(f"Error when updating strategy: {e}")
            strategy_orders = []

        # Check and qualify orders
        orders = strategy_orders

        if orders is not None and len(orders) > 0:
            # Submit orders
            for order in orders:
                if order is None:
                    continue
                # Submit order to relevant exchange
                try:
                    self.submit_order(
                        order=order
                    )
                except Exception as e:
                    print(f"AutoTrader exception when submitting order: {e}")

    def submit_order(self, order: Order):
        "The default order execution method."
        self.broker.place_order(order)
