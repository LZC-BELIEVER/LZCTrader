from brokers.broker import Broker


class Preliminary:

    def __init__(
        self,
        broker: Broker
    ) -> None:
        self.watchlist = []
        self.broker = broker

    def generate_tradelist(self, watchlist):
        self.watchlist = watchlist
        return self.watchlist

    # 程序运行时，会现调用generate_tradelist函数，从watchlist中筛选出交易品种。若有需要，可以按照策略文件以及此文件的格式，写出初筛策略实现选股
