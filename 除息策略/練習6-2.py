#%%
import os
import time
import random
import datetime
import requests
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from time import sleep
from tqdm import tqdm, trange
from bs4 import BeautifulSoup
from tvDatafeed import TvDatafeed,Interval
from dateutil.relativedelta import relativedelta


re = requests.get("https://stock.capital.com.tw/z/zm/zmd/zmdb.djhtm")
soup = BeautifulSoup(re.text)
table = soup.find_all("table")[0]
symbol = table.find_all(class_= "t3t1")

symbols = []
symbols_TW = []
symbols_chines = []
exchanges = []

# symbols_TW : 2330.TW ； symbols_chines : 台積電
for i in symbol:
    symbolnumber = str(i.text[:4]) + ".TW"
    symbols_TW.append(symbolnumber)
    symbolname = i.text[4::].replace("\n", "").replace(" ", "")
    symbols_chines.append(symbolname)

# 證交所名稱
for symbol in symbols_TW:
    if len(symbol) == 7:
        exchange = "TWSE"
    else:
        exchange = "TPEX"
    exchanges.append(exchange)

# symbols : 2330
for txt in symbols_TW:
    symbol = txt.split(".")[0]
    symbols.append(symbol)

df_top100 = pd.DataFrame({"symbol":symbols, "Exchange":exchanges , "symbol_TW":symbols_TW, "symbols_chines":symbols_chines})
df_top100.to_csv("C:\\MONEY\\STOCK\\DOWNLOAD\\Top100symbols.csv")

# --------------------TradingView 下載股票資料--------------------
'''
username = 'michael1220zhen'     # 帳號
password = 'Hnl-932-hnl'     # 密碼
tv = TvDatafeed(username = username, password = password)     # 登入TradingView

havedownload = 84
symbols=symbols[havedownload::]     # Tradingview 的代碼
exchanges=exchanges[havedownload::]     # Tradingview 的交易所
symbols_TW=symbols_TW[havedownload::]     # 自己的股票代碼

length = len(symbols)     # 總共有N檔股票
for symbol, exchange, symbols_TW, i in zip(symbols, exchanges, symbols_TW, tqdm(range(length))):
    symbol = str(symbol)
    sleep(1)
    df = tv.get_hist(symbol = symbol, exchange = exchange, interval = Interval.in_daily, n_bars = 7000)
    df.index = pd.to_datetime(df.index).strftime("%Y/%m/%d")
    df.index.name = "Date"
    df = df[["open", "high", "low", "close", "volume"]].rename(columns = {"open":"Open", "high":"High", "low":"Low", "close":"Close", "volume":"Volume"})     # 修改欄位名稱
    df = df.round(2)     # 修改數值為小數點後兩位
    df.to_csv(f"C:\\MONEY\\STOCK\\DOWNLOAD\\{symbol}.csv")

print(f"Update Date = {datetime.date.today()}")
'''
# -------------------- yahoofinance 下載股利資料 --------------------

N = 14     # 設定除息前N天參數

DividendYear = []     # 每一年年份
GainYear = []     # 賺錢(年)
Win_Prob_value = []     # 勝率
Loss_Prob_value = []     # 賠率
Win_mean_per_value = []     # 平均賺
Loss_mean_per_value = []     # 平均賠
Expected = []     # 期望值

for symbol in symbols:
    
    stock = yf.Ticker(f"{symbol}.TW")
    dividends = stock.dividends
    dividends.index = pd.to_datetime(dividends.index).strftime("%Y/%m/%d")
    dic = {"Date":dividends.index, "Dividend":dividends.values}
    dividends=pd.DataFrame(dic)     # 建立一個 DataFrame
    dividends.set_index("Date",inplace=True)     # 設定 index 為 Date
    dividends["date"]=dividends.index     # 將 index 欄位資料加入 "Dividend_Date" 欄位
    dividends["Pre1date"]=pd.to_datetime(dividends.index)-pd.offsets.BDay(1)     # 除息前一個交易的日期
    dividends["Pre1date"] = dividends["Pre1date"].dt.strftime("%Y/%m/%d")
    dividends["Pre"+str(N)+"date"]=pd.to_datetime(dividends.index)-pd.offsets.BDay(N)     # 除息前 N 個交易的日期
    dividends["Pre"+str(N)+"date"] = dividends["Pre"+str(N)+"date"].dt.strftime("%Y/%m/%d")
    dividends = dividends.round(2)

    # 新增一個除息前一天的 df
    df_Dividend_Pre1date = dividends[["Pre1date", "date"]]
    df_Dividend_Pre1date.set_index("Pre1date", inplace = True)

    # 新增一個除息前 N 天的 df
    df_Dividend_PreNdate = dividends[["Pre1date", f"Pre{str(N)}date", "date"]]
    df_Dividend_PreNdate.set_index(f"Pre{str(N)}date", inplace = True)

    # 讀取股價資料
    df_stock = pd.read_csv(f"C:\\MONEY\\STOCK\\DOWNLOAD\\{symbol}.csv", index_col = "Date", usecols = ["Date", "Close"]).rename(columns = {"Close":symbol})
    df_stock.index = pd.to_datetime(df_stock.index).strftime("%Y/%m/%d")
    
    # 將股價 join 除息前一天的 df
    df_Dividend_Pre1date = df_Dividend_Pre1date.join(df_stock)
    df_Dividend_Pre1date = df_Dividend_Pre1date.rename(columns = {symbol:f"{symbol}_Pre1Day"})
    
    # 將股價 join 除息前 N 天的 df
    df_Dividend_PreNdate = df_Dividend_PreNdate.join(df_stock)
    df_Dividend_PreNdate = df_Dividend_PreNdate.rename(columns = {symbol:f"{symbol}_Pre{str(N)}Day"})

    # 將除息前 N 天的 df.index 修改為 除息前一天的日期
    df_Dividend_PreNdate.set_index("Pre1date", inplace = True)
    df_Dividend_PreNdate = df_Dividend_PreNdate[[f"{symbol}_Pre{str(N)}Day"]]

    # 匯整 前一天與前 N 天的 df
    df_Dividend_Pre1date = df_Dividend_Pre1date.join(df_Dividend_PreNdate)
    df_Dividend_Pre1date = df_Dividend_Pre1date.dropna()
    
    # 計算賺賠金額
    df_Dividend_Pre1date["PL"] = df_Dividend_Pre1date[f"{symbol}_Pre1Day"] - df_Dividend_Pre1date[f"{symbol}_Pre{str(N)}Day"]
    # 計算賺賠金額比(%)
    df_Dividend_Pre1date["PL%"] = (df_Dividend_Pre1date[f"{symbol}_Pre1Day"] - df_Dividend_Pre1date[f"{symbol}_Pre{str(N)}Day"]) / df_Dividend_Pre1date[f"{symbol}_Pre{str(N)}Day"]
    # 計算賺錢訊號
    df_Dividend_Pre1date["PL>0"] = np.where(df_Dividend_Pre1date["PL"] > 0, 1, 0)
    # 計算勝率
    Win_Prob = df_Dividend_Pre1date[["PL%"]][df_Dividend_Pre1date["PL%"] > 0].count() / len(df_Dividend_Pre1date.index)
    Win_Prob = round(Win_Prob.values[0], 4)
    # 計算賠率
    Loss_Prob = df_Dividend_Pre1date[["PL%"]][df_Dividend_Pre1date["PL%"] < 0].count() / len(df_Dividend_Pre1date.index)
    Loss_Prob = round(Loss_Prob.values[0], 4)
    # 計算平均賺
    Win_mean_per = df_Dividend_Pre1date["PL%"][df_Dividend_Pre1date["PL%"] > 0].mean()
    Win_mean_per = round(Win_mean_per, 4)
    # 計算平均賠
    Loss_mean_per = df_Dividend_Pre1date["PL%"][df_Dividend_Pre1date["PL%"] < 0].mean()
    Loss_mean_per_mean_per = round(Loss_mean_per, 4)
    # 計算期望值
    Expect_value = Win_Prob * Win_mean_per + Loss_Prob * Loss_mean_per
    Expect_value = round(Expect_value, 4)

    DividendYear.append(len(df_Dividend_Pre1date.index))
    GainYear.append(df_Dividend_Pre1date["PL>0"].sum(axis = 0))
    Win_Prob_value.append(Win_Prob)
    Loss_Prob_value.append(Loss_Prob)
    Win_mean_per_value.append(Win_mean_per)
    Loss_mean_per_value.append(Loss_mean_per)
    Expected.append(Expect_value)
dic = {"symbol":symbols, "DividendYear":DividendYear, "GainYear":GainYear, "Win_Prob":Win_Prob_value, "Loss_Prob":Loss_Prob_value,
       "Win_mean_per":Win_mean_per_value, "Loss_mean_per":Loss_mean_per_value, "Expected":Expected}
df = pd.DataFrame(dic)
df = df.round(4)
df["WinLossRatio"] = round(df["Win_mean_per"] / abs(df["Loss_mean_per"]), 2)

# 將百分比欄位轉換為百分比格式的字串
df["Win_Prob"] = df["Win_Prob"].apply(lambda x: "{:.2%}".format(x))
df["Loss_Prob"] = df["Loss_Prob"].apply(lambda x: "{:.2%}".format(x))
df["Win_mean_per"] = df["Win_mean_per"].apply(lambda x: "{:.2%}".format(x))
df["Loss_mean_per"] = df["Loss_mean_per"].apply(lambda x: "{:.2%}".format(x))
df["Expected"] = df["Expected"].apply(lambda x: "{:.2%}".format(x))

df = df[df["Expected"] > "0.00%"]
sort_condition = ["Win_Prob", "Win_mean_per"]
df = df.sort_values(sort_condition, ascending = [False, False])
df = df.dropna()
print(df)
df.to_csv("C:\\MONEY\\STOCK\\BEFORE\\除息前14天買進.csv", index=False)