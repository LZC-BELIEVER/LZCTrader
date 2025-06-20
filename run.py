from LZCTrader.lzctrader import LZCTrader

zc = LZCTrader()
zc.configure(broker_name='futures',  # 期货券商接口，目前仅'future'一个选项
             mode='virtualtrading',  # 模式选择，虚拟为'virtualtrading'，实盘为'realtrading'
             enter_license='s3az29vbx5w3',  # 登录通行证。暂设为此值即可
             account='',  # 账号。虚拟盘中，为simnow投资者代码
             password='',  # 密码。sinnow密码
             trade_type='within')  # 交易类型，日内为'within'，日间为'across'。选择日内交易时，会在休市前平掉单日所有仓。日间则不会。

zc.set_preliminary_select('preliminary')  # 此处引入初筛策略。注意：必须和初筛策略py文件的命名严格一致。若无初筛策略，选择preliminary.py即可
zc.set_strategy('example')  # 此处引入策略。注意：必须和交易策略py文件的命名严格一致
zc.run()

# 此为系统主运行文件。以上的所有函数，均为必需。
