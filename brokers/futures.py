import os
import time
import threading
import pickle
import importlib
import pandas as pd
from datetime import datetime, timezone
from brokers.broker import Broker
from LZCTrader.order import Order
import API


class Futures(Broker):
    def __init__(self, enter_license: str, fc_code: str, account: str, password: str):

        self.lisence = enter_license
        self.account_id = account
        self.password = password
        self.fc_code = fc_code

        # Assign data broker
        self.data_broker = self
        self.allow_dancing_bears = False

        self.api = API.Context(lisence=self.lisence, fc_code=self.fc_code, user_id=self.account_id, password=self.password)

        self.long_position = 0
        self.short_position = 0
        self.timer_thread = None

    def __repr__(self):
        return "Futures Broker Interface"

    def __str__(self):
        return "Futures Broker Interface"

    def get_candles(
            self,
            instrument: str,
            granularity: str = None,
            count: int = None,
            start_time: datetime = None,
            end_time: datetime = None,
            cut_yesterday: bool = False
    ) -> pd.DataFrame:

        if count is not None:

            response = self.api.instrument.candles(
                instrument, granularity=granularity, count=count
            )
            data = self.response_to_df(response, count, granularity, cut_yesterday)

        else:
            # count is None
            # Assume that both start_time and end_time have been specified.
            from_time = start_time.timestamp()
            to_time = end_time.timestamp()

            # try to get data
            response = self.api.instrument.candles(
                instrument, granularity=granularity, fromTime=from_time, toTime=to_time
            )

            data = self.response_to_df(response, count, granularity, cut_yesterday)

        return data

    def response_to_df(self, response, count, granularity, cut_yesterday):
        """将API响应转换为Pandas DataFrame的函数。"""
        try:
            candles = response
        except KeyError:
            raise Exception(
                "下载数据时出错 - 请检查仪器格式并重试。"
            )

        times = []
        close_price, high_price, low_price, open_price, volume = [], [], [], [], []

        # 请求为字典时，要用[]访问，不能用.访问

        for candle in candles:
            times.append(candle["actionTimestamp"])
            close_price.append(float(candle["close"]))
            high_price.append(float(candle["high"]))
            low_price.append(float(candle["low"]))
            open_price.append(float(candle["open"]))
            volume.append(float(candle["volume"]))

        dataframe = pd.DataFrame(
            {
                "Open": open_price,
                "High": high_price,
                "Low": low_price,
                "Close": close_price,
                "Volume": volume,
            }
        )

        # 将 'barTime' 转换为正确的日期时间格式，去掉微秒部分
        dataframe.index = pd.to_datetime(times, format='ISO8601')

        if cut_yesterday:
            hours = dataframe.index.hour
            get_morning = (hours >= 8) & (hours <= 16)  # 8:00 - 16:00
            get_night = ((hours >= 20) & (hours <= 23)) | ((hours >= 0) & (hours <= 5))  # 20:00 - 5:00

            # 检查是否同时包含 morning 和 night 数据
            has_morning = any(get_morning)
            has_night = any(get_night)

            if has_morning and has_night:
                # 如果同时存在，则根据当前时间决定保留哪一组
                current_hour = pd.Timestamp.now().hour  # 获取当前时间的小时
                if 8 <= current_hour <= 16:
                    selected_group = dataframe[get_morning]  # 当前是早上，保留 morning 数据
                else:
                    selected_group = dataframe[get_night]  # 当前是晚上，保留 night 数据
            elif has_morning:
                selected_group = dataframe[get_morning]  # 只有 morning 数据
            elif has_night:
                selected_group = dataframe[get_night]  # 只有 night 数据
            else:
                raise ValueError("Wrong Data!")  # 都不满足，返回完整数据

            return selected_group

        return dataframe

    def get_positions(
            self,
            instrument: str,
    ) -> list:

        # try to get data
        response = self.api.instrument.positions(
            instrument
        )

        positions_information = response

        return positions_information

    def get_position(self, instrument: str):

        positions_informations = self.get_positions(instrument)
        positions_dict = {}
        positions_dict["long_tdPosition"] = 0
        positions_dict["long_ydPosition"] = 0
        positions_dict["short_tdPosition"] = 0
        positions_dict["short_ydPosition"] = 0

        if positions_informations is None or positions_informations == []:
            positions_dict["long_tdPosition"] = 0
            positions_dict["long_ydPosition"] = 0
            positions_dict["short_tdPosition"] = 0
            positions_dict["short_ydPosition"] = 0
            return positions_dict

        if len(positions_informations) > 2:
            raise ValueError("Wrong position information!")

        for positions_information in positions_informations:
            if positions_information["direction"] == 2:
                positions_dict["long_tdPosition"] = positions_information["tdPosition"]
                positions_dict["long_ydPosition"] = positions_information["ydPosition"]
            elif positions_information["direction"] == 3:
                positions_dict["short_tdPosition"] = positions_information["tdPosition"]
                positions_dict["short_ydPosition"] = positions_information["ydPosition"]
            else:
                raise ValueError("Invalid direction")

        return positions_dict

    def clear_positions(self, instrument: str):

        positions_informations = self.get_positions(instrument)
        if positions_informations is None:
            return

        for positions_information in positions_informations:
            exchange = positions_information["exchange"]
            direction = positions_information["direction"]
            if direction == 2:
                direction = 3
            else:
                direction = 2
            ydPosition = positions_information["ydPosition"]
            tdPosition = positions_information["tdPosition"]
            self.clear_position(instrument, exchange, direction, ydPosition, tdPosition)
        return
    
    def clear_position(self, instrument: str = None, exchange: str = 'SHFE', direction: int = 2, ydPosition: int = 0, tdPosition: int = 0):
        # ！！！！在多品种时，此函数需修改
        close_orders = []
        if(tdPosition>0):
            close_orders.append(self.close_position(instrument, exchange, direction, 4, tdPosition))
        if(ydPosition>0):
            close_orders.append(self.close_position(instrument, exchange, direction, 5, ydPosition))
        for order in close_orders:
            self.place_order(order)
        return

    def close_position(self, instrument: str = None, exchange: str = 'SHFE', direction: int = 2, offset: int = 4, volume: int = 1):
        if direction == 2:
            temp = self.get_candles(instrument, granularity="1s", count=1)
            kong_exit_point = temp.iloc[0]['Close'] + 3
            close_order = Order(
                instrument=instrument,
                direction=direction,
                exchange=exchange,
                offset=offset,
                price=kong_exit_point,
                volume=volume,
                stopPrice=0,
                orderPriceType=1
            )
        elif direction == 3:
            temp = self.get_candles(instrument, granularity="1s", count=1)
            duo_exit_point = temp.iloc[0]['Close'] - 3
            close_order = Order(
                instrument=instrument,
                direction=direction,
                exchange=exchange,
                offset=offset,
                price=duo_exit_point,
                volume=volume,
                stopPrice=0,
                orderPriceType=1
            )
        else:
            raise ValueError(direction)
        return close_order

    def place_order(self, order: Order):
        response = self.api.order.market(
            order=order
        )

        return response

    def relog(self):
        self.api.sse_client.login(self.password)


