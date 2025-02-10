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
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import MetaTrader5 as mt5
import numpy as np
import datetime
import pandas as pd
import pytz
import pandas_ta as ta
from time import sleep


news_zone = 'GB'
# news_zone = 'EU'
# news_zone = 'US'
# news_zone = 'ALL2'
# news_zone = 'NEW'
# news_zone = 'CC'

if news_zone == 'GB':
    currs = ['GBPJPY','GBPUSD', 'EURUSD','EURGBP']
elif news_zone == 'EU':
    currs = [ 'EURUSD', 'EURGBP']
elif news_zone == 'ALL':
    currs = ['GBPJPY','GBPUSD', 'EURUSD', 'EURGBP', 'USDJPY', 'XAUUSD', 
             'USDCAD', 'AUDUSD', 'BTCUSD', 'NZDUSD']
elif news_zone == 'CC':
    currs = ['BTCUSD', 'ETHUSD', 'DOGUSD', 'SOLUSD']
elif news_zone == 'ALL2':    
    currs = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'GBPAUD', 'GBPCAD', 
               'GBPCHF', 'GBPJPY', 'GBPNZD', 'GBPUSD', 'EURAUD', 'EURCAD', 'EURCHF', 'EURGBP', 'EURJPY', 'EURNZD',
               'EURUSD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDCNH', 'USDJPY', 'XAUUSD',#, 'BTCUSD']
                'BTCUSD']
else:
    currs = ['AUDUSD','GBPUSD', 'NZDUSD','XAUUSD']


# SET THE NEWS TIME
news_min = 1
news_hour = 22

close_case = 0
pct_diff = 5 # 0.00001
period = 10
man_tp = 1000
man_sl = -1000
DD = 0
DU = 0

time_frame = 60
i = 50 # FVG in points

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

# Extract event details
events = []
try:
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'calendar__row')]")
    for row in rows:
        try:
            time_elem = row.find_element(By.CLASS_NAME, "calendar__time").text
            currency_elem = row.find_element(By.CLASS_NAME, "calendar__currency").text
            impact_elem = row.find_element(By.XPATH, "//td[contains(@class, 'calendar__impact')]/span").get_attribute("class")
            event_elem = row.find_element(By.CLASS_NAME, "calendar__event").text
            actual_elem = row.find_element(By.CLASS_NAME, "calendar__actual").text
            forecast_elem = row.find_element(By.CLASS_NAME, "calendar__forecast").text
            previous_elem = row.find_element(By.CLASS_NAME, "calendar__previous").text

            # Extract impact level from class name
            if "red" in impact_elem:
                impact = "High"
            elif "medium" in impact_elem:
                impact = "Medium"
            elif "yel" in impact_elem:
                impact = "Low"
            else:
                impact = ""

            events.append({
                "time": time_elem,
                "currency": currency_elem,
                "impact": impact,
                "event": event_elem,
                "actual": actual_elem,
                "forecast": forecast_elem,
                "previous": previous_elem,
            })
        except Exception:
            continue
except Exception as e:
    print(f"Error retrieving rows: {e}")
    # driver.quit()
    # exit(1)

# Convert to DataFrame
df = pd.DataFrame(events)
df_high_impact = df.loc[df['impact'] == 'High']
df.to_csv("forex_factory_calendar.csv", index=False)
print("Data saved to forex_factory_calendar.csv")



tz = pytz.timezone("Africa/Lagos")
naija_now = datetime.datetime.now(tz)


# minutes_to_add = (time_frame - naija_now.minute % time_frame) % time_frame
# if minutes_to_add == 0:  # If already at a 5-minute mark, move to the next one
#     minutes_to_add = time_frame
# rounded_time = (naija_now + datetime.timedelta(minutes=minutes_to_add)).replace(second=0, microsecond=0)

# Step 3: Calculate the time difference in seconds


# Monitor the events and wait until actual data appears
for event in events:
    event_time_str = event["time"]
    if event_time_str:
        try:
            event_time = datetime.strptime(event_time_str, "%I:%M%p").time()
            while datetime.now().time() < event_time:
                # remaining_time = (datetime.combine(datetime.today(), event_time) - datetime.now()).total_seconds()
                time_to_sleep = (event_time - naija_now).total_seconds()
                print('Trade On pause till: ', event_time)        
                # sleep(time_to_sleep - 2)
                if time_to_sleep <= 2:
                    break
                print(f"Waiting for actual value of: {event['event']} ({event['currency']})")
                time.sleep(time_to_sleep - 2)

            # print(f"Waiting for actual value of: {event['event']} ({event['currency']})")
            while True:
                try:
                    actual_value = driver.find_element(By.XPATH, "//td[contains(@class, 'calendar__actual')]").text
                    if actual_value not in ["", "-"]:
                        span_class = driver.find_element(By.XPATH, "//td[contains(@class, 'calendar__actual')]/span").get_attribute("class")
                        status = "Better" if "better" in span_class else "Worse" if "worse" in span_class else "N/A"
                        print(f"Actual: {actual_value}, Status: {status}")
                        break
                except:
                    pass
                time.sleep(0.3)
        except Exception as e:
            print(f"Error processing event {event['event']}: {e}")

# driver.quit()


