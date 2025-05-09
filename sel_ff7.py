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
# import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


import MetaTrader5 as mt5
# import numpy as np
# import datetime
# import pandas as pd
import pytz
# import pandas_ta as ta
# from time import sleep


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

def open_trade(symbol, trade_type, volume, comment, impact):
    trade_action = mt5.ORDER_TYPE_BUY if trade_type == "Buy" else mt5.ORDER_TYPE_SELL
    price = mt5.symbol_info_tick(symbol).ask if trade_type == "Buy" else mt5.symbol_info_tick(symbol).bid
    point = mt5.symbol_info(symbol).point
    sl_val = 80 if impact == 'L' else 120
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_action,
        "price": price,
        "deviation": 10,
              
        # "tp": price * 1.0005 if trade_type == "Buy" else price * 0.9995, # 0.05%
        "sl": price - (sl_val * point) if trade_type == "Buy" else price + (sl_val * point),
        # "sl": price * 0.999 if trade_type == "Buy" else price * 1.001, # 0.1%
            
        "tp": price - (40 * point) if trade_type == "Sell" else price + (40 * point),
        "magic": 123,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    try:
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to open trade for {symbol}: {result.retcode}")
        else:
            print(f"Opened trade: {symbol}, {volume} lots, {'Buy' if trade_type == 'Buy' else 'Sell'}")
    except:
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Failed to open trade for {symbol}: {result.retcode}")
        pass
        


# 2. Initialize Selenium WebDriver
driver = webdriver.Chrome() # options=options)
# Navigate to Forex Factory Calendar
driver.get("https://www.forexfactory.com/calendar?day=today")
# time.sleep(5)  # Allow page to load
WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

prev_time_elem = '12:01am'
tz = pytz.timezone("Africa/Casablanca")
naija_now = datetime.now(tz)

# INITIATE EVENT TIME TO AVOID LOOP ERROR WHEN THE DAY STARTS WITH A BAD EVENT TIME
event_time = datetime.strptime(prev_time_elem, "%I:%M%p").time()
event_time = datetime.combine(naija_now.date(), event_time)
event_time = tz.localize(datetime.combine(datetime.today(), event_time.time()))
prev_event_time = event_time

attempt = 1
page_loaded = False

while True:
    try:
        event_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__event')]")
        if len(event_elems) < 1: 
            while attempt <= 5 and not page_loaded:
                try:
                    driver.quit()
                    driver = webdriver.Chrome() # options=options)
                    driver.get("https://www.forexfactory.com/calendar?day=today") 
                    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete") 
                    page_loaded = True
                    attempt = 1
                except Exception as e:
                    print(f"Page not fully loaded yet (Attempt {attempt}/5). Error: {e}")
                    attempt += 1
                    time.sleep(5)
                    continue
            event_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__event')]")
        impact_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__impact')]/span")
        currency_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__currency')]")
        forecast_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__forecast')]")
        time_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__time')]")
        for i in range(len(event_elems)):
            print('')
            print('Row ', i , '/', len(event_elems))
            # print('')
            try: 
                naija_now = datetime.now(tz)
                event_time = datetime.strptime(time_elems[i].text, "%I:%M%p").time()
                event_time = datetime.combine(naija_now.date(), event_time)
                # print("2 time switched to time format successful")
                
                event_time = tz.localize(datetime.combine(datetime.today(), event_time.time()))
                prev_event_time = event_time
            except:
                event_time = prev_event_time
                print('E1')
                # event_time = tz.localize(datetime.combine(datetime.today(), event_time.time()))
                pass
                # continue

            # event_time, event_elem, currency_elem, forecast_elem = get_news(i, prev_time_elem, driver)
            
            if event_time > datetime.now(tz) - timedelta(minutes=1):
                print('Eventime: ', event_time)
                print('Nowtime: ', datetime.now(tz))
                print('time to wait: ', (event_time - (datetime.now(tz) + timedelta(minutes=1))).total_seconds(), ' seconds')
                print(f"1. Waiting for actual value of: {event_elems[i].text} ({currency_elems[i].text})")
                try:
                    time.sleep((event_time - (datetime.now(tz) + timedelta(minutes=0.7))).total_seconds())
                    # time.sleep(30)
                except:
                    print('E2')
                    pass
                # Navigate to Forex Factory Calendar
                driver.quit()
                driver = webdriver.Chrome() # options=options)
                
                # open new FF
                driver.get("https://www.forexfactory.com/calendar?day=today")
                time.sleep(5)  # Allow page to load
                            
                event_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__event')]")
                if len(event_elems) < 1: 
                    while attempt <= 5 and not page_loaded:
                        try:
                            driver.quit()
                            driver = webdriver.Chrome() # options=options)
                            driver.get("https://www.forexfactory.com/calendar?day=today") 
                            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete") 
                            page_loaded = True
                            attempt = 1
                        except Exception as e:
                            print(f"Page not fully loaded yet (Attempt {attempt}/5). Error: {e}")
                            attempt += 1
                            time.sleep(5)
                            continue
                    event_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__event')]")
                impact_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__impact')]/span")
                currency_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__currency')]")
                forecast_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__forecast')]")
                time_elems = driver.find_elements(By.XPATH, "//td[contains(@class, 'calendar__time')]")
                
            # for j in range(i+1):
                j = i
                try: 
                    naija_now = datetime.now(tz)
                    event_time = event_time if time_elems[j].text == "" else datetime.strptime(time_elems[j].text, "%I:%M%p").time()
                    event_time = datetime.combine(naija_now.date(), event_time)
                    # print("2 time switched to time format successful")
                    # print(f"Done: {event_elems[j].text} ({currency_elems[j].text})")
                    event_time = tz.localize(datetime.combine(datetime.today(), event_time.time()))
                    # impact_ele = impact_elems[j].get_attribute("title")
                except:
                    print('E3')
                    # event_time = 0
                    # event_time = tz.localize(datetime.combine(datetime.today(), event_time.time()))
                    pass
                
                # rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'calendar__row')]")
                # row = rows[i]
                # event_time, event_elem, currency_elem, forecast_elem = get_news(i, prev_time_elem, driver)
                impact_ele = impact_elems[j].get_attribute("title")
                if  event_time > datetime.now(tz) - timedelta(minutes=8):
                    print(f"NEWS TIME  FOR: {event_elems[j].text} ({currency_elems[j].text})")
                    
                    try:
                        # Wait until the <span> inside the .calendar__actual cell appears
                        WebDriverWait(driver, 200).until(
                            EC.presence_of_element_located((By.XPATH, f"(//td[contains(@class, 'calendar__actual')])[{j+1}]/span"))
                        )
                        
                        # Extract row text
                        row_text = driver.execute_script(
                            f"return document.querySelectorAll('.calendar__actual')[{j+1}].innerText;"
                        )
                        
                        # Extract span text and class
                        span_data = driver.execute_script(
                            f"""
                            let elem = document.querySelectorAll('.calendar__actual')[{j+1}].querySelector('span');
                            return elem ? {{ text: elem.innerText, class: elem.className }} : {{ text: null, class: null }};
                            """
                        )
                        
                        actual_value = span_data["text"]
                        status = span_data["class"]
                        
                        print(f"Row {j} detected - Text: {row_text}, Span Text: {actual_value}, Span Class: {status}")

                        
                        print(f"Actual: {actual_value}, Status: {status}")
                        news_zone = currency_elems[j].text
                        
                        print('News zone: ', news_zone)
                        if news_zone == 'GBP':
                            currs1 = ['GBPJPY','GBPUSD', 'GBPCAD', 'GBPAUD', 'GBPNZD']
                            currs2 = ['EURGBP']
                        elif news_zone == 'EUR':
                            currs1 = ['EURUSD', 'EURGBP', 'EURCAD', 'EURJPY', 'EURAUD', 'EURCHF']
                            currs2 = []
                        elif news_zone == 'USD':
                            currs1 = ['USDJPY', 'USDCAD', 'USDCHF']
                            currs2 = ['GBPUSD', 'EURUSD', 'XAUUSD', 'AUDUSD', 'BTCUSD', 'NZDUSD']         
                        elif news_zone == 'CC':
                            currs = ['BTCUSD', 'ETHUSD', 'DOGUSD', 'SOLUSD']
                        elif news_zone == 'AUD':    
                            currs1 = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD']
                            currs2 = ['GBPAUD', 'EURAUD',]
                        elif news_zone == 'JPY':    
                            currs1 = []
                            currs2 = ['GBPJPY', 'AUDJPY', 'USDJPY', 'CADJPY']
                        elif news_zone == 'NZD':    
                            currs1 = ['NZDUSD', 'NZDCAD', 'NZDJPY' ]
                            currs2 = ['AUDNZD', 'EURNZD', 'GBPNZD']
                        elif news_zone == 'CHF':    
                            currs1 = ['CHFJPY' ]
                            currs2 = ['AUDCHF', 'EURCHF', 'GBPCHF', 'USDCHF']
                        elif news_zone == 'CAD':    
                            currs1 = ['CADJPY' ]
                            currs2 = ['GBPCAD', 'EURCAD', 'USDCAD','NZDCAD', 'AUDCAD']
                        else:
                            currs1 = []  
                            currs2 = []
                            
                        commm = impact_ele[0] + ' ' + event_elems[i].text
                        if impact_ele[0] == 'H' or impact_ele[0] == 'M': #and 'Farm' in  event_elems[i].text:
                            time.sleep(30)
                            if status == 'better': #'better':
                                
                                for curr in currs1:
                                    
                                    open_trade(curr, "Sell", 1.0, commm, impact_ele[0])
                                for curr in currs2: 
                                    open_trade(curr, "Buy", 1.0, commm, impact_ele[0])
                                
                            elif status == 'worse':#'worse':
                                for curr in currs1:
                                    open_trade(curr, "Buy", 1.0, commm, impact_ele[0])
                                for curr in currs2: 
                                    open_trade(curr, "Sell", 1.0, commm, impact_ele[0])
                            else:
                                print('Gray actual')
                            
                        else:
                            # time.sleep(0.01)
                            if status == 'worse': #'better':
                                for curr in currs1:
                                    
                                    open_trade(curr, "Sell", 1.0, commm, impact_ele[0])
                                for curr in currs2: 
                                    open_trade(curr, "Buy", 1.0, commm, impact_ele[0])
                                
                            elif status == 'better':#'worse':
                                for curr in currs1:
                                    open_trade(curr, "Buy", 1.0, commm, impact_ele[0])
                                for curr in currs2: 
                                    open_trade(curr, "Sell", 1.0, commm, impact_ele[0])
                            else:
                                print('Gray actual')
                        
                        # actual_checker = 0
                        # break
                    
                
                    except TimeoutException:
                        print('E4')
                        print("Timeout waiting for actual value.")
                        driver.quit()
                        driver = webdriver.Chrome() # options=options)
                        
                        # open new FF
                        driver.get("https://www.forexfactory.com/calendar?day=today")
                        time.sleep(5)
                        pass
                        # break  # Exit loop after timeout
                    except Exception as e:
                        print('E5')
                        time.sleep(0.1)
                        # actual_checker = actual_checker+1
    
                        print(f"Error retrieving rows: {e}")
    
                        print('check 4: error in actual checker')
                        driver.quit()
                        driver = webdriver.Chrome() # options=options)
                        
                        # open new FF
                        driver.get("https://www.forexfactory.com/calendar?day=today")
                        time.sleep(5)
                        continue
                        # pass
                        # break
                        # rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'calendar__row')]")
            else:
                print(f"Done: {event_elems[i].text} ({currency_elems[i].text}) - {impact_elems[i].get_attribute("title")}")
                try:
                    # Wait until the <span> inside the .calendar__actual cell appears
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, f"(//td[contains(@class, 'calendar__actual')])[{i+1}]/span"))
                    )
                    
                    # Extract row text
                    row_text = driver.execute_script(
                        f"return document.querySelectorAll('.calendar__actual')[{i+1}].innerText;"
                    )
                    
                    # Extract span text and class
                    span_data = driver.execute_script(
                        f"""
                        let elem = document.querySelectorAll('.calendar__actual')[{i+1}].querySelector('span');
                        return elem ? {{ text: elem.innerText, class: elem.className }} : {{ text: null, class: null }};
                        """
                    )
                    
                    actual_value = span_data["text"]
                    status = span_data["class"]
                    
                    print(f"Row {i} detected - Text: {row_text}, Span Text: {actual_value}, Span Class: {status}")

                    
                    print(f"Actual: {actual_value}, Status: {status}")
                except:
                    print('E6')
                    # pass
                    continue
        # Get the current datetime in Casablanca
        nnow = datetime.now(tz)
        
        # Define 11:59 PM on the same day
        target_time = nnow.replace(hour=23, minute=59, second=59, microsecond=0)
        if nnow < target_time:
            
            
            # Calculate the time difference in seconds
            seconds_to_wait = (target_time - nnow).total_seconds()
            print('NO MORE NEWS! ON SLEEP TILL 12 MIDNIGHT!')
            time.sleep(seconds_to_wait+10)
            
            driver.quit()
            driver = webdriver.Chrome() # options=options)
            
            # open new FF
            driver.get("https://www.forexfactory.com/calendar?day=today")
            time.sleep(5)
    except Exception as e:
        print('E7')
        print(f"Error retrieving rows: {e}")
        print('check 1: error in getting the rows of calendar 1')
        continue
    # driver.quit()
    # exit(1)











