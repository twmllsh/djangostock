import numpy as np
import pandas as pd
import requests
import FinanceDataReader as fdr
from dashboard.utils import chart
from dashboard.utils.sean_func import Sean_func
from dashboard import models
from dashboard.models import InvestorTrading

class GetData:
    
    
    def _get_ohlcv_from_daum(code,   data_type="30분봉", limit=450):
        '''
        Big Chart에서 받기.
        '''
        acode = "A" + code
        # data_type= '일봉'
        limit = 480
        option_dic = {
            "월봉": "months",
            "주봉": "weeks",
            "일봉": "days",
            "60분봉": "60/minutes",
            "30분봉": "30/minutes",
            "15분봉": "15/minutes",
            "5분봉": "5/minutes",
        }

        str_option = option_dic[data_type]
        url = f"http://finance.daum.net/api/charts/{acode}/{str_option}"
        params = {"limit": f"{limit}", "adjusted": "true"}
        headers = {"referer": "https://finance.daum.net/chart/", "user-agent": "Mozilla/5.0"}

        response = requests.get(url=url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
        else:
            return pd.DataFrame()

        data = data["data"]
        df = pd.DataFrame(data)
        chage_col = {
            "candleTime": "Date",
            "tradePrice": "Close",
            "openingPrice": "Open",
            "highPrice": "High",
            "lowPrice": "Low",
            "candleAccTradePrice": "TradePrice",
            "candleAccTradeVolume": "Volume",
        }
        columns = ["Date", "Open", "High", "Low", "Close", "Volume", "TradePrice"]
        df["candleTime"] = pd.to_datetime(df["candleTime"])
        df.rename(columns=chage_col, inplace=True)
        df = df[columns].set_index("Date")
        return df
    
    def _get_ohlcv_from_fdr(code):
        limit = 450
        end = pd.Timestamp.now().date()
        start = end - pd.Timedelta(days=limit)
        df = fdr.DataReader(code, start=start, end=end)
        return df


class ElseInfo:
    _, check_y_current, check_y_future = Sean_func._실적기준구하기()  # 0-1 0대비 1성장율.. 
    _, check_q_current, check_q_future =  Sean_func._실적기준구하기('q')  ## 0-2 yoy 1-2 qoq
    
    ohlcv_end_date = pd.Timestamp.now().date()
    ohlcv_start_date = ohlcv_end_date - pd.Timedelta(days=365 * 2)
    
class Stock:
    
    def __init__(self, code, start_date=None, end_date=None, anal=False):
        
        self.code = code

        self.ticker = models.Ticker.objects.get(code=self.code)
        self.info : models.Info = self.ticker.info
        self.액면가 = self.info.액면가
        self.상장주식수 = self.info.상장주식수
        self.유동비율 = self.info.유동비율
        self.유동주식수 = self.상장주식수 * self.유동비율 / 100 if self.유동비율 else self.상장주식수 
        self.외국인소진율 = self.info.외국인소진율
        
        self.ohlcv_day = models.Ohlcv.get_data(self.ticker)
        self.chart_d: chart.Chart = chart.Chart(self.ohlcv_day, mas=[3,5,10,20,60,120,240],
                                   상장주식수=self.상장주식수,
                                   유동주식수=self.상장주식수 * self.유동비율,
                                   )
        if anal:
            # 5 30 받아서 chart 생성 . 후 필요한 값만 가져오기. 
            self.ohlcv_30 = GetData._get_ohlcv_from_daum(code=self.code, data_type='30분봉')
            self.ohlcv_5 = GetData._get_ohlcv_from_daum(code=self.code, data_type='5분봉')
            self.chart_30 = chart.Chart(self.ohlcv_30, mas=[10,20,60,120,240],
                                   상장주식수=self.상장주식수,
                                   유동주식수=self.상장주식수 * self.유동비율,
                                   )
            
            self.chart_5 = chart.Chart(self.ohlcv_5, mas=[10,20,60,120,240],
                                   상장주식수=self.상장주식수,
                                   유동주식수=self.상장주식수 * self.유동비율,
                                   )
            
        # investor
        self.investor_part = self.get_investor_part()    
        
        ## 연간 매출액, 영업이익, 당기순이익 데이터 가져오기. ==> models에 함수로 이동하기
        fin : models.Finstats = self.ticker.finstats_set
        fin_y_qs = fin.filter(fintype='연결연도', quarter=0).values('year','매출액', '영업이익','당기순이익')
        fin_qs_q = fin.exclude(quarter=0).filter(fintype='연결분기').values('year','quarter','매출액', '영업이익','당기순이익')
        
        fin_df = pd.DataFrame(fin_y_qs)
        fin_df_q = pd.DataFrame(fin_qs_q)
        fin_df = fin_df.set_index('year')
        fin_df_q['index'] = fin_df_q['year'].astype(str) + "/" + fin_df_q['quarter'].astype(str).str.zfill(2)
        fin_df_q = fin_df_q.set_index("index")
        
        
  
            
       
        
    # 날짜범위와 계산값 반환.  to_list or  dict
    def get_investor_part(self):
 
        ls = []
        low_dates = self._get_low_dates()
        qs = InvestorTrading.objects.filter(ticker=self.ticker).filter(날짜__gte=low_dates[0])
        investor_df = pd.DataFrame(qs.values('날짜','투자자','매도거래량','매수거래량', '매도거래대금','매수거래대금'))
        investor_df['순매수거래대금'] = investor_df['매수거래대금'] - investor_df['매도거래대금']
        investor_df['순매수거래량'] = investor_df['매수거래량'] - investor_df['매도거래량']
        # 데이터 분리하고. 
        investor_df['날짜'] = pd.to_datetime(investor_df['날짜'])
        for i in range(len(low_dates)):
            temp_dic = {}
            if len(low_dates)-1  == i:
                print('last')
                start_date = low_dates[i]
                temp_df = investor_df.loc[(investor_df['날짜'] >= start_date)]
            else:
                start_date, end_date = low_dates[i],low_dates[i+1]
                temp_df = investor_df.loc[(investor_df['날짜'] >= start_date) & (investor_df['날짜'] < end_date)]
            
            if len(temp_df):
                temp_dic= self._cal_investor(temp_df)
                ls.append(temp_dic)  
        print("low_dates: ", low_dates)
        return ls

    def _get_low_dates(self):
        low3 = self.chart_d.ma3.df_last_low_points
        low3_all = self.chart_d.ma3.df_all_low_points
        low20 = self.chart_d.ma20.df_last_low_points
        start_date = None
        if len(low20)==0:
            if len(low3)==0:
                print('pass')
            else:
                start_date= low3.index[0]
                print('3일로 지정.')
            pass
        else:
            if len(low20)==1:
                date20 = low20.index[-1]
            else:
                date20 = low20.index[-2]
            start_date = low3_all[low3_all.index < date20].index[-1]
        print("start_date : ", start_date)
        # low_dates = list(low3_all.loc[low3_all.index >= start_date].index) + [self.chart_d.df.index[-1]]
        low_dates = list(low3_all.loc[low3_all.index >= start_date].index)
        return low_dates
        
    def _cal_investor(self, df):
        '''
        구간데이터를 주면 정리해주는 함수. return dict
        '''
        temp_dic = {}
        if all([col in df.columns for col in ['날짜', '투자자','매도거래대금','매수거래대금','순매수거래대금']]):
            temp_df = df.copy()
            
            ##########################################
            temp_dic["start"] , temp_dic["end"] = temp_df['날짜'].iloc[0],temp_df['날짜'].iloc[-1] 
            
            ########################################
            grouped_temp_df = temp_df.groupby('투자자')[['매도거래대금','매수거래대금','순매수거래대금']].sum()
            grouped_temp_df = grouped_temp_df.loc[~((grouped_temp_df['매수거래대금'] ==0) & (grouped_temp_df['매도거래대금'] ==0))]  ## 매수매도 모두 0인값 제거. 
            grouped_temp_df["매집비"] = round((grouped_temp_df["매수거래대금"] / grouped_temp_df["매도거래대금"]) * 100, 1)
            # inf 값을 10000으로 대체
            df.replace([np.inf, -np.inf], 10000, inplace=True)
            grouped_temp_df["full"] = (grouped_temp_df["순매수거래대금"] == grouped_temp_df["매수거래대금"] ) & (grouped_temp_df["순매수거래대금"] !=0) &  (grouped_temp_df["매수거래대금"] >=100000000) # 1억이상.  

            # 주도기관
            적용기관리스트 = list(grouped_temp_df.sort_values("매집비", ascending=False).index)
            주도기관 = ','.join(적용기관리스트[:2])
            적용기관 = ','.join(적용기관리스트)
            temp_dic["적용기관"] = 적용기관
            temp_dic["주도기관"] = 주도기관
        
        
            ##  전체풀매수 여부..
            df_sum = grouped_temp_df.sum()
            매집비 = round(df_sum.loc['매수거래대금'] / df_sum.loc['매도거래대금'] *100 , 1) 
            순매수 = df_sum.loc["순매수거래대금"]
            순매수금액_억 = round(순매수 / 100000000, 1)
            temp_dic["순매수대금"] = 순매수
            temp_dic["순매수금_억"] = 순매수금액_억
            temp_dic["매집비"] = 매집비
            

            ## 부분 full_buy 여부 ##############################################################
            temp_df["full_b"] = (temp_df["순매수거래대금"] == temp_df["매수거래대금"]) & (temp_df["매수거래대금"] !=0) & (temp_df['매수거래대금'] >= 50000000 ) 
            full_b = temp_df.loc[temp_df["full_b"]]
            if len(full_b):
                # result_b = full_b.groupby('투자자').sum()[['순매수거래량','순매수거래대금','full_b']].sort_values(['순매수거래대금','full_b'],ascending=[False,False])
                result_b = full_b.groupby('투자자')[['순매수거래량','순매수거래대금','full_b']].sum().sort_values(['순매수거래대금','full_b'],ascending=[False,False])
                부분풀매수기관 = ','.join(result_b.index)
                부분풀매수금액 = result_b['순매수거래대금'].sum()
                부분풀매수일 = result_b['full_b'].sum()
                temp_dic['부분풀매수기관'] = 부분풀매수기관
                temp_dic['부분풀매수금액'] = 부분풀매수금액
                temp_dic['부분풀매수일'] = 부분풀매수일
            else:
                temp_dic['부분풀매수기관'] = ""
                temp_dic['부분풀매수금액'] = 0
                temp_dic['부분풀매수일'] = 0
                
            ## 부분 full_sell 여부 ##############################################################
            temp_df["full_s"] = (abs(temp_df["순매수거래대금"]) == temp_df["매도거래대금"]) & (temp_df["매도거래대금"] !=0)  
            full_s = temp_df.loc[temp_df["full_s"]]
            if len(full_s):
                # result_s = full_s.groupby('투자자').sum()[['순매수거래량','순매수거래대금','full_s']].sort_values(['순매수거래대금','full_s'],ascending=[True,False])
                result_s = full_s.groupby('투자자')[['순매수거래량','순매수거래대금','full_s']].sum().sort_values(['순매수거래대금','full_s'],ascending=[True,False])
                부분풀매도기관 = ','.join(result_s.index)
                부분풀매도금액 = result_s['순매수거래대금'].sum()
                부분풀매도일 = result_s['full_s'].sum()
                temp_dic['부분풀매도기관'] = 부분풀매도기관
                temp_dic['부분풀매도금액'] = 부분풀매도금액
                temp_dic['부분풀매도일'] = 부분풀매도일
            else:
                temp_dic['부분풀매도기관'] = ""
                temp_dic['부분풀매도금액'] = 0
                temp_dic['부분풀매도일'] = 0
            
            ## 전체 full 여부
            if len(grouped_temp_df.loc[grouped_temp_df["full"]]):
                풀매수기관 = list(grouped_temp_df.loc[grouped_temp_df["full"]].index)
                풀매수금액 = grouped_temp_df.loc[grouped_temp_df['full']]['순매수거래대금'].sum()
                풀매수여부 = True if len(풀매수기관) else False
                temp_dic["풀매수여부"] = 풀매수여부
                temp_dic["풀매수기관"] = 풀매수기관
                temp_dic["풀매수금액"] = 풀매수금액
            else:
                temp_dic["풀매수여부"] = False
                temp_dic["풀매수기관"] = ""
                temp_dic["풀매수금액"] = 0
                ## 추후 추가할수 있는 부분.
                # temp_dic["start_ma5_value"] = start_ma5_value
                # temp_dic["저점대비현재가상승률"] = 저점대비현재가상승률
                
            return temp_dic



    ################  기술적 분석  ######################3
    
    def is_3w(self):
        pass
    
    def is_5w(self):
        pass
    




        
    def plot(self, option='day'):
        
        from bokeh.models import ColumnDataSource, Range1d
        from bokeh.plotting import figure, show
        from bokeh.models.formatters import NumeralTickFormatter
        from bokeh.layouts import gridplot, column, row
        
        if option=='day':
            chart = getattr(self, "chart_d")
            
        ## df 변환. 
        
        # df = pd.DataFrame(MSFT)[-240:]
        
        df : pd.DataFrame= chart.df.reset_index()
        df.columns = [col.lower() for col in df.columns]
        df["date"] = pd.to_datetime(df["date"])

        inc = df.close > df.open
        dec = df.open > df.close
        
        
        source = ColumnDataSource(data=dict(
            date=df.date,
            open=df.open,
            close=df.close,
            high=df.high,
            low=df.low,
            volume=df.volume,
        ))


        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        title = f"{self.ticker.name}({self.ticker.code})"
        
        p1 = figure(tools=TOOLS, width=800, height=300,
                    # toolbar_location=None,
                title=title,
                background_fill_color="#ffffff",
                    # x_range=Range1d(df.index[-40],df.index[-1] + 5),
                    # y_range=Range1d(0,20),
                    )
        p1.xaxis.major_label_orientation = 0.8 # radians
        p1.x_range.range_padding = 0.05

        # map dataframe indices to date strings and use as label overrides
        x_lable_overrides = {
            i: date.strftime('%y-%m-%d') for i, date in zip(df.index, df["date"])
        }
        p1.xaxis.major_label_overrides = x_lable_overrides

        # one tick per week (5 weekdays)
        p1.xaxis.ticker = list(range(df.index[0], df.index[-1], 10))
        p1.xaxis.axis_label = 'Date'
        p1.yaxis.axis_label = 'Price'

        # 그리드 설정
        p1.xgrid.grid_line_color=None
        p1.ygrid.grid_line_alpha=0.5

        # 축라벨 포멧팅
        p1.yaxis.formatter = NumeralTickFormatter(format="0,0")

        ## 캔들차트 그리기
        p1.segment(df.index[dec], df.loc[dec, 'high'], df.index[dec], df.loc[dec, 'low'], color="#2a79e2")
        p1.segment(df.index[inc], df.loc[inc, 'high'], df.index[inc], df.loc[inc, 'low'], color="#f4292f")

        p1.vbar(df.index[dec], 0.6, df.open[dec], df.close[dec], color="#2a79e2", line_width=0)
        p1.vbar(df.index[inc], 0.6, df.open[inc], df.close[inc], fill_color="#f4292f", line_width=0)


        ## 이동평균선 그리기
        mas = [3, 20, 60]
        color = ['blue', 'red', 'green']
        width = [1, 2, 3]
        alpha = [0.7, 0.7, 0.6]

        multi_line = [getattr(chart, f"ma{ma}").data.to_list() for ma in mas]
        xs = [df.index.to_list()] * len(multi_line)

        p1.multi_line(xs=xs,
                    ys=multi_line,
                    color=color,
                    alpha=alpha,
                    line_width=width)

        ## BB
        # ma60 = df.close.rolling(60).mean()
        # std60 = df.close.rolling(60).std()
        # upper = ma60 + 2 * std60
        # lower = ma60 - 2 * std60
        upper = getattr(chart, 'bb60').upper
        lower = getattr(chart, 'bb60').lower
        
        
        p1.multi_line(xs=[upper.index, lower.index],
                    ys=[upper, lower],
                    color="#f6b2b1",
                    alpha=0.8,
                    line_width=2,
                    legend_label='BB',
                    )

        ## sun
        # ma20 = df.close.rolling(20).mean()
        # std20 = df.close.rolling(20).std()
        # sun_max = ma20 + 2 * std20
        # sun_low = ma20 - 2 * std20
        sun_max = getattr(chart, 'sun').line_max.data
        sun_min = getattr(chart, 'sun').line_min.data
        p1.varea(
            x=sun_max.index,
            y1= sun_max,
            y2= sun_min,
            color='#bfd8f6',
            alpha=0.5,
            legend_label='mesh'
            )



        # # 거래량 차트 그리기
        p2 = figure( width=800, height=150, x_range=p1.x_range, toolbar_location=None)  # x_range를 공유해서 차트가 일치하게 만듦
        p2.vbar(x=df.index[dec], top=df.volume[dec], width=0.7, fill_color="#2a79e2",line_width=0 )
        p2.vbar(x=df.index[inc], top=df.volume[inc], width=0.7, fill_color="#f4292f",line_width=0)
        # p2.vbar(x=df.index, top=df.volume,  fill_color="#B3DE69", )

        p2.xaxis.major_label_overrides = x_lable_overrides
        p2.x_range.range_padding = 0.05
        p2.xaxis.axis_label = 'Date'
        p2.yaxis.axis_label = 'Volume'

        ## 그리드 설정
        p2.xgrid.grid_line_color=None
        p2.ygrid.grid_line_alpha=0.5

        ## 주석 (유통주식수, 상장주식수)


        layout = column(p1, p2, sizing_mode="stretch_both")
        return layout
    
    
    
    def __repr__(self):
        return f"<Stock> {self.ticker.name}({self.ticker.code})"