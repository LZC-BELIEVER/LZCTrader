import threading
import subprocess
import datetime
import time
import os
import signal
import psutil


def run_strategy():
    """执行 run.py 脚本"""
    python_exe = r"L:\Quantification\env\Scripts\python.exe"
    script_path = r"L:\Quantification\LeopardSeek\run.py"
    subprocess.Popen([python_exe, script_path], cwd=r"L:\Quantification\LeopardSeek")
#  注意！在此处，将python环境路径和项目路径改为你项目的对应路径

def wait_until_target(hour, minute=0):
    """等待直到目标时间"""
    while True:
        now = datetime.datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if now >= target:
            break
        delta = (target - now).total_seconds()
        time.sleep(min(delta, 10 if delta < 180 else 60))


def schedule_runner():
    """定时检测，到点自动启动 run.py"""
    start_times = [(9, 0), (21, 0)]  # 仅保留启动时间 (小时, 分钟)

    # 存储今天已经执行的操作
    executed_start_today = set()

    while True:
        now = datetime.datetime.now()
        weekday = now.weekday()  # 周一=0，周日=6

        if weekday < 5:  # 周一到周五
            # 处理启动时间
            for start_hour, start_min in start_times:
                if (start_hour, start_min) in executed_start_today:
                    continue

                wait_until_target(start_hour, start_min)

                now = datetime.datetime.now()
                if now.weekday() < 5 and now.hour == start_hour:
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} Launching run.py！")
                    t = threading.Thread(target=run_strategy)
                    t.start()
                    executed_start_today.add((start_hour, start_min))
        else:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Weekend Sleep 1 h ...")
            time.sleep(3600)

        # 每天凌晨清空标记
        if now.hour == 0 and (now.minute < 5 or (0, 0) not in executed_start_today):
            executed_start_today.clear()

        time.sleep(30)  # 避免空循环占CPU


if __name__ == '__main__':
    print("Timer started：Work days 9:00 / 21:00 run sys")
    schedule_runner()