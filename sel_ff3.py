# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:00:01 2025

1. LOGIN TO MT5
2. GET DATA OF EVENTS FROM FF
3. PAUSE OR SLEEP TILL NEXT EVENT
4. WAIT TILL NEWS ARRIVES
5. STRATEGY TO TRADE - BUY IF BETTER, SELL IF WORSE
6. TP-10PTS, SL-20PTS || USE OF TRAILING SL

@author: jbriz
"""

# IMPORT LIBRARIES
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import MetaTrader5 as mt5
import numpy as np
# import datetime
import pandas as pd
import pytz
import pandas_ta as ta
from time import sleep


actual_checker = 0


# # LOGIN TO MT5
# account = 7002735 #187255335 #51610727
# mt5.initialize("C:/Program Files/MetaTrader 5 IC Markets (SC)/terminal64.exe")
# authorized=mt5.login(account, password="xxxxxxxx", server = "ICMarketsSC-MT5-2")

# 1. LOGIN TO MT5
account = 51962256
mt5.initialize("C:/Program Files/FxPro - MetaTrader 5/terminal64.exe")
authorized=mt5.login(account, password="1nojf!W@MEUAz8", server = "mt5-demo.icmarkets.com")

if authorized:
    print("Connected: Connecting to MT5 Client")
    # sleep(3)
else:
    print("Failed to connect at account #{}, error code: {}"
          .format(account, mt5.last_error()))
   
# establish connection to MetaTrader 5 terminal
if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    mt5.shutdown()

def open_trade(symbol, trade_type, volume, magic):
    trade_action = mt5.ORDER_TYPE_BUY if trade_type == "Buy" else mt5.ORDER_TYPE_SELL
    price = mt5.symbol_info_tick(symbol).ask if trade_type == "Buy" else mt5.symbol_info_tick(symbol).bid,
    point = point = mt5.symbol_info(symbol).point
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_action,
        "price": price,
        "deviation": 10,
        "sl": price - (20 * point) if trade_type == "Buy" else price + (20 * point),
        "tp": price - (10 * point) if trade_type == "Sell" else price + (10 * point),
        "magic": magic,
        "comment": "Synchronized trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to open trade for {symbol}: {result.retcode}")
    else:
        print(f"Opened trade: {symbol}, {volume} lots, {'Buy' if trade_type == mt5.ORDER_TYPE_BUY else 'Sell'}")


# 2. Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (optional)

try:
    driver = webdriver.Chrome() # options=options)
except ModuleNotFoundError as e:
    print("SSL module not found. Ensure your Python environment includes SSL support.")
    exit(1)

# Navigate to Forex Factory Calendar
driver.get("https://www.forexfactory.com/calendar?day=today")
time.sleep(5)  # Allow page to load


tz = pytz.timezone("Africa/Lagos")
naija_now = datetime.now(tz)

while True:
    try:
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'calendar__row')]")
        status = "N/A"
        for row in rows:
            try:
                impact_elem = row.find_element(By.XPATH, "//td[contains(@class, 'calendar__impact')]/span").get_attribute("class")
                currency_elem = row.find_element(By.CLASS_NAME, "calendar__currency").text
                time_elem = row.find_element(By.CLASS_NAME, "calendar__time").text
                event_elem = row.find_element(By.CLASS_NAME, "calendar__event").text
                forecast_elem = row.find_element(By.CLASS_NAME, "calendar__forecast").text
                

                try: 
                    event_time = datetime.strptime(time_elem, "%I:%M%p").time()
                    event_time = datetime.combine(naija_now.date(), event_time)
                except:
                    pass
                # if "red" or "yel" or "ora"  in impact_elem:
                    
                if event_time > datetime.now() - timedelta(minutes=5):
                    time.sleep((event_time - timedelta(minutes=5)).total_seconds())
                    # Navigate to Forex Factory Calendar
                    driver = webdriver.Chrome() # options=options)
                    driver.get("https://www.forexfactory.com/calendar?day=today")
                    time.sleep(5)  # Allow page to load
                    try:
                        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'calendar__row')]")
                        status = "N/A"
                        for row in rows:
                            try:
                                impact_elem = row.find_element(By.XPATH, "//td[contains(@class, 'calendar__impact')]/span").get_attribute("class")
                                currency_elem = row.find_element(By.CLASS_NAME, "calendar__currency").text
                                time_elem = row.find_element(By.CLASS_NAME, "calendar__time").text
                                event_elem = row.find_element(By.CLASS_NAME, "calendar__event").text
                                forecast_elem = row.find_element(By.CLASS_NAME, "calendar__forecast").text
                                

                                try: 
                                    event_time = datetime.strptime(time_elem, "%I:%M%p").time()
                                    event_time = datetime.combine(naija_now.date(), event_time)
                                except:
                                    pass
                    
                    
                                if event_time > datetime.now() - timedelta(seconds=40):
                                    # remaining_time = (datetime.combine(datetime.today(), event_time) - datetime.now()).total_seconds()
                                    time_to_sleep = (event_time - datetime.now()).total_seconds()
                                    print('Trade On pause till: ', event_time)        
                                    # sleep(time_to_sleep - 1)
                                    if time_to_sleep > 2:
                                        # break
                                        print(f"Waiting for actual value of: {event_elem} ({currency_elem})")
                                        time.sleep(time_to_sleep - 1)
                    
                                    while actual_checker < 30:
                                        try:
                                            actual_1 = row.find_element(By.CLASS_NAME, "calendar__actual")
                                            actual_2 = actual_1.find_element(By.TAG_NAME, "span")
                                            # actual_value = row.find_element(By.XPATH, "//td[contains(@class, 'calendar__actual')]").text
                                            actual_value= row.find_element(By.CLASS_NAME, "calendar__actual").text
                                            time.sleep(1)
                                            actual_checker = actual_checker+1
                                            if actual_value not in ["", "-"]:
                                                # span_class = row.find_element(By.XPATH, "//td[contains(@class, 'calendar__actual')]/span").get_attribute("class")
                                                status = actual_2.get_attribute("class")
                                                status = "Better" if "better" in status else "Worse" if "worse" in status else "N/A"
                                                if status == "N/A" and actual_value >= forecast_elem:
                                                    status = "Better" 
                                                elif status == "N/A" and actual_value < forecast_elem:
                                                    status = "Worse"
                                                print(f"Actual: {actual_value}, Status: {status}")
                                                actual_checker = 0
                                                break
                                        except:
                                            pass
                                        time.sleep(0.3)
                
                            except Exception:
                                    continue
                    except Exception as e:
                            print(f"Error retrieving rows: {e}")
            except Exception:
                continue
    except Exception as e:
        print(f"Error retrieving rows: {e}")
        # driver.quit()
        # exit(1)
    news_zone = currency_elem
    
    
    if news_zone == 'GBP':
        currs1 = ['GBPJPY','GBPUSD','EURGBP', 'GBPCAD']
        currs2 = ['EURGBP']
    elif news_zone == 'EUR':
        currs1 = ['EURUSD', 'EURGBP', 'EURCAD']
        currs2 = []
    elif news_zone == 'USD':
        currs1 = ['USDJPY', 'USDCAD']
        currs2 = ['GBPUSD', 'EURUSD', 'XAUUSD', 'AUDUSD', 'BTCUSD', 'NZDUSD']         
    elif news_zone == 'CC':
        currs = ['BTCUSD', 'ETHUSD', 'DOGUSD', 'SOLUSD']
    elif news_zone == 'AUD':    
        currs1 = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD']
        currs2 = []
    elif news_zone == 'JPY':    
        currs1 = []
        currs2 = ['GBPJPY', 'AUDJPY', 'USDJPY', 'CADJPY']
    elif news_zone == 'NZD':    
        currs1 = ['NZDUSD', 'NZDCAD', 'NZDJPY' ]
        currs2 = ['AUDNZD', 'EURNZD', 'GBPNZD']
    elif news_zone == 'CHF':    
        currs1 = ['CHFJPY' ]
        currs2 = ['AUDCHF', 'EURCHF', 'GBPCHF']
    else:
        currs1 = []  
        currs2 = []
        
    
    if status == 'Better':
        for curr in currs1:
            
            open_trade(curr, "Buy", 1, 123)
        for curr in currs2: 
            open_trade(curr, "Sell", 1, 123)
        
    elif status == 'Worse':
        for curr in currs1:
            open_trade(curr, "Sell", 1, 123)
        for curr in currs2: 
            open_trade(curr, "Buy", 1, 123)
    else:
        print('Gray actual')










