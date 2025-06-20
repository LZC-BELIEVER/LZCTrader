class Order:
    """AutoTrader Order object."""

    def __init__(
        self,
        instrument: str = None,
        direction: int = None,
        exchange: str = None,
        offset: int = None,
        price: int = None,
        volume: int = None,
        stopPrice: int = None,
        orderPriceType: int = None,
    ):
        """Create a new order.

        Parameters
        ----------
        instrument : str
            The trading instrument of the order.

        direction : int
            The direction of the order (1 for long, -1 for short).

        """

        # Required attributes
        self.instrument = instrument
        self.direction = direction
        self.exchange = exchange
        self.offset = offset
        self.price = price
        self.volume = volume
        self.stopPrice = stopPrice
        self.orderPriceType = orderPriceType
