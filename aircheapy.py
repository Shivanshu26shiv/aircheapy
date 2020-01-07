'''
from selenium import webdriver
url = 'https://www.google.com/flights?hl=it#flt=/m/07_pf./m/05qtj.2019-04-27;c:EUR;e:1;sd:1;t:f;tt:o'
driver = webdriver.Chrome()
driver.get(url)
print(driver.find_element_by_css_selector('.gws-flights-results__cheapest-price').text)
driver.quit()
'''

from selenium import webdriver
from datetime import datetime
from datetime import timedelta
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException,
                                        WebDriverException,
                                        ElementClickInterceptedException,
                                        ElementNotInteractableException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from functools import partial
import multiprocessing
from multiprocessing.pool import ThreadPool
import pprint as pp
import geocoder
import requests

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

def calculate(from_dest, to_dest):
    # driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe', service_args=args)
    driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\Xarvis-PC\Desktop\chromedriver_win32\chromedriver.exe')
    
    try:
        url='https://www.happyeasygo.com/flights/'+from_dest+'-'+to_dest
        print('url:', url)
        driver.get(url)
        # driver.refresh()
        driver.execute_script("location.reload(true);")
        time.sleep(5)
        driver.find_element_by_css_selector('body')
        webdriver.ActionChains(driver).send_keys(Keys.PAGE_UP).perform()

        round_trip = from_dest_dict[from_dest]+'->'+to_dest_dict[to_dest]+'->'+from_dest_dict[from_dest]
        print('Path:', round_trip)
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
                    print('Poor connectivity... skipping')
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

                if c==TILL_N_DAYS:
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
                if i[0] <= j[0] and ((datetime.strptime(j[0], "%Y%m%d")-datetime.strptime(i[0], "%Y%m%d")).days <= MAX_GAP_OF_DAYS) and i[1]+j[1] <= INR_MAX:
                    d[i[0]+'-'+j[0]] = i[1]+j[1]

        # print('d:', d)

        new_d = {}
        if d != {}:
            d=sorted(d.items(), key=lambda item: item[1])[:CHEAPEST_N_RESULTS]

            for date_strings, cached_price in d:
                from_str = datetime.strptime(date_strings.split('-')[0], '%Y%m%d')
                to_str   = datetime.strptime(date_strings.split('-')[1], '%Y%m%d')
                new_url = url+'/'+from_str.strftime("%Y-%m-%d")+'-'+to_str.strftime("%Y-%m-%d")
                # print('new_url:', new_url)
                key = (from_str.strftime("%d %B %Y (%A)")+' to '+to_str.strftime("%d %B %Y (%A)"))
                try:
                    driver.get(new_url)
                    driver.execute_script("location.reload(true);")
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
                    key = key+' (cached)'
                    value = cached_price

                new_d[key] = value
                
            new_d=sorted(new_d.items(), key=lambda item: item[1])
            # print('new_d:', round_trip, new_d)
            final[round_trip] = new_d
        
        driver.quit()
        return
    
    finally:
        driver.quit()


if __name__ == '__main__':
    tim = datetime.now()
    
    ###########################
    TILL_N_DAYS = 60 # max is 60
    CHEAPEST_N_RESULTS = 2
    INR_MAX = 20000
    MAX_GAP_OF_DAYS = 10
    ###########################    

    from_dest_dict={}

    # getting current ip's iata code
    try:
        g = geocoder.ip('me')
        r = requests.get("http://iatageo.com/getCode/"+str(g.latlng[0])+"/"+str(g.latlng[1]))
        if r.status_code == 200:
            from_dest_dict[eval(r.content)['IATA']] = str(g[0]).split(',')[0].lstrip('[')
    except:
        from_dest_dict = {'BLR': 'Bengaluru'}

    print(from_dest_dict)

    to_dest_dict = {'PEK': 'Beijing', 'LHR': 'London', 'HND': 'Tokyo', 'CDG': 'Paris', 'FRA': 'Frankfurt', 'HKG': 'Hong Kong',
                    'DXB': 'Dubai', 'JFK': 'New York', 'AMS': 'Amsterdam', 'CGK': 'Jakarta', 'BKK': 'Bangkok', 'SIN': 'Singapore',
                    'PVG': 'Shanghai', 'FCO': 'Rome', 'SYD': 'Sydney', 'MIA': 'Miami'}

    to_dest_dict = {'BKK': 'Bangkok', 'DXB': 'Dubai', 'HND': 'Tokyo'}

    final = {}
    try:
        print('MAX_GAP_OF_DAYS:', MAX_GAP_OF_DAYS)
        
        try:
            INR_MAX = INR_MAX
            print('INR_MAX:', INR_MAX)
        except NameError:
            INR_MAX = 999999999

        try:
            CHEAPEST_N_RESULTS = CHEAPEST_N_RESULTS
            print('CHEAPEST_N_RESULTS:', CHEAPEST_N_RESULTS)
        except NameError:
            CHEAPEST_N_RESULTS = None
            
        from_de=from_dest_dict.keys()[0]

        '''
        calculate(from_de, 'BKK')
        calculate(from_de, 'FCO')
        calculate(from_de, 'DXB')
        '''
        func = partial(calculate, from_de)
        pool = ThreadPool(processes=4)
        pool.map(func, to_dest_dict.keys())
        pool.close()
        pool.join()
        
    finally:
        pp.pprint(final)
        print 'Start:', tim, ' Stop:', datetime.now()

