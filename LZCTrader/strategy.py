from abc import ABC, abstractmethod
from brokers.broker import Broker
from datetime import datetime


class Strategy(ABC):
    @abstractmethod
    def __init__(
        self,
        instrument: str,
        exchange: str,
        parameters: dict,
        broker: Broker
    ) -> None:
        """Instantiate the strategy. This gets called from the TraderBot assigned to
        this strategy.
        """
        super().__init__()
        self.instrument = instrument
        self.exchange = exchange
        self.parameters = parameters
        self.broker = broker

    @abstractmethod
    def generate_signal(self, timestamp: datetime):
        """Generate trading signals based on the data supplied."""


