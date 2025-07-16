import os
import sys
import time
import threading
import importlib
import importlib.util
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from LZCTrader.tools.utilities import read_yaml, extract_letters
from brokers.futures import Futures
from LZCTrader.lzcbot import LZCBot


class LZCTrader:
    """A Python-Based Automated Trading Systems For China's Market.

    Methods
    -------
    configure(...)
        Configures run settings for LZCTrader.

    add_strategy(...)
        Adds a strategy to the active LZCTrader instance.

    References
    ----------
    Author: LZC from XJTU

    GitHub: https://github.com/LZC-BELIEVER/LeopardSeek
    """

    def __init__(self) -> None:
        """LZCTrader initialisation. Called when creating new LZCTrader
        instance.
        """
        # Public attributes
        self.broker_name = None
        self.broker = None
        self.mode = None
        self.license = ''
        self.account = ''
        self.password = ''
        self.trade_type = ''
        self.across = False
        self.strategy_config = {}
        self.preliminary_config = {}
        self.strategy_timestep = None
        self.preliminary_select = None
        self.strategy_class = None
        self.fake_time = datetime.min
        self.bot_list = []
        self.fc_code = ''
        self.timer_thread = None
        self.market_time_type = None

        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        map_file_path = os.path.join(self.root_dir, "LZCTrader/tools/instrument_map")
        self.instrument_map = read_yaml(map_file_path + ".yaml")

    def __repr__(self):
        return "LZCTrader instance"

    def __str__(self):
        return "LZCTrader instance"

    def configure(
        self,
        broker_name: str = 'futures',
        mode: str = 'realtrading',
        enter_license: str = '',
        account: str = '',
        password: str = '',
        trade_type: str = 'within'
    ) -> None:
        """Configures run settings for LZCTrader.

        Parameters
        ----------
        broker_name : str, optional
            The broker(s) to connect to for trade execution. The default is 'futures'.

        mode : str, necessary
            The trading mode of the system. There are 'backtest', 'virtualtrading', 'realtrading'.

        enter_license:str,necessary
            The license of yours.

        account:str,necessary
            Your account number.

        password:str,necessary
            Your account password

        trade_type : str, optional
            Whether the trade across days or within a day. There are 'across' and 'within'. The default is 'within'.

        Returns
        -------
        None
        """
        self.broker_name = broker_name
        self.mode = mode
        self.license = enter_license
        self.account = account
        self.password = password
        self.trade_type = trade_type

        if self.trade_type == 'within':
            self.across = False
        elif self.trade_type == 'across':
            self.across = True
        else:
            raise ValueError("Invalid trade type")

        if self.mode == 'realtrading':
            self.fc_code = 'rh'
        elif self.mode == 'virtualtrading':
            self.fc_code = 'simnow'
        else:
            raise ValueError("Invalid mode")

        supported_brokers = ['futures']
        if self.broker_name not in supported_brokers:
            raise ValueError("Unsupported broker")
        if self.broker_name == 'futures':
            self.broker = Futures(
                enter_license=self.license,
                fc_code=self.fc_code,
                account=self.account,
                password=self.password
            )

    def set_strategy(
        self,
        strategy_config_filename: str = None
    ) -> None:
        """Adds a strategy to LZCTrader.

        Parameters
        ----------
        strategy_config_filename : str, optional
            The prefix of the yaml strategy configuration file, located in
            home_dir/strategies_config. The default is None.

        Returns
        -------
        None
            The strategy will be added to the active AutoTrader instance.

        Available interval time format:
            days / day / d
            hours / hour / hr / h
            minutes / minute / min / m
            seconds / second / sec / s

        """
        config_file_path = os.path.join(
            self.root_dir, "strategies_config", strategy_config_filename
        )
        strategy_config = read_yaml(config_file_path + ".yaml")

        # Check for other required keys
        required_keys = ["CLASS", "INTERVAL", "WATCHLIST"]
        for key in required_keys:
            if key not in strategy_config:
                print(
                    f"Please include the '{key}' key in your strategy configuration."
                )
                sys.exit(0)

        # Set timestep from strategy strategies_config
        try:
            granularity = pd.Timedelta(
                strategy_config["INTERVAL"]
            ).to_pytimedelta()
        except Exception as e:
            print(f"Error parsing time interval '{strategy_config['INTERVAL']}': {str(e)}")
            sys.exit(1)

        self.strategy_config = strategy_config
        self.strategy_timestep = granularity.total_seconds()

        # 策略文件路径
        strategies_file_path = os.path.join(self.root_dir, "strategies", strategy_config_filename)
        strategy_module_name = Path(strategy_config_filename).stem  # 去除扩展名得到模块名
        class_name = strategy_config["CLASS"]

        try:
            # 动态加载模块
            strategy_file_path_py = os.path.join(
                self.root_dir, "strategies", f"{strategy_config_filename}.py"
            )
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(strategy_module_name, strategy_file_path_py)
            strategy_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(strategy_module)

            # 获取类
            if not hasattr(strategy_module, class_name):
                raise AttributeError(f"Class '{class_name}' not found in module '{strategy_module_name}'")

            strategy_class = getattr(strategy_module, class_name)

            # 实例化策略
            self.strategy_class = strategy_class

        except Exception as e:
            print(f"Error initializing strategy: {str(e)}")
            sys.exit(1)

    def set_preliminary_select(
        self,
        preliminary_select_filename: str = None
    ) -> None:
        """Adds a preliminary_select strategy to LZCTrader.

        Parameters
        ----------
        preliminary_select_filename : str, optional
            The prefix of the yaml strategy configuration file, located in
            home_dir/strategies_config. The default is None.

        Returns
        -------
        None
            The strategy will be added to the active AutoTrader instance.

        Available interval time format:
            days / day / d
            hours / hour / hr / h
            minutes / minute / min / m
            seconds / second / sec / s

        """
        preliminary_select_file_path = os.path.join(
            self.root_dir, "preliminary_config", preliminary_select_filename
        )
        preliminary_select_config = read_yaml(preliminary_select_file_path + ".yaml")

        preliminary_select_module_name = Path(preliminary_select_filename).stem  # 去除扩展名得到模块名
        class_name = preliminary_select_config["CLASS"]

        try:
            # 动态加载模块
            preliminary_select_file_path_py = os.path.join(
                self.root_dir, "preliminary", f"{preliminary_select_filename}.py"
            )
            spec = importlib.util.spec_from_file_location(preliminary_select_module_name, preliminary_select_file_path_py)
            preliminary_select_module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(preliminary_select_module)

            # 获取类
            if not hasattr(preliminary_select_module, class_name):
                raise AttributeError(f"Class '{class_name}' not found in module '{preliminary_select_module}'")

            preliminary_select_class = getattr(preliminary_select_module, class_name)

            # 实例化策略
            self.preliminary_select = preliminary_select_class(self.broker)

        except Exception as e:
            print(f"Error initializing preliminary strategy: {str(e)}")
            sys.exit(1)

    def run(
        self
    ) -> None:
        """
        Run LZCTrader.
        """
        current_time = datetime.now().hour
        if 7 < current_time < 16:
            self.market_time_type = 'morning'
        elif current_time > 19 or current_time < 4:
            self.market_time_type = 'night'
        else:
            raise ValueError("Invalid trade time")

        watchlist = self.strategy_config['WATCHLIST']
        tradelist = self.preliminary_select.generate_tradelist(watchlist)
        for instrument in tradelist:
            instrument_type = extract_letters(instrument)
            try:
                instrument_config = self.instrument_map[f'{instrument_type}']
            except KeyError:
                raise ValueError("Unsupported instrument")
            exchange = instrument_config['exchange']
            morning = instrument_config['morning']
            night = instrument_config['night']
            stop = instrument_config['stop']

            if self.market_time_type == 'morning':
                if not morning:
                    continue
            else:
                if not night:
                    continue

        bot = LZCBot(
            strategy=self.strategy_class(instrument=instrument,
                                         exchange=exchange,
                                         parameters=self.strategy_config['PARAMETERS'],
                                         broker=self.broker)
        )
        bot.run_thread = threading.Thread(target=self.real_loop, args=(bot,))
        bot.stop_flag = threading.Event()
        bot.stop_thread = threading.Thread(target=self.start_market_status_timer, args=(stop, bot))

        time.sleep(0.2)
        bot.run_thread.start()
        bot.stop_thread.start()
        self.bot_list.append(bot)

        # 首先收集所有需要等待的线程
        threads_to_wait = {bot.run_thread for bot in self.bot_list}

        while threads_to_wait:
            # 获取当前所有存活线程
            alive_threads = set(threading.enumerate())
            # 找出已经结束的线程
            finished_threads = threads_to_wait - alive_threads

            # 处理已结束的线程
            for thread in finished_threads:
                # 找到对应的bot
                for bot in self.bot_list:
                    if bot.run_thread is thread:
                        if not self.across:
                            self.broker.clear_positions(bot.instrument)
                            time.sleep(2)
                            print(f"Bot {bot.instrument} killed")
                        break
                threads_to_wait.remove(thread)

            # 避免忙等待
            if threads_to_wait:
                time.sleep(0.1)  # 短暂休眠减少CPU占用

        print("EXIT SYSTEM")
        sys.exit(0)

    def real_loop(
        self,
        bot: LZCBot
    ) -> None:
        """
        Run real trade loop.
        """
        while not bot.stop_flag.is_set():
            bot.update(self.fake_time)
            time.sleep(self.strategy_timestep)

    def start_market_status_timer(self, stoptime: list, bot: LZCBot):
        """Start market monitor"""

        def timer_loop():
            # target_times = [(14, 57), (22, 57)]
            target_times = stoptime

            while True:
                now = datetime.now()
                weekday = now.weekday()  # 周一=0，周日=6
    
                if weekday < 5:  # 周一到周五
                    for target_hour, target_min in target_times:
                        target_time = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
    
                        if target_time < now:
                            target_time += timedelta(days=1)
                        time_diff = (now - target_time).total_seconds()
                        #if abs(time_diff) < 60:
                try:
                    #self.stop_flag.set()
                    bot.stop_flag.set()
                    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Closing BOT")
                    time.sleep(80)
                            except AttributeError:
                                print("ERROR when closing market")
                else:
                    time.sleep(3600)  # 周末休眠1小时
                    continue

                time.sleep(30)  # 检查间隔

        # 启动线程（daemon=True 确保主进程退出时线程自动终止）
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()
        print(f"Bot {bot.instrument} monitor RUNNING")
