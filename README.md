# LZCTrader 使用文档

## 简介
- LZCTrader是面向广大量化策略研究人员所使用的直连交易客户端系统，系统可以实现获取期货行情数据并根据自定义策略实现自动化交易。
- 系统参考[AutoTrader](https://github.com/kieran-mackle/AutoTrader)架构实现。现在只支持中国大陆期货市场多期货品种交易。
- Author: LZC from XJTU (Solo)

## 文件结构
- **API**:券商接口模块
- **brokers**:券商定义模块
- **LZCTrader**：系统主模块
- **preliminary**:初筛策略模块
- **preliminary_config**:初筛策略配置模块
- **strategies**:交易策略模块
- **strategies_config**:交易策略配置模块
- **run.py**:系统单次运行文件
- **day_and_night.py**:系统交易日定时运行文件

## 部署方法
1. 下载PyCharm，并最好准备一个3.12以上的Python环境
2. 在环境中下载(pip)系统运行所需的所有库文件
3. 仿照strategies文件夹下的example.py，写一个属于你自己的策略文件。并仿照strategies_config文件夹下的example.yaml，完成策略的配置文件。注意！策略文件和配置文件的文件名必须完全一致，最好为全部小写。
4. 在run.py中，配置configue，set_preliminary_select以及set_strategy，配置方法见注释。接着，在day_and_night.py中run_strategy()函数中按照注释修改运行路径。 
5. 运行day_and_night.py
6. 支持的交易品种见LZCTrader/tools/instrument_map.yaml
7. 当收到服务器端 message='ready' 信息时，表示系统已经开始正常运行。系统无额外运行界面，下单成功时，会显示单号。


