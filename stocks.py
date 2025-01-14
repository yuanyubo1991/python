from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
import datetime as dt
import pandas as pd
import tushare as ts
import numpy as np
np.NaN = np.nan  # 将 NaN 替换为 nan
import pandas_ta as ta

# 沪深300成分股股票代码和名称
HS300_STOCKS = {
    '000001.SZ': '平安银行', '000002.SZ': '万科A', '000063.SZ': '中兴通讯', '000100.SZ': 'TCL科技', '000157.SZ': '中联重科',
    '000166.SZ': '申万宏源', '000301.SZ': '东方盛虹', '000333.SZ': '美的集团', '000338.SZ': '潍柴动力', '000408.SZ': '藏格矿业',
    '000425.SZ': '徐工机械', '000538.SZ': '云南白药', '000568.SZ': '泸州老窖', '000596.SZ': '古井贡酒', '000617.SZ': '中油资本',
    '000625.SZ': '长安汽车', '000630.SZ': '铜陵有色', '000651.SZ': '格力电器', '000661.SZ': '长春高新', '000708.SZ': '中信特钢',
    '000725.SZ': '京东方A', '000768.SZ': '中航西飞', '000776.SZ': '广发证券', '000786.SZ': '北新建材', '000792.SZ': '盐湖股份',
    '000800.SZ': '一汽解放', '000807.SZ': '云铝股份', '000858.SZ': '五粮液', '000876.SZ': '新希望', '000895.SZ': '双汇发展',
    '000938.SZ': '紫光股份', '000963.SZ': '华东医药', '000975.SZ': '山金国际', '000977.SZ': '浪潮信息', '000983.SZ': '山西焦煤',
    '000999.SZ': '华润三九', '001289.SZ': '龙源电力', '001965.SZ': '招商公路', '001979.SZ': '招商蛇口', '002001.SZ': '新和成',
    '002007.SZ': '华兰生物', '002027.SZ': '分众传媒', '002028.SZ': '思源电气', '002049.SZ': '紫光国微', '002050.SZ': '三花智控',
    '002074.SZ': '国轩高科', '002129.SZ': 'TCL中环', '002142.SZ': '宁波银行', '002179.SZ': '中航光电', '002180.SZ': '纳思达',
    '002230.SZ': '科大讯飞', '002236.SZ': '大华股份', '002241.SZ': '歌尔股份', '002252.SZ': '上海莱士', '002271.SZ': '东方雨虹',
    '002304.SZ': '洋河股份', '002311.SZ': '海大集团', '002352.SZ': '顺丰控股', '002371.SZ': '北方华创', '002415.SZ': '海康威视',
    '002422.SZ': '科伦药业', '002459.SZ': '晶澳科技', '002460.SZ': '赣锋锂业', '002463.SZ': '沪电股份', '002466.SZ': '天齐锂业',
    '002475.SZ': '立讯精密', '002493.SZ': '荣盛石化', '002555.SZ': '三七互娱', '002594.SZ': '比亚迪', '002601.SZ': '龙佰集团',
    '002648.SZ': '卫星化学', '002709.SZ': '天赐材料', '002714.SZ': '牧原股份', '002736.SZ': '国信证券', '002812.SZ': '恩捷股份',
    '002916.SZ': '深南电路', '002920.SZ': '德赛西威', '002938.SZ': '鹏鼎控股', '003816.SZ': '中国广核', '300014.SZ': '亿纬锂能',
    '300015.SZ': '爱尔眼科', '300033.SZ': '同花顺', '300059.SZ': '东方财富', '300122.SZ': '智飞生物', '300124.SZ': '汇川技术',
    '300274.SZ': '阳光电源', '300308.SZ': '中际旭创', '300316.SZ': '晶盛机电', '300347.SZ': '泰格医药', '300394.SZ': '天孚通信',
    '300408.SZ': '三环集团', '300413.SZ': '芒果超媒', '300418.SZ': '昆仑万维', '300433.SZ': '蓝思科技', '300442.SZ': '润泽科技',
    '300450.SZ': '先导智能', '300498.SZ': '温氏股份', '300502.SZ': '新易盛', '300628.SZ': '亿联网络', '300661.SZ': '圣邦股份',
    '300750.SZ': '宁德时代', '300759.SZ': '康龙化成', '300760.SZ': '迈瑞医疗', '300782.SZ': '卓胜微', '300832.SZ': '新产业',
    '300896.SZ': '爱美客', '300979.SZ': '华利集团', '300999.SZ': '金龙鱼', '301269.SZ': '华大九天', '600000.SH': '浦发银行',
    '600009.SH': '上海机场', '600010.SH': '包钢股份', '600011.SH': '华能国际', '600015.SH': '华夏银行', '600016.SH': '民生银行',
    '600018.SH': '上港集团', '600019.SH': '宝钢股份', '600023.SH': '浙能电力', '600025.SH': '华能水电', '600026.SH': '中远海能',
    '600027.SH': '华电国际', '600028.SH': '中国石化', '600029.SH': '南方航空', '600030.SH': '中信证券', '600031.SH': '三一重工',
    '600036.SH': '招商银行', '600039.SH': '四川路桥', '600048.SH': '保利发展', '600050.SH': '中国联通', '600061.SH': '国投资本',
    '600066.SH': '宇通客车', '600085.SH': '同仁堂', '600089.SH': '特变电工', '600104.SH': '上汽集团', '600111.SH': '北方稀土',
    '600115.SH': '中国东航', '600150.SH': '中国船舶', '600160.SH': '巨化股份', '600161.SH': '天坛生物', '600176.SH': '中国巨石',
    '600183.SH': '生益科技', '600188.SH': '兖矿能源', '600196.SH': '复星医药', '600219.SH': '南山铝业', '600233.SH': '圆通速递',
    '600276.SH': '恒瑞医药', '600309.SH': '万华化学', '600332.SH': '白云山', '600346.SH': '恒力石化', '600362.SH': '江西铜业',
    '600372.SH': '中航机载', '600377.SH': '宁沪高速', '600406.SH': '国电南瑞', '600415.SH': '小商品城', '600426.SH': '华鲁恒升',
    '600436.SH': '片仔癀', '600438.SH': '通威股份', '600460.SH': '士兰微', '600482.SH': '中国动力', '600489.SH': '中金黄金',
    '600515.SH': '海南机场', '600519.SH': '贵州茅台', '600547.SH': '山东黄金', '600570.SH': '恒生电子', '600584.SH': '长电科技',
    '600585.SH': '海螺水泥', '600588.SH': '用友网络', '600600.SH': '青岛啤酒', '600660.SH': '福耀玻璃', '600674.SH': '川投能源',
    '600690.SH': '海尔智家', '600741.SH': '华域汽车', '600745.SH': '闻泰科技', '600760.SH': '中航沈飞', '600795.SH': '国电电力',
    '600803.SH': '新奥股份', '600809.SH': '山西汾酒', '600837.SH': '海通证券', '600845.SH': '宝信软件', '600875.SH': '东方电气',
    '600886.SH': '国投电力', '600887.SH': '伊利股份', '600893.SH': '航发动力', '600900.SH': '长江电力', '600905.SH': '三峡能源',
    '600918.SH': '中泰证券', '600919.SH': '江苏银行', '600926.SH': '杭州银行', '600938.SH': '中国海油', '600941.SH': '中国移动',
    '600958.SH': '东方证券', '600989.SH': '宝丰能源', '600999.SH': '招商证券', '601006.SH': '大秦铁路', '601009.SH': '南京银行',
    '601012.SH': '隆基绿能', '601021.SH': '春秋航空', '601059.SH': '信达证券', '601066.SH': '中信建投', '601088.SH': '中国神华',
    '601100.SH': '恒立液压', '601111.SH': '中国国航', '601117.SH': '中国化学', '601127.SH': '赛力斯', '601136.SH': '首创证券',
    '601138.SH': '工业富联', '601166.SH': '兴业银行', '601169.SH': '北京银行', '601186.SH': '中国铁建', '601211.SH': '国泰君安',
    '601225.SH': '陕西煤业', '601229.SH': '上海银行', '601236.SH': '红塔证券', '601238.SH': '广汽集团', '601288.SH': '农业银行',
    '601318.SH': '中国平安', '601319.SH': '中国人保', '601328.SH': '交通银行', '601336.SH': '新华保险', '601360.SH': '三六零',
    '601377.SH': '兴业证券', '601390.SH': '中国中铁', '601398.SH': '工商银行', '601600.SH': '中国铝业', '601601.SH': '中国太保',
    '601607.SH': '上海医药', '601618.SH': '中国中冶', '601628.SH': '中国人寿', '601633.SH': '长城汽车', '601658.SH': '邮储银行',
    '601668.SH': '中国建筑', '601669.SH': '中国电建', '601688.SH': '华泰证券', '601689.SH': '拓普集团', '601698.SH': '中国卫通',
    '601699.SH': '潞安环能', '601728.SH': '中国电信', '601766.SH': '中国中车', '601788.SH': '光大证券', '601799.SH': '星宇股份',
    '601800.SH': '中国交建', '601808.SH': '中海油服', '601816.SH': '京沪高铁', '601818.SH': '光大银行', '601838.SH': '成都银行',
    '601857.SH': '中国石油', '601865.SH': '福莱特', '601868.SH': '中国能建', '601872.SH': '招商轮船', '601877.SH': '正泰电器',
    '601878.SH': '浙商证券', '601881.SH': '中国银河', '601888.SH': '中国中免', '601898.SH': '中煤能源', '601899.SH': '紫金矿业',
    '601901.SH': '方正证券', '601916.SH': '浙商银行', '601919.SH': '中远海控', '601939.SH': '建设银行', '601985.SH': '中国核电',
    '601988.SH': '中国银行', '601989.SH': '中国重工', '601995.SH': '中金公司', '601998.SH': '中信银行', '603019.SH': '中科曙光',
    '603195.SH': '公牛集团', '603259.SH': '药明康德', '603260.SH': '合盛硅业', '603288.SH': '海天味业', '603296.SH': '华勤技术',
    '603369.SH': '今世缘', '603392.SH': '万泰生物', '603501.SH': '韦尔股份', '603659.SH': '璞泰来', '603799.SH': '华友钴业',
    '603806.SH': '福斯特', '603833.SH': '欧派家居', '603986.SH': '兆易创新', '603993.SH': '洛阳钼业', '605117.SH': '德业股份',
    '605499.SH': '东鹏饮料', '688008.SH': '澜起科技', '688009.SH': '中国通号', '688012.SH': '中微公司', '688036.SH': '传音控股',
    '688041.SH': '海光信息', '688082.SH': '盛美上海', '688111.SH': '金山办公', '688126.SH': '沪硅产业', '688169.SH': '石头科技',
    '688187.SH': '时代电气', '688223.SH': '晶科能源', '688256.SH': '寒武纪', '688271.SH': '联影医疗', '688303.SH': '大全能源',
    '688396.SH': '华润微', '688472.SH': '阿特斯', '688506.SH': '百利天恒', '688599.SH': '天合光能', '688981.SH': '中芯国际'
}

# 设置 tushare 的 token
my_database_token = '63324699e6c373c9f2cf6eaac850bd161b9fd31bb8d1f546316348f7'
ts.set_token(my_database_token)
pro = ts.pro_api()

# 获取股票数据
def get_stock_data(stock_code, date_period):
    today = dt.date.today()
    start_date = today - dt.timedelta(days=date_period)
    end_date = today
    formatted_end_date = str(end_date).replace('-', '')
    formatted_start_date = str(start_date).replace('-', '')
    df = pro.daily(ts_code=stock_code, start_date=formatted_start_date, end_date=formatted_end_date)
    df = df.sort_values('trade_date', ascending=True)
    return df

# 计算技术指标
def calculate_indicators(df):
    # 计算5日均线和20日均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    
    # 计算MA5的斜率
    df['MA5_slope'] = df['MA5'].diff()
    
    # 计算成交量的变化（例如5日平均成交量）
    df['Volume_MA5'] = df['vol'].rolling(window=5).mean()
    
    df.fillna(0, inplace=True)
    return df

def detect_signals(df, buy_volume_ratio=0.05, sell_volume_ratio=0.05):
    """
    生成买卖信号
    :param df: 包含股票数据的DataFrame
    :param buy_volume_ratio: 买入点成交量放大比例（默认5%）
    :param sell_volume_ratio: 卖出点成交量放大比例（默认5%）
    :return: 包含买卖信号的DataFrame
    """
    df['signal'] = 0  # 初始化信号列

    # 买入信号条件
    df['buy_signal'] = (
        (df['MA5_slope'] > 0) &  # 当前交易日MA5斜率为正
        (df['MA5_slope'].shift(1) < 0) &  # 上一个交易日MA5斜率为正
        (df['vol'] > (1 + buy_volume_ratio) * df['vol'].shift(1))  # 当前交易日成交量放大一定比例
    )

    # 卖出信号条件
    df['sell_signal'] = (
        (df['MA5_slope'] < 0) &  # 当前交易日MA5斜率为负
        (df['MA5_slope'].shift(1) > 0) &  # 上一个交易日MA5斜率为负
        (df['vol'] > (1 + sell_volume_ratio) * df['vol'].shift(1))  # 当前交易日成交量放大一定比例
    )

    # 标记买入和卖出信号
    df.loc[df['buy_signal'], 'signal'] = 1
    df.loc[df['sell_signal'], 'signal'] = -1

    # 记录信号出现的日期和收盘价
    df['buy_date'] = df['trade_date'].where(df['buy_signal'])
    df['buy_close'] = df['close'].where(df['buy_signal'])
    df['sell_date'] = df['trade_date'].where(df['sell_signal'])
    df['sell_close'] = df['close'].where(df['sell_signal'])

    return df

def calculate_return(df, initial_cash=100000, date_period=365):
    cash = initial_cash  # 初始现金
    shares = 0  # 持有的股票数量
    buy_price = 0  # 买入价格
    total_return = 0  # 总收益率

    for index, row in df.iterrows():
        if row['buy_signal']:
            # 买入股票
            if cash > 0:
                shares = cash / row['close']  # 用所有现金买入股票
                buy_price = row['close']
                cash = 0  # 现金清零
        elif row['sell_signal']:
            # 卖出股票
            if shares > 0:
                cash = shares * row['close']  # 卖出所有股票
                shares = 0  # 股票清零
                total_return += (cash - initial_cash) / initial_cash  # 计算收益率

    # 如果最后还持有股票，按最后一天的收盘价计算股票价值
    if shares > 0:
        final_value = shares * df.iloc[-1]['close']
        total_return += (final_value - initial_cash) / initial_cash

    # 计算年化收益率
    annualized_return = ((1 + total_return) ** (365 / date_period) - 1) * 100

    return total_return * 100, annualized_return  # 返回总收益率和年化收益率


class SellScreen(Screen):
    def __init__(self, **kwargs):
        super(SellScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # 使用 ScrollView 来支持滚动
        self.scroll_view = ScrollView(size_hint=(1, 0.9))  # 设置 ScrollView 的高度为页面的90%
        self.label = Label(
            text="", 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_y=None, 
            text_size=(self.width, None), 
            halign='left', 
            valign='top'
        )
        self.label.bind(width=lambda *x: self.label.setter('text_size')(self.label, (self.label.width, None)))
        self.label.bind(texture_size=self.label.setter('size'))  # 根据内容调整 Label 的高度
        self.scroll_view.add_widget(self.label)
        self.layout.add_widget(self.scroll_view)

        # 添加返回按钮
        self.back_button = Button(text='返回', font_name='STKAITI', font_size=25, size_hint_y=0.1)
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)

    def update_content(self, all_signals, total_return, annualized_return):
        if all_signals:
            # 按照日期顺序显示所有买卖点
            formatted_text = "操作      日期      收盘价\n"
            for signal in all_signals:
                date, text, signal_type = signal
                if signal_type == 'buy':
                    formatted_text += f"[color=ff0000]{text}[/color]\n"  # 红色字体显示买点
                else:
                    formatted_text += f"[color=00ff00]{text}[/color]\n"  # 绿色字体显示卖点
            
            self.label.text = formatted_text
            self.label.markup = True  # 启用 Markup 以支持颜色
        else:
            self.label.text = "没有买卖点出现。"

    def go_back(self, instance):
        self.manager.current = 'input_screen'


# 输入页面
class InputScreen(Screen):
    def __init__(self, **kwargs):
        super(InputScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=0, padding=0)

        # 左侧布局（输入框和按钮）
        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.6, spacing=0)

        # 回溯天数输入框及其提示词
        date_period_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        date_period_label = Label(text='回溯天数:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.date_period_input = TextInput(
            text='365', 
            hint_text='(如 365)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        date_period_layout.add_widget(date_period_label)
        date_period_layout.add_widget(self.date_period_input)
        left_layout.add_widget(date_period_layout)

        # 股票名称输入框及其提示词
        stock_name_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        stock_name_label = Label(text='股票代码:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.stock_code_input = TextInput(
            text='601628.SH', 
            hint_text='(例 601628.SH)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        stock_name_layout.add_widget(stock_name_label)
        stock_name_layout.add_widget(self.stock_code_input)
        left_layout.add_widget(stock_name_layout)

        # 买入点成交量放大比例输入框
        buy_volume_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        buy_volume_label = Label(text='买入成交量放大:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.buy_volume_input = TextInput(
            text='0.05', 
            hint_text='(如 0.05)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        buy_volume_layout.add_widget(buy_volume_label)
        buy_volume_layout.add_widget(self.buy_volume_input)
        left_layout.add_widget(buy_volume_layout)

        # 卖出点成交量放大比例输入框
        sell_volume_layout = BoxLayout(orientation='horizontal', size_hint_y=10, height=40)
        sell_volume_label = Label(text='卖出成交量放大:', size_hint_x=1, font_name='STKAITI', font_size=30)
        self.sell_volume_input = TextInput(
            text='0.05', 
            hint_text='(如 0.05)', 
            multiline=False, 
            font_name='STKAITI', 
            font_size=30, 
            size_hint_x=0.7,
            halign='center'
        )
        sell_volume_layout.add_widget(sell_volume_label)
        sell_volume_layout.add_widget(self.sell_volume_input)
        left_layout.add_widget(sell_volume_layout)

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

        # 下一页按钮
        self.next_button = Button(
            text='查看买卖点', 
            size_hint_y=10, 
            height=40, 
            font_name='STKAITI', 
            font_size=25, 
            background_color='blue'
        )
        self.next_button.bind(on_press=self.go_to_sell_screen)
        left_layout.add_widget(self.next_button)

        # 右侧布局（结果显示标签）
        right_layout = BoxLayout(orientation='vertical', size_hint_x=1, spacing=10)

        # 结果显示标签
        self.result_label = Label(
            text='Developed by 玉帛书影\n\n\t\t中国人寿 -- 601628.SH\n\t\t工商银行 -- 601398.SH\n\t\t长江电力 -- 600900.SH', 
            size_hint_y=10, 
            height=100, 
            font_name='STKAITI', 
            font_size=30, 
            text_size=(None, None), 
            halign='center', 
            valign='middle'
        )
        right_layout.add_widget(self.result_label)

        # 将左右布局添加到主布局
        self.layout.add_widget(left_layout)
        self.layout.add_widget(right_layout)

        # 添加布局到页面
        self.add_widget(self.layout)

    def run_script(self, instance):
        check_input1_ok = False
        check_input2_ok = False
        message = ''
        if self.date_period_input.text == '':
            check_input1_ok = False
            message += '^o^ 输入的回溯日期为空 ^o^\n'
        elif self.date_period_input.text.isdigit():
            check_input1_ok = True
        else:
            check_input1_ok = False
            message += '^o^ 请输入正确的回溯日期 ^o^\n'
        
        for code, name in HS300_STOCKS.items():
            if self.stock_code_input.text == code:
                check_input2_ok = True
                break
            
        if check_input2_ok:
            message += ''
        else:
            message += '请输入有效的沪深300成分股代码\n(暂不支持其它成分股，风险太大)'

        if check_input1_ok and check_input2_ok:
            date_period = int(self.date_period_input.text)
            stock_code = self.stock_code_input.text
            buy_volume_ratio = float(self.buy_volume_input.text)  # 获取买入点成交量放大比例
            sell_volume_ratio = float(self.sell_volume_input.text)  # 获取卖出点成交量放大比例

            # 运行主函数
            self.stock_name, self.total_return, self.annualized_return = main(date_period, self.manager.get_screen('sell_screen'), stock_code, buy_volume_ratio, sell_volume_ratio)

            # 更新 result_label 显示总体收益和年化收益
            self.result_label.text = f"{self.stock_name}\n 总收益率: {self.total_return:.2f}%\n年化收益率: {self.annualized_return:.2f}%"
        else:
            self.result_label.text = f"{message}"

    def go_to_sell_screen(self, instance):
        # 切换到卖点页面
        self.manager.current = 'sell_screen'

# 修改 main 函数以返回总体收益和年化收益
def main(date_period, sell_screen, stock_code, buy_volume_ratio, sell_volume_ratio):
    sell_stocks = []
    all_signals = []  # 用于存储所有买卖点
    stock_name = 'OTHER'
    total_return = 0  # 初始化总收益率
    annualized_return = 0  # 初始化年化收益率

    if stock_code:
        for code, name in HS300_STOCKS.items():
            if stock_code == code:
                stock_name = name
                break
        if stock_code:
            try:
                df = get_stock_data(stock_code, date_period)
                df = calculate_indicators(df)
                df = detect_signals(df, buy_volume_ratio, sell_volume_ratio)  # 传递成交量放大比例

                # 计算总收益率和年化收益率
                total_return, annualized_return = calculate_return(df, date_period=date_period)

                # 遍历整个数据框，找到所有的买卖点
                for index, row in df.iterrows():
                    if row['buy_signal']:
                        all_signals.append((row['buy_date'], f"买入   {row['buy_date']}    {row['buy_close']}", 'buy'))
                    if row['sell_signal']:
                        sell_stocks.append(f"(卖点日期: {row['sell_date']}, 收盘价: {row['sell_close']})")
                        all_signals.append((row['sell_date'], f"卖出   {row['sell_date']}    {row['sell_close']}", 'sell'))

                # 按照日期排序所有买卖点
                all_signals.sort(key=lambda x: x[0])

            except Exception as e:
                print(f"股票 {stock_name} 时出错: {e}")

    # 更新买点和卖点页面，并传递总收益率和年化收益率
    sell_screen.update_content(all_signals, total_return, annualized_return)

    # 返回总收益率和年化收益率
    return stock_name, total_return, annualized_return

# 定义应用程序
class StockApp(App):
    def build(self):
        # 创建 ScreenManager
        self.screen_manager = ScreenManager()

        # 添加输入页面
        self.input_screen = InputScreen(name='input_screen')
        self.screen_manager.add_widget(self.input_screen)


        # 添加卖点页面
        self.sell_screen = SellScreen(name='sell_screen')
        self.screen_manager.add_widget(self.sell_screen)

        return self.screen_manager

if __name__ == "__main__":
    # 设置中文字体
    from kivy.core.text import LabelBase
    LabelBase.register(name='STKAITI', fn_regular='STKAITI.TTF')  # 确保 STKAITI.TTF 文件在项目目录中
    StockApp().run()
