from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
import sys
import io
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import tushare as ts
import matplotlib.ticker as ticker
import os
import numpy as np
np.NaN = np.nan  # 将 NaN 替换为 nan
import pandas_ta as ta  # 使用 pandas_ta 替代 TA-Lib
from kivy.uix.label import Label

# 设置 tushare 的 token
my_database_token = '63324699e6c373c9f2cf6eaac850bd161b9fd31bb8d1f546316348f7'
ts.set_token(my_database_token)
pro = ts.pro_api()

# 获取股票数据
def get_stock_data(stock_code, date_period):
    today = dt.date.today()
    start_date = today - dt.timedelta(days=date_period)
    end_date = today - dt.timedelta(days=1)
    formatted_end_date = str(end_date).replace('-', '')
    formatted_start_date = str(start_date).replace('-', '')
    df = pro.daily(ts_code=stock_code, start_date=formatted_start_date, end_date=formatted_end_date)
    df = df.sort_values('trade_date', ascending=True)
    return df

# 计算技术指标
def calculate_indicators(df):
    # 计算 MACD、RSI 和 KDJ 指标
    df.ta.macd(append=True)
    df.ta.rsi(append=True)
    df.ta.stoch(append=True)
    df.fillna(0, inplace=True)  # 将 NaN 替换为 0
    return df

# 判断买卖点
def detect_signals(df):
    df['signal'] = 0  # 初始化信号列

    # MACD 买入信号：MACD 线从下向上穿过信号线
    df['MACD_buy'] = (df['MACD_12_26_9'] > df['MACDs_12_26_9']) & (df['MACD_12_26_9'].shift(1) < df['MACDs_12_26_9'].shift(1))
    
    # RSI 买入信号：RSI 低于 30（超卖）
    df['RSI_buy'] = df['RSI_14'] < 30
    
    # KDJ 买入信号：K 线从下向上穿过 D 线
    df['KDJ_buy'] = (df['STOCHk_14_3_3'] > df['STOCHd_14_3_3']) & (df['STOCHk_14_3_3'].shift(1) < df['STOCHd_14_3_3'].shift(1))
    
    # 检查前五个交易日内是否有另外两个指标中的至少一个出现过买入信号
    df['MACD_buy_prev_5'] = df['MACD_buy'].rolling(window=5, min_periods=1).max()
    df['RSI_buy_prev_5'] = df['RSI_buy'].rolling(window=5, min_periods=1).max()
    df['KDJ_buy_prev_5'] = df['KDJ_buy'].rolling(window=5, min_periods=1).max()
    
    # 综合买入信号：今天任意一个指标出现买入信号，并且前五个交易日内另外两个指标中至少一个也出现过买入信号
    df['buy_signal'] = (
        (df['MACD_buy'] & ((df['RSI_buy_prev_5'] == 1) | (df['KDJ_buy_prev_5'] == 1))) |
        (df['RSI_buy'] & ((df['MACD_buy_prev_5'] == 1) | (df['KDJ_buy_prev_5'] == 1))) |
        (df['KDJ_buy'] & ((df['MACD_buy_prev_5'] == 1) | (df['RSI_buy_prev_5'] == 1)))
    )
    
    # MACD 卖出信号：MACD 线从上向下穿过信号线
    df['MACD_sell'] = (df['MACD_12_26_9'] < df['MACDs_12_26_9']) & (df['MACD_12_26_9'].shift(1) > df['MACDs_12_26_9'].shift(1))
    
    # RSI 卖出信号：RSI 高于 70（超买）
    df['RSI_sell'] = df['RSI_14'] > 70
    
    # KDJ 卖出信号：K 线从上向下穿过 D 线
    df['KDJ_sell'] = (df['STOCHk_14_3_3'] < df['STOCHd_14_3_3']) & (df['STOCHk_14_3_3'].shift(1) > df['STOCHd_14_3_3'].shift(1))
    
    # 综合卖出信号：MACD、RSI 或 KDJ 任一个提示卖出
    df['sell_signal'] = df['MACD_sell'] | df['RSI_sell'] | df['KDJ_sell']
    
    # 标记买入和卖出信号
    df.loc[df['buy_signal'], 'signal'] = 1
    df.loc[df['sell_signal'], 'signal'] = -1
    
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
def filter_signals(df, buy_price_limit, sell_price_limit, pair_limit):
    position = 0  # 0 表示没有持仓，1 表示持有股票
    last_buy_price = None  # 上一个买入点的价格
    last_sell_price = None  # 上一个卖出点的价格
    signals = []
    filtered_signals = []  # 记录被过滤掉的买卖点
    operations = []  # 记录所有买卖操作

    for i in range(len(df)):
        if df.iloc[i]['signal'] == 1 and (position == 0 or pair_limit == 'NO'):  # 买入信号
            if buy_price_limit == 'YES':
                # 当前价格必须低于上一个卖出点的价格
                if last_sell_price is None or df.iloc[i]['close'] < last_sell_price:
                    signals.append('buy')
                    position = 1
                    last_buy_price = df.iloc[i]['close']  # 更新上一个买入点的价格
                    operations.append(('buy', df.iloc[i]['trade_date'], last_buy_price))  # 记录买入操作
                else:
                    signals.append('hold')  # 不满足价格条件，忽略买入信号
                    filtered_signals.append((df.iloc[i]['trade_date'], 'buy'))  # 记录被过滤的买入点
            else:
                signals.append('buy')
                position = 1
                last_buy_price = df.iloc[i]['close']  # 更新上一个买入点的价格
                operations.append(('buy', df.iloc[i]['trade_date'], last_buy_price))  # 记录买入操作
        elif df.iloc[i]['signal'] == -1 and (position == 1 or pair_limit == 'NO'):  # 卖出信号
            if sell_price_limit == 'YES':
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
                signals.append('sell')
                position = 0
                last_sell_price = df.iloc[i]['close']  # 更新上一个卖出点的价格
                operations.append(('sell', df.iloc[i]['trade_date'], last_sell_price))  # 记录卖出操作
        else:
            signals.append('hold')
            if df.iloc[i]['signal'] == 1:
                filtered_signals.append((df.iloc[i]['trade_date'], 'buy'))  # 记录被过滤的买入点
            elif df.iloc[i]['signal'] == -1:
                filtered_signals.append((df.iloc[i]['trade_date'], 'sell'))  # 记录被过滤的卖出点

    df['action'] = signals
    return df, filtered_signals, operations

# 计算并返回总交易次数、总收益率和平均年化收益率
def calculate_returns(operations, start_date, end_date):
    if not operations:
        return 0, 0, 0  # 如果没有交易记录，返回 0

    total_return = 0  # 总收益率
    total_operations = len(operations) // 2  # 总交易次数（买入和卖出成对出现）

    # 计算总收益率
    for i in range(0, len(operations), 2):
        if i + 1 >= len(operations):
            break  # 如果没有配对的卖出点，忽略最后一次买入
        buy_price = operations[i][2]
        sell_price = operations[i + 1][2]
        return_percent = (sell_price - buy_price) / buy_price * 100  # 计算单次收益率
        total_return += return_percent  # 累加总收益率

    # 计算平均年化收益率
    if total_operations > 0:
        total_days = (end_date - start_date).days
        if total_days <= 0:
            print("Warning: 投资天数小于等于 0，无法计算年化收益率。")
            return total_operations, total_return, 0

        # 计算年化收益率
        average_annual_return = (1 + total_return / 100) ** (365 / total_days) - 1
        average_annual_return_percent = average_annual_return * 100
    else:
        average_annual_return_percent = 0

    return total_operations, total_return, average_annual_return_percent

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
            return f"上一交易日 {nearest_date} 出现买点信号，建议今天买入。"
        elif signal == -1:
            return f"上一交易日 {nearest_date} 出现卖出信号，建议今天卖出。"
        else:
            return f"上一交易日 {nearest_date} 没有出现信号，建议持仓不动。"
    else:
        return f"Warning: 日期 {nearest_date} 无效。"

# 绘制曲线并标注买卖点
def plot_signals(df, filtered_signals, stock_code):
    plt.figure(figsize=(14, 10))
    
    # 创建子图
    ax1 = plt.subplot(1, 1, 1)  # 价格和均线

    # 绘制收盘价曲线
    ax1.plot(df['trade_date'], df['close'], label='Close Price', color='gray', alpha=0.7)
    
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
                    color='pink', marker='^', label='Filtered Buy Signal', s=100)
    if filtered_sell_dates:
        ax1.scatter(filtered_sell_dates, df[df['trade_date'].isin(filtered_sell_dates)]['close'], 
                    color='gray', marker='v', label='Filtered Sell Signal', s=100)
    
    # 设置子图的属性
    ax1.set_title(f'{stock_code} Stock Price with Buy/Sell Signals')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    ax1.xaxis.set_major_locator(ticker.MultipleLocator(10))

    # 调整布局
    plt.tight_layout()
    plt.savefig('temp_plot.png')
    plt.close()

# 主函数
def main(stock_code, date_period, buy_price_limit, sell_price_limit, pair_limit):
    # 获取股票数据
    df = get_stock_data(stock_code, date_period)
    
    # 计算技术指标
    df = calculate_indicators(df)
    
    # 检测买卖信号
    df = detect_signals(df)
    
    # 用户手动指定买入点或卖出点
    manual_signals = {
    #    '20220110': 'buy',  # 指定2022年1月10日为买入点
    #    '20220120': 'sell',  # 指定2022年1月20日为卖出点
    }
    df = add_manual_signals(df, manual_signals)
    
    # 过滤信号
    df, filtered_signals, operations = filter_signals(df, buy_price_limit, sell_price_limit, pair_limit)
    
    # 计算起始日期和结束日期
    today = dt.date.today()
    start_date = today - dt.timedelta(days=date_period)
    end_date = today - dt.timedelta(days=1)  # 结束日期为昨天

    # 计算总交易次数、总收益率和平均年化收益率
    total_operations, total_return, average_annual_return = calculate_returns(operations, start_date, end_date)
    
    # 检查指定日期是否是买卖点
    signal_info = check_signal_on_date(df)
    
    # 绘制曲线并标注买卖点
    plot_signals(df, filtered_signals, stock_code)

    # 返回结果
    return total_operations, total_return, average_annual_return, signal_info


# 在 InputScreen 类的 __init__ 方法中移除“下一页”按钮的初始化
class InputScreen(Screen):
    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=0, padding=0)

        # 左侧布局（输入框和按钮）
        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=0)

        # 股票代码输入框及其提示词
        stock_code_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        stock_code_label = Label(text='股票代码:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.stock_name_input = TextInput(
            text='600900.SH', 
            hint_text='股票代码 (如 600900.SH)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        stock_code_layout.add_widget(stock_code_label)
        stock_code_layout.add_widget(self.stock_name_input)
        left_layout.add_widget(stock_code_layout)

        # 回溯天数输入框及其提示词
        date_period_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        date_period_label = Label(text='回溯天数:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.date_period_input = TextInput(
            text='365', 
            hint_text='回溯天数 (如 365)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        date_period_layout.add_widget(date_period_label)
        date_period_layout.add_widget(self.date_period_input)
        left_layout.add_widget(date_period_layout)

        # 买入价格限制按钮及其提示词
        buy_price_limit_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        buy_price_limit_label = Label(text='限制买入价 < 卖出价:', size_hint_x=1, font_name='STKAITI', font_size=30, color='orange')
        self.buy_price_limit_button = Button(
            text='NO',  # 默认值
            size_hint_x=0.7,
            font_name='STKAITI',
            font_size=30,
            background_color='orange'
        )
        self.buy_price_limit_button.bind(on_press=self.toggle_buy_price_limit)
        buy_price_limit_layout.add_widget(buy_price_limit_label)
        buy_price_limit_layout.add_widget(self.buy_price_limit_button)
        left_layout.add_widget(buy_price_limit_layout)

        # 卖出价格限制按钮及其提示词
        sell_price_limit_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        sell_price_limit_label = Label(text='限制卖出价 > 买入价:', size_hint_x=1, font_name='STKAITI', font_size=30, color='orange')
        self.sell_price_limit_button = Button(
            text='YES',  # 默认值
            size_hint_x=0.7,
            font_name='STKAITI',
            font_size=30,
            background_color='orange'
        )
        self.sell_price_limit_button.bind(on_press=self.toggle_sell_price_limit)
        sell_price_limit_layout.add_widget(sell_price_limit_label)
        sell_price_limit_layout.add_widget(self.sell_price_limit_button)
        left_layout.add_widget(sell_price_limit_layout)

        # 买卖点成对限制按钮及其提示词
        pair_limit_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        pair_limit_label = Label(text='限制买卖点成对出现:', size_hint_x=1, font_name='STKAITI', font_size=30, color='orange')
        self.pair_limit_button = Button(
            text='NO',  # 默认值
            size_hint_x=0.7,
            font_name='STKAITI',
            font_size=30,
            background_color='orange'
        )
        self.pair_limit_button.bind(on_press=self.toggle_pair_limit)
        pair_limit_layout.add_widget(pair_limit_label)
        pair_limit_layout.add_widget(self.pair_limit_button)
        left_layout.add_widget(pair_limit_layout)

        # 运行按钮
        self.run_button = Button(
            text='点击运行', 
            size_hint_y=10, 
            height=40, 
            font_name='STKAITI', 
            font_size=25, 
            background_color='red'
        )
        self.run_button.bind(on_press=self.run_script)
        left_layout.add_widget(self.run_button)

        # 右侧布局（结果显示标签）
        right_layout = BoxLayout(orientation='vertical', size_hint_x=1, spacing=10)

        # 结果显示标签
        self.result_label = Label(
            text='Developed by 玉帛书影', 
            size_hint_y=10, 
            height=100, 
            font_name='STKAITI', 
            font_size=30, 
            text_size=(None, None), 
            halign='center', 
            valign='middle'
        )
        right_layout.add_widget(self.result_label)

        # 上一交易日信号标签
        self.signal_label = Label(
            text='', 
            size_hint_y=10, 
            height=100, 
            font_name='STKAITI', 
            font_size=30, 
            text_size=(None, None), 
            halign='center', 
            valign='middle'
        )
        right_layout.add_widget(self.signal_label)

        # 将左右布局添加到主布局
        self.layout.add_widget(left_layout)
        self.layout.add_widget(right_layout)

        # 添加布局到页面
        self.add_widget(self.layout)

    def toggle_buy_price_limit(self, instance):
        # 切换买入价格限制
        if self.buy_price_limit_button.text == 'NO':
            self.buy_price_limit_button.text = 'YES'
        else:
            self.buy_price_limit_button.text = 'NO'

    def toggle_sell_price_limit(self, instance):
        # 切换卖出价格限制
        if self.sell_price_limit_button.text == 'NO':
            self.sell_price_limit_button.text = 'YES'
        else:
            self.sell_price_limit_button.text = 'NO'

    def toggle_pair_limit(self, instance):
        # 切换买卖点成对限制
        if self.pair_limit_button.text == 'NO':
            self.pair_limit_button.text = 'YES'
        else:
            self.pair_limit_button.text = 'NO'

    def run_script(self, instance):
        # 获取输入值
        stock_code = self.stock_name_input.text
        date_period = int(self.date_period_input.text)
        buy_price_limit = self.buy_price_limit_button.text
        sell_price_limit = self.sell_price_limit_button.text
        pair_limit = self.pair_limit_button.text

        # 运行主函数
        total_operations, total_return, average_annual_return, signal_info = main(stock_code, date_period, buy_price_limit, sell_price_limit, pair_limit)

        # 更新结果显示标签
        result_text = f"总交易次数: {total_operations}\n总收益率: {total_return:.2f}%\n平均年化收益率: {average_annual_return:.2f}%"
        self.result_label.text = result_text

        # 更新上一交易日信号标签
        self.signal_label.text = signal_info

        # 更新图片（但不跳转）
        self.manager.get_screen('image_screen').update_image()

        # 动态添加“下一页”按钮
        if not hasattr(self, 'next_button'):
            self.next_button = Button(
                text='查看买卖点', 
                size_hint_y=None, 
                height=40, 
                font_name='STKAITI', 
                font_size=30, 
                background_color='green'
            )
            self.next_button.bind(on_press=self.go_to_image_screen)
            self.layout.children[0].add_widget(self.next_button)  # 将按钮添加到左侧布局

    def go_to_image_screen(self, instance):
        # 跳转到第二页
        self.manager.current = 'image_screen'

# 定义第二页（图片页面）
class ImageScreen(Screen):
    def __init__(self, **kwargs):
        super(ImageScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=0, padding=0)

        # 图片显示
        self.image_widget = Image(size_hint_y=None, height=1200, keep_ratio=True, allow_stretch=True, pos_hint={'x': 0, 'y': 0})
        self.layout.add_widget(self.image_widget)

        # 返回按钮
        self.back_button = Button(text='返回', size_hint_y=None, height=40, font_size=30, font_name='STKAITI', background_color='green')
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        # 添加布局到页面
        self.add_widget(self.layout)

    def update_image(self):
        # 更新图片
        if os.path.exists('temp_plot.png'):
            self.image_widget.source = 'temp_plot.png'
            self.image_widget.reload()

    def go_back(self, instance):
        # 返回到第一页
        self.manager.current = 'input_screen'

# 定义应用程序
class StockApp(App):
    def build(self):
        # 创建 ScreenManager
        self.screen_manager = ScreenManager()

        # 添加第一页（输入页面）
        self.input_screen = InputScreen(name='input_screen')
        self.screen_manager.add_widget(self.input_screen)

        # 添加第二页（图片页面）
        self.image_screen = ImageScreen(name='image_screen')
        self.screen_manager.add_widget(self.image_screen)

        return self.screen_manager

if __name__ == "__main__":
    # 设置中文字体
    from kivy.core.text import LabelBase
    LabelBase.register(name='STKAITI', fn_regular='STKAITI.TTF')  # 确保 STKAITI.TTF 文件在项目目录中
    StockApp().run()
