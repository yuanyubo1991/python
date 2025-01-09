import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import datetime as dt

my_database_token= 'xxxxxxxxxxxxxxx'
stock_code = '600900.SH'  # 股票代码
date_window = 1*365
ma_period = 5  # 设置均线周期，例如10日均线
x = 2  # 连续x天差值都为正（买入点）或负（卖出点）
y = 1  # 再往前y天差值都为负（买入点）或正（卖出点')

# 设置tushare的token
ts.set_token(my_database_token)
pro = ts.pro_api()

# 获取股票数据
def get_stock_data(stock_code, date_period, ma_period):
    today = dt.date.today()
    start_date = today - dt.timedelta(days=date_period)
    end_date = today - dt.timedelta(days=1)
    formatted_end_date = str(end_date).replace('-', '')
    formatted_start_date = str(start_date).replace('-', '')
    df = pro.daily(ts_code=stock_code, start_date=formatted_start_date, end_date=formatted_end_date)
    stock_name = df.iloc[0]['ts_code'].split('.')[0]  # 提取股票代码前缀
    df = df.sort_values('trade_date', ascending=True)
    df[f'MA{ma_period}'] = df['close'].rolling(window=ma_period).mean()  # 计算MAx
    print(stock_name)
    return df

# 判断均线拐点
def detect_turning_points(df, ma_period, x, y):
    df[f'MA{ma_period}_diff'] = df[f'MA{ma_period}'].diff()  # 计算MAx的差值
    
    # 判断买入点：连续x天差值都为正，且再往前y天差值都为负
    buy_condition = True
    for i in range(x):
        buy_condition &= (df[f'MA{ma_period}_diff'].shift(i) > 0)
    for i in range(x, x + y):
        buy_condition &= (df[f'MA{ma_period}_diff'].shift(i) < 0)
    df['buy_signal'] = buy_condition
    
    # 判断卖出点：连续x天差值都为负，且再往前y天差值都为正
    sell_condition = True
    for i in range(x):
        sell_condition &= (df[f'MA{ma_period}_diff'].shift(i) < 0)
    for i in range(x, x + y):
        sell_condition &= (df[f'MA{ma_period}_diff'].shift(i) > 0)
    df['sell_signal'] = sell_condition
    
    # 合并信号
    df['signal'] = 0
    df.loc[df['buy_signal'], 'signal'] = 1  # 买入信号
    df.loc[df['sell_signal'], 'signal'] = -1  # 卖出信号
    return df

# 用户手动指定买入点或卖出点
def add_manual_signals(df, manual_signals):
    for date, action in manual_signals.items():
        if date in df['trade_date'].values:
            if action == 'buy':
                df.loc[df['trade_date'] == date, 'signal'] = 1  # 标记为买入点
            elif action == 'sell':
                df.loc[df['trade_date'] == date, 'signal'] = -1  # 标记为卖出点
        else:
            print(f"Warning: Date {date} not found in data. Ignoring manual signal.")
    return df

# 过滤信号，确保买入和卖出成对出现，并加入价格限制
def filter_signals(df):
    position = 0  # 0表示没有持仓，1表示持有股票
    last_buy_price = None  # 上一个买入点的价格
    last_sell_price = None  # 上一个卖出点的价格
    signals = []
    filtered_signals = []  # 记录被过滤掉的买卖点
    operations = []  # 记录所有买卖操作
    
    for i in range(len(df)):
        if df.iloc[i]['signal'] == 1 and position == 0:  # 买入信号
            # 当前价格必须低于上一个卖出点的价格
            # if last_sell_price is None or df.iloc[i]['close'] < last_sell_price:
                signals.append('buy')
                position = 1
                last_buy_price = df.iloc[i]['close']  # 更新上一个买入点的价格
                operations.append(('buy', df.iloc[i]['trade_date'], last_buy_price))  # 记录买入操作
            #else:
            #    signals.append('hold')  # 不满足价格条件，忽略买入信号
             #   filtered_signals.append((df.iloc[i]['trade_date'], 'buy'))  # 记录被过滤的买入点
        elif df.iloc[i]['signal'] == -1 and position == 1:  # 卖出信号
            # 当前价格必须高于上一个买入点的价格
            if last_buy_price is None or df.iloc[i]['close'] > last_buy_price:
                signals.append('sell')
                position = 0
                last_sell_price = df.iloc[i]['close']  # 更新上一个卖出点的价格
                operations.append(('sell', df.iloc[i]['trade_date'], last_sell_price))  # 记录卖出操作
            else:
                signals.append('hold')  # 不满足价格条件，忽略卖出信号
                filtered_signals.append((df.iloc[i]['trade_date'], 'sell'))  # 记录被过滤的卖出点
        else:
            signals.append('hold')
            if df.iloc[i]['signal'] == 1:
                filtered_signals.append((df.iloc[i]['trade_date'], 'buy'))  # 记录被过滤的买入点
            elif df.iloc[i]['signal'] == -1:
                filtered_signals.append((df.iloc[i]['trade_date'], 'sell'))  # 记录被过滤的卖出点
    
    df['action'] = signals
    return df, filtered_signals, operations

# 计算并打印收益率
def calculate_returns(operations):
    total_return = 0  # 总收益率
    print("交易记录及收益率：")
    for i in range(0, len(operations), 2):
        if i + 1 >= len(operations):
            break  # 如果没有配对的卖出点，忽略最后一次买入
        buy_date, buy_price = operations[i][1], operations[i][2]
        sell_date, sell_price = operations[i + 1][1], operations[i + 1][2]
        return_percent = (sell_price - buy_price) / buy_price * 100  # 计算单次收益率
        total_return += return_percent  # 累加总收益率
        print(f"买入日期: {buy_date}, 买入价格: {buy_price:.2f}, 卖出日期: {sell_date}, 卖出价格: {sell_price:.2f}, 收益率: {return_percent:.2f}%")
    print(f"总收益率: {total_return:.2f}%")

# 检查今天是否是买卖点
def check_signal_on_date(df):
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    formatted_yesterday = str(yesterday).replace('-', '')

    if formatted_yesterday in df['trade_date'].values:
        nearest_date = formatted_yesterday
    else:
        # 找到小于指定日期的最大日期
        nearest_date = df[df['trade_date'] < formatted_yesterday]['trade_date'].max()
        if pd.isna(nearest_date):
            print(f"Warning: 日期 {formatted_yesterday} 不在数据库中，且没有更早的日期。")

    if nearest_date in df['trade_date'].values:
        signal = df.loc[df['trade_date'] == nearest_date, 'signal'].values[0]
        if signal == 1:
            print(f"上一交易日 {nearest_date} 出现买点信号，建议今天买入。")
        elif signal == -1:
            print(f"上一交易日 {nearest_date} 出现卖出信号，建议今天卖出。")
        else:
            print(f"上一交易日 {nearest_date} 没有出现信号，建议持仓不动。")
    else:
        print(f"Warning: 日期 {nearest_date} 无效。")


# 绘制曲线并标注买卖点
def plot_signals(df, ma_period, filtered_signals):
    plt.figure(figsize=(14, 10))
    
    # 创建两个子图
    ax1 = plt.subplot(2, 1, 1)  # 第一个子图：价格和均线
#    ax2 = plt.subplot(2, 1, 2)  # 第二个子图：差值

    # 绘制收盘价曲线
    ax1.plot(df['trade_date'], df['close'], label='Close Price', color='blue', alpha=0.7)
    
    # 绘制MAx均线
    ax1.plot(df['trade_date'], df[f'MA{ma_period}'], label=f'{ma_period}-Day MA', color='orange', linestyle='--')
    
    # 标注真正的买入点
    buy_points = df[df['action'] == 'buy']
    ax1.scatter(buy_points['trade_date'], buy_points['close'], color='green', marker='^', label='Buy Signal', s=100)
    
    # 标注真正的卖出点
    sell_points = df[df['action'] == 'sell']
    ax1.scatter(sell_points['trade_date'], sell_points['close'], color='red', marker='v', label='Sell Signal', s=100)
    
    # 标注被过滤掉的买卖点
    filtered_buy_dates = [date for date, action in filtered_signals if action == 'buy']
    filtered_sell_dates = [date for date, action in filtered_signals if action == 'sell']
    
    if filtered_buy_dates:
        ax1.scatter(filtered_buy_dates, df[df['trade_date'].isin(filtered_buy_dates)]['close'], 
                    color='yellow', marker='^', label='Filtered Buy Signal', s=100)
    if filtered_sell_dates:
        ax1.scatter(filtered_sell_dates, df[df['trade_date'].isin(filtered_sell_dates)]['close'], 
                    color='gray', marker='v', label='Filtered Sell Signal', s=100)
    
    # 设置第一个子图的属性
    ax1.set_title(f'Traffic Bank Stock Price with Buy/Sell Signals (MA{ma_period})')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 绘制差值曲线
#    ax2.plot(df['trade_date'], df[f'MA{ma_period}_diff'], label=f'MA{ma_period} Difference', color='purple', alpha=0.7)
    
    # 设置第二个子图的属性
#    ax2.set_title(f'MA{ma_period} Difference')
#    ax2.set_xlabel('Trade Date')
#    ax2.set_ylabel('Difference')
#    ax2.legend()
#    ax2.grid(alpha=0.3)
#    ax2.tick_params(axis='x', rotation=45)
    
    # 调整布局
    plt.tight_layout()
    plt.show()

# 主函数
def main():
    
    # 获取股票数据
    df = get_stock_data(stock_code, date_window, ma_period)
    
    # 检测均线拐点
    df = detect_turning_points(df, ma_period, x, y)
    
    # 用户手动指定买入点或卖出点
    manual_signals = {
    #    '20220110': 'buy',  # 指定2022年1月10日为买入点
    #    '20220120': 'sell',  # 指定2022年1月20日为卖出点
    }
    df = add_manual_signals(df, manual_signals)
    
    # 过滤信号
    df, filtered_signals, operations = filter_signals(df)
    
    # 输出交易信号
    #print(df[['trade_date', 'close', f'MA{ma_period}', f'MA{ma_period}_diff', 'signal', 'action']])
    
    # 计算并打印收益率
    calculate_returns(operations)
    
    # 检查指定日期是否是买卖点
    check_signal_on_date(df)

    
    # 绘制曲线并标注买卖点
    plot_signals(df, ma_period, filtered_signals)

if __name__ == "__main__":
    main()
