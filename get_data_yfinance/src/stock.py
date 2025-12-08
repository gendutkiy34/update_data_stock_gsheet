import json
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utilization import General

gx=General()

cols=['date','Close', 'High', 'Low', 'Open', 'Volume', 'RSI(14)', 'EMA12',
       'EMA26', 'MACD', 'Signal', 'Volatilitas(7d)', 'Sinyal', 'Interpretasi',
       'Emiten']

class Stock():

    def __init__(self,code_list=None,days_back=7):
        if isinstance(code_list,list):
            self.code_list = code_list
        elif isinstance(code_list,str):
            self.code_list = code_list.split(',')
        self.days_back = days_back

    def ListStock(self):
        return self.code_list

    def GetYesterday(self,start_date,end_date):
        data_result = []
        for emiten in self.code_list:
            print(f"Mengambil data {emiten} ...")
            raw = yf.download(emiten, start=start_date, end=end_date, auto_adjust=True)
            if not raw.empty:
                try:
                    raw['date'] = raw.index.strftime('%Y-%m-%d')
                    if isinstance(raw.columns, pd.MultiIndex):
                        raw.columns = raw.columns.get_level_values(0)
                    for col in ["Open", "High", "Low", "Close"]:
                        if col not in raw.columns:
                            raise ValueError(f"Kolom '{col}' tidak ditemukan di data harga.")

                    # Hitung RSI(14)
                    delta = raw["Close"].diff()
                    gain = np.where(delta > 0, delta, 0).flatten()
                    loss = np.where(delta < 0, -delta, 0).flatten()
                    avg_gain = pd.Series(gain).rolling(window=14).mean()
                    avg_loss = pd.Series(loss).rolling(window=14).mean()
                    rs = avg_gain / avg_loss
                    raw["RSI(14)"] = 100 - (100 / (1 + rs))

                    # Hitung MACD, Signal
                    raw["EMA12"] = raw["Close"].ewm(span=12, adjust=False).mean()
                    raw["EMA26"] = raw["Close"].ewm(span=26, adjust=False).mean()
                    raw["MACD"] = raw["EMA12"] - raw["EMA26"]
                    raw["Signal"] = raw["MACD"].ewm(span=9, adjust=False).mean()

                    # Volatilitas 7 hari (risiko)
                    raw["Volatilitas(7d)"] = raw["Close"].pct_change().rolling(window=7).std()

                    # Pastikan semua array 1D
                    close = raw["Close"].values.flatten()
                    rsi = raw["RSI(14)"].values.flatten()
                    vol = raw["Volatilitas(7d)"].values.flatten()
                    macd = raw["MACD"].values.flatten()
                    signal = raw["Signal"].values.flatten()
                    ema12 = raw["EMA12"].values.flatten()
                    ema26 = raw["EMA26"].values.flatten()
                       
                    raw["Emiten"] = emiten.replace(".JK", "")
                    datafilter=raw.tail(1)
                    
                    data_result.append(raw.tail(1))
                except Exception as e:
                    print(f"⚠️ failed to calculate {emiten}: {e}")
            else:
                print(f"⚠️ Data {emiten} tidak tersedia")
        return pd.concat(data_result)[cols]

    def Get7Days(self,start_date,end_date):
            data_result = []
            for emiten in self.code_list:
                print(f"Mengambil data {emiten} ...")
                raw = yf.download(emiten, start=start_date, end=end_date, auto_adjust=True)
                if not raw.empty:
                    try:
                        if isinstance(raw.columns, pd.MultiIndex):
                            raw.columns = raw.columns.get_level_values(0)
                        for col in ["Open", "High", "Low", "Close"]:
                            if col not in raw.columns:
                                raise ValueError(f"Kolom '{col}' tidak ditemukan di data harga.")
                        
                        # Hitung RSI(14)
                        delta = raw["Close"].diff()
                        gain = np.where(delta > 0, delta, 0).flatten()
                        loss = np.where(delta < 0, -delta, 0).flatten()
                        avg_gain = pd.Series(gain).rolling(window=14).mean()
                        avg_loss = pd.Series(loss).rolling(window=14).mean()
                        rs = avg_gain / avg_loss
                        raw["RSI(14)"] = 100 - (100 / (1 + rs))

                        # Hitung MACD, Signal
                        raw["EMA12"] = raw["Close"].ewm(span=12, adjust=False).mean()
                        raw["EMA26"] = raw["Close"].ewm(span=26, adjust=False).mean()
                        raw["MACD"] = raw["EMA12"] - raw["EMA26"]
                        raw["Signal"] = raw["MACD"].ewm(span=9, adjust=False).mean()

                        # Volatilitas 7 hari (risiko)
                        raw["Volatilitas(7d)"] = raw["Close"].pct_change().rolling(window=7).std()

                        # Pastikan semua array 1D
                        close = raw["Close"].values.flatten()
                        rsi = raw["RSI(14)"].values.flatten()
                        vol = raw["Volatilitas(7d)"].values.flatten()
                        macd = raw["MACD"].values.flatten()
                        signal = raw["Signal"].values.flatten()
                        ema12 = raw["EMA12"].values.flatten()
                        ema26 = raw["EMA26"].values.flatten()

                        raw["Emiten"] = emiten.replace(".JK", "")
                        data_result.append(raw)
                    except Exception as e:
                        print(f"⚠️ failed to calculate {emiten}: {e}")
                else:
                    print(f"⚠️ Data {emiten} tidak tersedia")
            return pd.concat(data_result)

    
