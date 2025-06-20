
class EntitySpec(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def create(
        self,
        order
    ):
        new_order = order

        response = self.ctx.sse_client.send_order(
            symbol=new_order.instrument,
            exchange=new_order.exchange,
            direction=new_order.direction,
            offset=new_order.offset,
            price=new_order.price,
            volume=new_order.volume,
            stopPrice=new_order.stopPrice,
            orderPriceType=new_order.orderPriceType
        )

        return response

    def market(self, order):

        return self.create(
            order=order
        )

