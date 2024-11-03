# -- Active: 1728471122893@@127.0.0.1@5432@stock
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.db.models import Q
from .forms import SignUpForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy , reverse
from .utils import mystock
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.embed import components, server_document
from pykrx import stock as pystock

from .utils.dbupdater import DBUpdater
from apscheduler.schedulers.background import BackgroundScheduler
sched : BackgroundScheduler = BackgroundScheduler()


# pd.options.plotting.backend = "bokeh" ## 버전문제인듯. 작동안함. 


######################## scheduler start! ################################
# year(int/str) -> 실행할 연도 4자리
# month(int/str) -> 실행할 월 1-12
# day(int/str) -> 실행할 일 1-31
# week(int/str) -> 실행할 주차 수 1-53
# day_of_week(int/str) -> 실행할 요일 0-6 | mon,tue,wed,thu,fri,sat,sun
# hour(int/str) -> 실행할 시간 0-23
# minute(int/str) -> 실행할 분 0-59
# second(int/str) -> 실행할 초 0-59
# timezone(timezoneInfo|str) -> 사용할 timezone


# @sched.scheduled_job('cron',  hour=22, minute=8)
# def scheduler_ticker():
#     DBUpdater.update_ticker()

@sched.scheduled_job('cron', day_of_week="1-5", hour=7, minute=30)
def scheduler_ticker():
    DBUpdater.update_ticker()
    
@sched.scheduled_job('cron', day_of_week="1-5", hour=20, minute=58)
def scheduler_ohlcv():
    DBUpdater.update_ohlcv()
    
@sched.scheduled_job('cron', day_of_week="1-5", hour=17, minute=10)
def dcheduler_basic_info():
    DBUpdater.update_basic_info()

@sched.scheduled_job('cron', day_of_week="1-5", hour=18, minute=5)
def dcheduler_update_investor():
    DBUpdater.update_investor()

@sched.scheduled_job('cron',  day_of_week="1-6", hour="8-18", minute="*/45")
def dcheduler_update_issue():
    DBUpdater.update_issue()

@sched.scheduled_job('cron', day_of_week="1-6", hour="8-23", minute="*/30")
def dcheduler_update_stockplus_news():
    DBUpdater.update_stockplus_news()
    
@sched.scheduled_job('cron', day_of_week=0,  hour=8, minute=0)
def dcheduler_update_theme_upjong():
    DBUpdater.update_theme_upjong()

if not settings.DEBUG:
    sched.start()
##########################sceduler end!  ##################################


class CustomLoginView(auth_views.LoginView):
    template_name='dashboard/registration/login.html'

    def get_success_url(self):
        # return reverse_lazy('dashboard:stock') ## url name
        return reverse('dashboard:dashboard') ## url name

customLoginView = CustomLoginView.as_view()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard:login')
    else:
        form = SignUpForm()
    return render(request, 'dashboard/registration/signup.html', {'form': form})



from .forms import StockFilterForm

from ex_form.models import MyStock


# df = pystock.get_market_ohlcv("20220720", "20220810", "005930")
 
# 3:23 부터 보기. https://www.youtube.com/watch?v=JRGktwaaYUA


def index(request):
    return render(request, 'dashboard/root.html')

def _left(request):
    tickers = ["005930", "000660", "310210"]
    names = ['삼성전자','sk하이닉스', '보로노이']
    data = [{ "code":'005930',
            "name":'삼성전자',
            "reasons":'new_bra 3w sun',
            },
            { "code":'000660',
            "name":'sk하이닉스',
            "reasons":'new_bra 3',
            },
            { "code":'310210',
            "name":'보로노이',
            "reasons":'3w',
            },
            ]
    df = pd.DataFrame(data)
    print(df)
    
    category_filters = []
    # mystocks = MyStock.objects.all()
    if request.method == 'POST':
        form = StockFilterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('new_bra'):
                category_filters.append('new_bra')
            if form.cleaned_data.get('3w'):
                category_filters.append('3w')
            if form.cleaned_data.get('sun'):
                category_filters.append('sun')
            if form.cleaned_data.get('consen'):
                category_filters.append('consen')
            
            if category_filters:
                query = Q()
                for category in category_filters:
                    query &= Q(reasons__icontains=category)
                # mystocks = mystocks.filter(query)
                    df = df.loc[df['reasons'].str.contains(query)]
                mystocks = df.to_dict('records')
                print(mystocks)
                print('필터되서 rendering!!')
            else:
                print('전체데이터')
            return render(request, "dashboard/includes/_left.html", {"form":form, 'mystocks':mystocks})
                
        else:
            print('is_valid failed! ')
            return render(request, "dashboard/includes/_left.html", {"form":form, 'mystocks':mystocks})
    else:
        form = StockFilterForm()
        print('그냥 rendering!!')
        print("category_filters",category_filters)
        return render(request, "dashboard/includes/_left.html", {"form":form, 'mystocks':mystocks}) 


   


def display_ticker(request, ticker):
    df, ticker_info = get_stock_data(ticker)
    
    candlestick_fig = create_candlestick_chart(df)
    scripts, chart_div= components(candlestick_fig)
    print(f"scripts : {scripts}")
    print(f"chart_dic : {chart_div}")
    context = {
        'tickers': zip(tickers, names),
        'ticker': ticker_info,
        'scripts': scripts,
        'hist_chart_div' : chart_div,
        'name' : f"{ticker_info}_name",
        'industry' : f"{ticker_info}_industry",
        'sector' : f"{ticker_info}_sector",
        'summary' : f"{ticker_info}_summary",
        'close' : f"{ticker_info}_close",
        'change' : f"{ticker_info}_change",
        'pct_change' : f"{ticker_info}_pct_change",
        }
    return render(request, "dashboard/display_ticker.html", context)


def bokeh_plot(request):
    p = figure(title="Sample Plot", x_axis_label='x', y_axis_label='y')
    p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
    
    script, div = components(p)

    print("====================")
    print(div)
    return render(request, 'dashboard/_plot.html', {'script': script, 'div': div})

def plot_test(request):
    code = request.GET.get('code',"")
    ma = request.GET.get('ma',"")
    print(f"code: {code}")
    print(f"ma: {ma}")
    from .utils.mystock import Stock
    charts = []
    try:
        stock = Stock(f'{code}', anal=True)

        p = stock.chart_d.plot_bokeh(title='Day')
        charts.append(components(p))
        if ma:
            chart = getattr(stock, 'chart_30')
            p30 = chart.plot_bokeh(title='min30')
            charts.append(components(p30))
            chart = getattr(stock, 'chart_5')
            p5 = chart.plot_bokeh(title='min5')
            charts.append(components(p5))

    except:
        p = figure(title="Sample Plot", x_axis_label='x', y_axis_label='y')
        p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
        
    
    script, div = components(p)
    context= {'charts':charts, 'script': script, 'div': div, 'code':code}
    return render(request, 'dashboard/plot_test.html', context=context)



def item_index(request):
    categories = ['Sun', 'BB', 'New']
    items = ['005930', '000660']
    context = {
        "categories" : categories,
        "items" : items,
    }
    print(context)
    return render(request, 'dashboard/dashboard.html', context)
    
def item_detail(request, item):
    file_path = settings.BASE_DIR / "templates" / "dashboard" / "_plot.html"
    output_file(file_path)
    p = figure(title="Sample Plot item detail", x_axis_label='x', y_axis_label='y')
    p.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=2)
    save(p)
    context = {'code':item }
    return render(request, 'dashboard/base.html', context)


def get_stock_data(ticker):
    end_date = pd.Timestamp.now().date()
    start_date = end_date - pd.Timedelta(days=365)
    str_start_date, str_end_date = start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
    df = pystock.get_market_ohlcv(str_start_date, str_end_date, ticker)
    df = df.reset_index()
    df = df.rename(columns={
        "날짜":"date",
        "시가":"open",
        "고가":"high",
        "저가":"low",
        "종가":"close",
        "거래량":"volume",
    })
    print(f'{ticker} 데이터 다운로드!! ')
    print(df.tail(2))
    return df, ticker

def create_candlestick_chart(df):
    p = figure(x_axis_type='datetime', sizing_mode="stretch_width",
                 tooltips=[('open','@open'),
                           ('high','@high'),
                           ('low','@low'),
                           ('close','@close'),
                           ])
    p.line(x='date', y='close',source=df)
    p.xaxis.axis_label="Date"
    p.yaxis.axis_label="Price ($)"
    return p
