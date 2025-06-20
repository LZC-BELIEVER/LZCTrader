import threading
import pandas as pd
from finta import TA
from datetime import datetime
from LZCTrader.strategy import Strategy
from brokers.broker import Broker
from LZCTrader.order import Order


class Example(Strategy):
    """Example Strategy

    策略演示文件
    请根据此文件的规范格式，写出自定义策略
    """

    def __init__(
        self, instrument: str, exchange: str, parameters: dict, broker: Broker  # 这四个是必需参数
    ) -> None:
        # 必需：
        self.instrument = instrument  # 品种
        self.exchange = exchange  # 交易所
        self.params = parameters  # 策略参数
        self.broker = broker  # 功能接口

        # 自定义：
        self.trade_num = 1  # 交易手数
        self.trade_offset = 3  # 取买几卖几
        self.lock = threading.Lock()  # 线程锁

    def min_generate_features(self, data: pd.DataFrame):
        # 在此函数中，根据传入参数data，计算出你策略所需的MA，EMA等指标，非必需
        ema_period = self.params['ema_period']  # 取参数，进行计算

        return data

    def generate_signal(self, dt: datetime):
        # 此为函数主体，根据指标进行计算，产生交易信号并下单，程序只会调用这一个函数进行不断循环。必需

        new_orders = []
        data = self.broker.get_candles(self.instrument, granularity="1min", count=30, cut_yesterday=True)  # 取行情数据函数示例
        # granularity：时间粒度，支持1s，5s，1min，1h等；
        # count：取k线的数目；
        # cut_yesterday：取的数据中，当同时包含今日数据和昨日数据时，是否去掉昨日数据。True表示去掉；
        data = data[::-1]  # 取到的数据中，按时间由近到远排序。再此翻转为由远到近，便于某些策略处理

        some_condition = True  # 由取到的data计算，得到某些condition，作为策略下单条件

        temp = self.broker.get_candles(self.instrument, granularity="1s", count=1)
        current_point = temp.iloc[0]['Close']  # 取最近一根秒级k线，作为当前价格

        if some_condition:
            self.broker.relog()  # 由于一段时间不登录，交易所可能会自动下线，所以每次下单前先登录
            duo_enter_point = current_point + self.trade_offset  # 下单价。为保证立刻成交，在此取买三、卖三报单，按照价格优先原则，会按当前价成交。取买几、卖几可自定义。
            new_order = Order(
                instrument=self.instrument,
                exchange=self.exchange,
                direction=2,  # 2为买，3为卖
                offset=1,  # 1为开仓，4为平今，5为平昨
                price=duo_enter_point,  # 下单价
                volume=self.trade_num,  # 下单手数
                stopPrice=0,  # 未实现功能。设为0即可
                orderPriceType=1  # 类型：限价单（现在限价单和市价单由报单价决定。以开多仓为例，报单价比当前价高，则立即成交，相当于市价单。报单价比当前价低，则需等价格跌到此价才成交，相当于现价单）
            )
            new_orders.append(new_order)
            self.write_order(type=1, point=current_point)  # 记录下单结果
        else:
            self.broker.relog()
            kong_enter_point = current_point - self.trade_offset
            new_order = Order(
                instrument=self.instrument,
                exchange=self.exchange,
                direction=3,
                offset=1,
                price=kong_enter_point,
                volume=self.trade_num,
                stopPrice=0,
                orderPriceType=1
            )
            new_orders.append(new_order)
            self.write_order(type=3, point=current_point)
        return new_orders

    def write_order(self, type, point):  # 记录下单结果函数，非必需
        now = datetime.now().strftime("%m-%d %H:%M:%S")
        if type == 1:  # 买开
            line = f"{now} {self.instrument}，买开，{point} \n"
        elif type == 2:  # 买平
            line = f"{now} {self.instrument}，买平，{point} \n"
        elif type == 3:  # 卖开
            line = f"{now} {self.instrument}，卖开，{point} \n"
        elif type == 4:  # 卖平
            line = f"{now} {self.instrument}，卖平，{point} \n"
        else:
            raise ValueError("Invalid type")

        with self.lock:
            with open("L:/Quantification/LeopardSeek/result/order_book.txt", "a", encoding="utf-8") as f:
                f.write(line)


