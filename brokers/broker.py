import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod
from LZCTrader.order import Order


class Broker(ABC):
    @abstractmethod
    def place_order(self, order: Order) -> None:
        """Translate order and place via exchange API."""

    @abstractmethod
    def get_candles(
            self,
            instrument: str,
            granularity: str = None,
            count: int = None,
            start_time: datetime = None,
            end_time: datetime = None,
            cut_yesterday: bool = True
    ) -> pd.DataFrame:
        """Get candles for an instrument."""
        pass

    @abstractmethod
    def relog(self):
        pass

    @abstractmethod
    def get_position(self, instrument: str) -> dict:
        return {}

