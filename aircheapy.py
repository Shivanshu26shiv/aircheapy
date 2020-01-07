'''
Indian to International and vice-versa cheap flight fare scanner
'''

from selenium import webdriver
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException,
                                        ElementClickInterceptedException,
                                        ElementNotInteractableException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functools import partial
import multiprocessing
from multiprocessing.pool import ThreadPool
import pprint as pp
import geocoder
import requests
import time
import sys

options = Options()
options.add_argument("--headless")
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--disable-dev-shm-usage')        

prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 0}
options.add_experimental_option("prefs", prefs)

args = ["hide_console", ]


def calculate(params, to_single_iata):
    # driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe', service_args=args)
    driver = webdriver.Chrome(options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe')
    
    try:
        final_output = {}
        
        if 'scan_till_N_days' not in params.keys(): scan_till_N_days = 30
        else: scan_till_N_days = params['scan_till_N_days']
        if 'cheapest_N_results' not in params.keys(): cheapest_N_results = None
        else: cheapest_N_results = params['cheapest_N_results']
        if 'maxINR' not in params.keys(): maxINR = 9999999
        else: maxINR = params['maxINR']
        if 'maxGap' not in params.keys(): maxGap = scan_till_N_days-2
        else: maxGap = params['maxGap']
        if 'cabinClass' not in params.keys(): cabinClass = 'Economy'
        else: cabinClass = params['cabinClass']
        if 'adults' not in params.keys(): adults = 1
        else: adults = params['adults']
        
        to_IATA = params['to_IATA']        
        from_IATA = params['from_IATA']
    
        from_single_iata=list(from_IATA.keys())[0]
        url = 'https://www.happyeasygo.com/flights/'+from_single_iata+'-'+to_single_iata
        url_params = '?adults='+str(adults)+'&cabinClass='+cabinClass
        print('url+url_params:', url+url_params)
        driver.get(url+url_params)
        # driver.refresh()
        driver.execute_script("location.reload(true);")
        time.sleep(5)
        driver.find_element_by_css_selector('body')
        webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()

        round_trip = from_IATA[from_single_iata]+'->'+to_IATA[to_single_iata]+'->'+from_IATA[from_single_iata]
        # print('Path:', round_trip)
        ld={}
        def calender(id_name):
            try:
                time.sleep(2)
                driver.find_element_by_id(id_name).click()
            except:
                try:
                    time.sleep(4)
                    driver.find_element_by_id(id_name).click()
                except:
                    print('Poor connectivity or unknown error... skipping')
                    return {}
                
            # not working
            # el=driver.find_element_by_id(id_name)
            # driver.execute_script("arguments[0].click();", el)
            
            time.sleep(2)
            l=[]
            for c, e in enumerate(driver.find_elements_by_xpath('//td[@data-handler="selectDay"]')):
                try:
                    if e.get_attribute("title") != '':
                        # print('Airfare:', e.get_attribute("title"))
                        l.append(((datetime.now() + timedelta(days=c)).strftime("%Y%m%d"), int(float(e.get_attribute("title")))))
                except:
                    print('Airfare issue:', e.get_attribute("title"))
                    continue

                if c==scan_till_N_days:
                    break
                
            ld[round_trip] = l
            return ld

        try:
            depart  = calender('D_date')[round_trip]
            arrival = calender('R_date')[round_trip]
        except KeyError:
            driver.quit()
            return

        d={}
        for i in depart:
            for j in arrival:
                if i[0] <= j[0] and ((datetime.strptime(j[0], "%Y%m%d")-datetime.strptime(i[0], "%Y%m%d")).days <= maxGap) and i[1]+j[1] <= maxINR:
                    d[i[0]+'-'+j[0]] = i[1]+j[1]

        # print('d:', d)

        new_d = {}
        if d != {}:
            d=sorted(d.items(), key=lambda item: item[1])[:cheapest_N_results]

            for date_strings, cached_price in d:
                from_str = datetime.strptime(date_strings.split('-')[0], '%Y%m%d')
                to_str   = datetime.strptime(date_strings.split('-')[1], '%Y%m%d')
                new_url = url+'/'+from_str.strftime("%Y-%m-%d")+'-'+to_str.strftime("%Y-%m-%d")+url_params
                # print('new_url:', new_url)
                key = (from_str.strftime("%d %B %Y (%A)")+' to '+to_str.strftime("%d %B %Y (%A)"))
                try:
                    driver.get(new_url)
                    driver.execute_script("location.reload(true);")
                    key = key+' ['+driver.current_url+']'
                    time.sleep(5)

                    
                    
                    new_price = driver.find_elements_by_class_name('fpr')[0].text
                    new_price = eval((new_price.strip()).replace(',',''))
                    value = new_price
                except (NoSuchElementException,
                        ElementClickInterceptedException,
                        ElementNotInteractableException):
                    try:
                        time.sleep(3)
                        new_price = driver.find_elements_by_class_name('fpr')[0].text
                        new_price = eval((new_price.strip()).replace(',',''))
                        value = new_price
                    except:
                        key = key+' (cached)'
                        value = cached_price
                except:
                    ele=driver.find_element_by_id('no_result')
                    # print('>>', ele.get_attribute("display"))
                    if ele.get_attribute("display") == None:
                        continue
                    else:
                        key = key+' (cached)'
                        value = cached_price

                new_d[key] = value

            new_d=sorted(new_d.items(), key=lambda item: item[1])
            # print('new_d:', round_trip, new_d)
            final_output[round_trip] = new_d
        
        driver.quit()
        return
    
    finally:
        pp.pprint(final_output)
        driver.quit()


def aircheapy(params, get_current_ips_IATA, use_threading):

    assert sys.version_info >= (2, 7), 'Python version should be at least 2.7'
    assert (not(get_current_ips_IATA and 'from_IATA' in params.keys()) and
            (not(get_current_ips_IATA is False and 'from_IATA' not in params.keys()))), "Flag 'get_current_ips_IATA' and constant 'from_IATA' are mutually exclusive"
    
    tim = datetime.now()
    
    scan_till_N_days = params['scan_till_N_days']
    cheapest_N_results = params['cheapest_N_results']
    maxINR = params['maxINR']
    maxGap = params['maxGap']
    to_IATA = params['to_IATA']

    from_IATA={}
    # getting current ip's iata code
    if get_current_ips_IATA:
        g = geocoder.ip('me')
        r = requests.get("http://iatageo.com/getCode/"+str(g.latlng[0])+"/"+str(g.latlng[1]))
        if r.status_code == 200:
            from_IATA[eval(r.content)['IATA']] = str(g[0]).split(',')[0].lstrip('[')
    else:
        from_IATA = params['from_IATA']

    params['from_IATA'] = from_IATA
    
    print('params:', params)

    try:
        if use_threading:
            func = partial(calculate, params)
            pool = ThreadPool(processes=multiprocessing.cpu_count())
            pool.map(func, list(to_IATA.keys()))
            pool.close()
            pool.join()
        else:
            for to_single_iata in to_IATA.keys():
                calculate(params, to_single_iata)     
    finally:
        # pp.pprint(final_output)
        print('Start:', tim, ' Stop:', datetime.now())


params = {
        'maxINR': 30000,
        'maxGap': 10,
        'cheapest_N_results': 2,
        'scan_till_N_days': 30,
        'adults': 2,
        'cabinClass': 'Premium Economy', # Economy, Business, First, Premium Economy
        # 'from_IATA': {'BLR': 'Bengaluru'}, 
        'to_IATA':
                {
                 # 'BKK': 'Bangkok',
                 'DXB': 'Dubai'
                 }
        }

    
aircheapy(params, get_current_ips_IATA=True, use_threading=True)
