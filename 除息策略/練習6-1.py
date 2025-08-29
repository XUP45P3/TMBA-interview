#%%

# 用 sharpe Ratio
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

N=14     # 設定除息前 N 個交易日

symbol = "2330.TW"
stock = yf.Ticker(symbol)
dividends = stock.dividends     # 下載股票股利資料
dividends.index=pd.to_datetime(dividends.index).strftime("%Y/%m/%d")   # 設定 dividends 的索引
dic={"Date":dividends.index,"Dividend":dividends.values}
dividends=pd.DataFrame(dic)     # 建立一個 DataFrame
dividends.set_index("Date",inplace=True)     # 設定 index 為 Date
dividends["date"]=dividends.index     # 將 index 欄位資料加入 "Dividend_Date" 欄位
dividends["Pre1date"]=pd.to_datetime(dividends.index)-pd.offsets.BDay(1)     # 除息前一個交易的日期
dividends["Pre1date"] = dividends["Pre1date"].dt.strftime("%Y/%m/%d")
dividends["Pre"+str(N)+"date"]=pd.to_datetime(dividends.index)-pd.offsets.BDay(N)     # 除息前 N 個交易的日期
dividends["Pre"+str(N)+"date"] = dividends["Pre"+str(N)+"date"].dt.strftime("%Y/%m/%d")
dividends = dividends.round(2)
print("----------原始資料----------")
print(dividends)

df_dividend_Pre1date = dividends[["Dividend", "date", "Pre1date"]]
df_dividend_Pre1date.set_index("Pre1date", inplace = True)
print("----------除息前1天----------")
print(df_dividend_Pre1date)

df_dividend_Pre14date = dividends[["date", "Pre1date", "Pre14date"]]
df_dividend_Pre14date.set_index("Pre14date", inplace = True)
print("----------除息前14天----------")
print(df_dividend_Pre14date)

df_stock = pd.read_csv("C://MONEY//STOCK//DOWNLOAD//2330.csv", index_col = "Date", usecols = ["Date", "Close"]).rename(columns = {"Close":"2330"})
df_stock.index = pd.to_datetime(df_stock.index, format = "%Y/%m/%d")      # format 設定一定要和原始資料格式一樣，只是先把 str 轉換為時間格式
df_stock.index = df_stock.index.strftime("%Y/%m/%d")     # 修改時間格式的寫法
print("----------股價資訊----------")
print(df_stock)

df_dividend_Pre1date = df_dividend_Pre1date.join(df_stock)
df_dividend_Pre1date = df_dividend_Pre1date.rename(columns = {"2330":"Pre1date_Price"})
print("----------Pre1date_新增股票----------")
print(df_dividend_Pre1date)

df_dividend_Pre14date = df_dividend_Pre14date.join(df_stock)
df_dividend_Pre14date = df_dividend_Pre14date.rename(columns = {"2330":"Pre14date_Price"})
print("----------Pre14date_新增股票----------")
print(df_dividend_Pre14date)

df_dividend_Pre14date.set_index("Pre1date", inplace = True)
print("----------將索引設定為 Pre1date----------")
print(df_dividend_Pre14date)

df_dividend_Pre14date = df_dividend_Pre14date[["Pre14date_Price"]]
print("----------指選取我要的 column----------")
print(df_dividend_Pre14date)

df_dividend_Pre1date = df_dividend_Pre1date.join(df_dividend_Pre14date)
print("----------匯整全部資料----------")
print(df_dividend_Pre1date)

df = df_dividend_Pre1date

df["PL"] = df["Pre1date_Price"] - df["Pre14date_Price"]
df["PL%"] = (df["Pre1date_Price"] - df["Pre14date_Price"]) / df["Pre14date_Price"]
df["PL>0"] = np.where(df["PL"] > 0, 1, 0)
print("----------加入損益欄位----------")
df = df.dropna()
df = df.round(2)
print(df)

Win_Prob = df[["PL%"]][df["PL%"] > 0].count() / len(df.index)
print("----------勝率----------")
print(Win_Prob)
Loss_Prob = df[["PL%"]][df["PL%"] < 0].count() / len(df.index)
print("----------賠率----------")
print(Loss_Prob)

PL_mean = df["PL%"].mean()
print("----------平均報酬率----------")
print(PL_mean)

Win_mean_per = df["PL%"][df["PL%"] > 0].mean()
Win_mean_per = round(Win_mean_per, 4)
print("----------平均賺----------")
print(Win_mean_per)

Loss_mean_per = df["PL%"][df["PL%"] < 0].mean()
Loss_mean_per = round(Loss_mean_per, 4)
print("----------平均賠----------")
print(Loss_mean_per)

PL = Win_mean_per / Loss_mean_per
print("----------賺賠比(盈虧比)----------")
print(PL)

rf = 0.00705  # 設定無風險利率
sharpe_ratio = (PL_mean - rf) / df["PL%"].std()
print("----------Sharpe Ratio----------")
print(round(sharpe_ratio, 4))

Except_value = Win_Prob * Win_mean_per + Loss_Prob * Loss_mean_per
Except_value = round(Except_value, 4)
print("----------期望值----------")
print(Except_value)
# 期望值(E(x) > 0基本上就會賺錢)

df_stock = pd.read_csv("C:\\MONEY\\STOCK\\DOWNLOAD\\2330.csv", index_col = "Date", usecols = ["Date", "Close"]).rename(columns = {"Close":"2330.TW"})
df_stock.index = pd.to_datetime(df_stock.index, format = "%Y/%m/%d")     # 將 index 改變為時間的格式
df_stock.index = pd.to_datetime(df_stock.index).strftime("%Y/%m/%d")     # 改變時間格式的寫法

df_dividend_Pre1date = df_dividend_Pre1date[["date"]]
df_dividend_Pre1date["Pre1date"] = df_dividend_Pre1date.index

df_dividend_Pre14date = dividends[["Pre14date"]]
df_dividend_Pre14date.set_index("Pre14date", inplace = True)
df_dividend_Pre14date["Pre14date"] = df_dividend_Pre14date.index

df_stock = df_stock.join(df_dividend_Pre1date).join(df_dividend_Pre14date)
df_stock.index = pd.to_datetime(df_stock.index)

df_stock["year"] = df_stock.index.year
df_stock["month"] = df_stock.index.month
df_stock["day"] = df_stock.index.strftime("%Y/%m/%d")
df_stock.index = pd.to_datetime(df_stock.index).strftime("%Y/%m/%d")
print(df_stock)

df_stock["Signal_Pre1date"] = np.where(df_stock.index == df_stock["Pre1date"], 1000, 0)
df_stock["Signal_Pre14date"] = np.where(df_stock.index == df_stock["Pre14date"], -1000, 0)
print(df_stock)

#for year in range(2004, 2025, 1):
#    df_stock[[symbol, "Signal_Pre1date", "Signal_Pre14date"]][df_stock.year == year].plot(title = f"2330.TW vs Dividend_{year}", secondary_y = symbol, figsize = (15, 2), grid = True)
#    plt.show()