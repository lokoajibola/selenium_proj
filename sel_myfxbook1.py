# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 13:27:31 2025

SCRAPE DATA FROM MYFXBOOK

@author: jbriz
"""


import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
import time
from time import sleep

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
    price = mt5.symbol_info_tick(symbol).ask if trade_type == "Buy" else mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point
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


# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening browser (optional)
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize Chrome WebDriver
# service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome() # service=service, options=options)

# Open Bet9ja Sports page
url = "https://www.myfxbook.com/forex-economic-calendar"
driver.get(url)

try:
    time.sleep(10)  # Adjust if necessary
    element1 = driver.find_element(By.XPATH, "//button[contains(@class, 'no-padding')]")
    # element1 = WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'no-padding')]")))
    element1.click()
    print("✅ Element 1 clicked successfully!")
    
    time.sleep(10)  # Adjust if necessary

    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//button[contains(@id, 'calendarToDayBtn')]")))
    element = driver.find_element(By.XPATH, "//button[contains(@id, 'calendarToDayBtn')]")
    # Click the element
    element.click()
    print("✅ Element 2 clicked successfully!")



    # Allow time for content to load
    time.sleep(10)  # Adjust if necessary
    
    tz = pytz.timezone("Africa/Lagos")
    naija_now = datetime.now(tz)
    
    news_row = driver.find_elements(By.XPATH, "//tr[contains(@class, 'economicCalendarRow')]")
    curr_row = driver.find_elements(By.XPATH, "//td[(@class, 'calendarToggleCell)]")
    datetime_row = driver.find_elements(By.XPATH, "//div[contains(@class, 'calendarDateTd')]")
    event_row = driver.find_elements(By.XPATH, "//a[contains(@class, 'calendar-event-link')]")
    impact_row = driver.find_elements(By.XPATH, "//div[contains(@class, 'impact')]")
    actual_row = driver.find_elements(By.XPATH, "//span[contains(@class, 'actualCell')]")
    
    for i in range(len(news_row)):
        date_time = datetime_row[i]
        date_time = date_time.find_element(By.XPATH, ".//div[contains(@class, 'calendarDateTd')]").text.strip()
        try: 
            event_time = datetime.strptime(date_time, "%I:%M%p").time()
            event_time = datetime.combine(naija_now.date(), event_time)
            
            
        
        
        
        except:
            pass
    
except Exception as e:
    # driver.quit()
    print(f"❌ Error: {e}")