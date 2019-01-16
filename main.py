import logging
import os
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

route = r"PATH/TO/WEBDRIVER"

class facebook:
    PATH = r'PATH/TO/FOLDER'
    LBOUND = 25
    logging.basicConfig(filename='fb_crawler.log', level=logging.INFO, format='%(asctime)s\t%(levelname)s\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def __init__(self, keys):
        self.keys = keys
        self.duplicate_count = 0
        self.crash_count = 0
        self.bound = None

    def __str__(self):
        return '[Crawler] facebook({0})'.format(self.keys)

    def open(self):
        self.browser = webdriver.Chrome(route)
        print('[Webdriver] opening...')
        logging.info('Webdriver opening...')

    def close(self):
        self.browser.close()
        print('[Webdriver] closing...')
        logging.info('Webdriver closing...')

    def crawl_by_page(self, index = -1):
        if index == -1:
            return
        key = self.keys[index - 1]
        #連上網頁
        self.browser.get(self.get_link_by_key(key))
        time.sleep(3)
        #取得第一個方框連結
        self.click_first_div()
        self.find_img(key)

    def crawl_by_albums(self, index = 0):
        if index == 0:
            logging.error('index not found')
            return
        key = self.keys[index - 1]
        self.browser.get(self.get_link_by_key(key))
        time.sleep(3)
        album_urls = list()
        album_blocks = self.browser.find_elements_by_css_selector("div._3rte > a")
        time.sleep(1)
        for album_block in album_blocks:
            album_urls.append(album_block.get_attribute("href"))
        for album_url in album_urls:
            self.browser.get(album_url)
            time.sleep(3)
            self.click_first_div()
            time.sleep(2)
            self.find_img(key)
            logging.info('{key} ({album_url}) download complete...'.format(key=key,album_url=album_url))
            print('{key} ({album_url}) download complete...'.format(key=key,album_url=album_url))
        logging.info('{key} download finish...'.format(key=key))
        print('{key} download finish...'.format(key=key))
        self.__init__(self.keys)

    def crawl_from_crach(self, url, key):
        self.browser.get(url)
        time.sleep(5)
        self.browser.execute_script("arguments[0].click();", self.browser.find_element_by_css_selector("div > a#u_0_m, div > a._4-eo"))
        time.sleep(2)
        self.find_img(key)

    def get_link_by_key(self, key):
        return 'https://www.facebook.com/pg/{0}/photos/?tab=albums'.format(key)

    def click_first_div(self):
        first = self.browser.find_element_by_css_selector("div._2eea > a")
        time.sleep(1)
        self.browser.execute_script("arguments[0].click();", first)
        time.sleep(3)

    def find_img(self, key):

        def download(img, key):

            def check_dir_exist(DIR):
                if not os.path.exists(DIR):
                    os.makedirs(DIR)
                    logging.warning('directory {DIR} not found'.fromat(DIR=DIR))
                    return False
                return True

            def set_bound_of_duplicate(DIR):
                return int(len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])**(0.5))

            def check_file_exist(src, key, filename, filepath):

                def check_if_duplicate():
                    if self.duplicate_count >= self.bound + self.LBOUND:
                        self.duplicate_count = 0
                        return 0
                    else:
                        return 1

                if not os.path.isfile(filepath):
                    self.duplicate_count = 0 #把 i 歸零
                    print('[Download] {key} {filename}.jpg downloading... status {status}/{bound}'.format(key = key, filename = filename, status = self.duplicate_count, bound = self.bound + self.LBOUND))
                    logging.info('{key} {filename}.jpg downloading... status {status}/{bound} ({page})'.format(key = key, filename = filename, status = self.duplicate_count, bound = self.bound + self.LBOUND, page = self.browser.current_url))
                    urllib.request.urlretrieve(src, filepath)
                    return 1
                else:
                    self.duplicate_count += 1
                    print('[Download] {key} {filename}.jpg already downloading... status {status}/{bound}'.format(key = key, filename = filename, status = self.duplicate_count, bound = self.bound + self.LBOUND))
                    logging.info('[Download] {key} {filename}.jpg already downloading... status {status}/{bound} ({page})'.format(key = key, filename = filename, status = self.duplicate_count, bound = self.bound + self.LBOUND, page = self.browser.current_url))
                    return check_if_duplicate()

            try:
                src = img.get_attribute("src")
            except Exception as e: 
                logging.error(e)
                return -1
            filename = src[src.find('oh=') + 3 : src.find('&oe')]
            if self.bound == None:
                if check_dir_exist(self.PATH + key):
                    self.bound = set_bound_of_duplicate(self.PATH + key)
                else:
                    self.bound = 0
            filepath = self.PATH + key + '/' + filename + '.jpg'
            return check_file_exist(src, key, filename, filepath)

        def crash_process():
            self.close()
            time.sleep(1)
            self.open()
            time.sleep(2)
            self.browser.get(url) # <- current_album , whole_album

        while True:
            img = None
            while img is None:
                try:
                    img = self.browser.find_element_by_css_selector("div._2-sx > img.spotlight")
                    time.sleep(2)
                    status = download(img, key)
                    if status == 0:
                        return
                except:
                    self.crash_count += 1
                    logging.warning('image not found in {key} current url {current}'.format(key=key, current = self.browser.current_url))
                    time.sleep(2)
                    #超過1分鐘設為timeout
                    if self.crash_count >= 30:
                        #self.crash_count = 0
                        pass#crash_process()
            self.crash_count = 0
            while True:
                try:
                    self.browser.execute_script("arguments[0].click();", self.browser.find_element_by_css_selector("div > a.next"))
                    break
                except:
                    print('[Error] cant find the img')
                    pass
                time.sleep(2)
