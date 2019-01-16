from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import urllib.request
import time
route = r"C:\Users\ShiueFeng\Documents\chromedriver.exe"
def facebook():
    try:
        browser = webdriver.Chrome(route)
        browser.get('https://www.facebook.com/pg/K.M.Team83/photos/?ref=page_internal')
        time.sleep(10)
        #page scroll
        for i in range(0, 20):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        #find every img shortcut
        elems = browser.find_elements_by_css_selector("div._2eea > a")
        #get urls
        urls = list()
        for elem in elems:
            urls.append(elem.get_attribute("href"))
        #url loop
        for url in reversed(urls):
            browser.get(url)
            time.sleep(1)
            #before click
            front = browser.find_element_by_css_selector("div#u_0_e")
            if front.is_displayed():
                browser.find_element_by_css_selector("a#expanding_cta_close_button").click()
                time.sleep(1)
            #img click
            browser.find_element_by_css_selector("a._4-eo").click()
            time.sleep(2)
            #find img
            try:
                img = browser.find_element_by_css_selector("div._2-sx > img.spotlight")
                time.sleep(2)
            except:
                print('[Error] browser.find_element_by_css_selector("div._2-sx > img.spotlight")')
                continue
            #get img url
            try:
                src = img.get_attribute("src")
            except Exception as e: 
                print(e)
                continue
            #filename process
            filename = src
            filename = filename[filename.find('?oh=') + 4 : filename.find('&oe')]
            #download img
            PATH = 'downloads/'
            urllib.request.urlretrieve(src, PATH + filename + '.jpg')
            print('downloaded....')
    except Exception as e:
        print(e)
        pass
    finally:
        browser.close()
facebook()

