from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import re

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
login_url = 'http://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com'
browser = webdriver.Chrome(executable_path='E:\py_code\webdriver/chromedriver.exe', options=chrome_options)
cookie_dict = {}


def get_cookies():
    browser.get(login_url)
    try:
        username = input('输入手机号:')
        browser.find_element_by_xpath('//*[@id="phone"]').send_keys(username)
        password = input('输入密码:')
        browser.find_element_by_xpath('//*[@id="pwd"]').send_keys(password)
        browser.find_element_by_xpath('//*[@id="loginBtn"]').click()
    except NoSuchElementException:
        print('未找到元素，请重新检查网页')
    normal_window = browser.current_window_handle
    cookie = browser.get_cookies()
    cookie_dict['name'] = cookie[-1]['name']
    cookie_dict['value'] = cookie[-1]['value']
    pass


def play_video(url):
    browser.add_cookie(cookie_dict)
    browser.get(url)
    normal_window = browser.current_window_handle
    browser.switch_to.frame(browser.find_element_by_id('iframe'))
    ele_temp = browser.find_elements_by_tag_name('iframe')
    browser.switch_to.frame(ele_temp[-1])

    try:
        browser.find_element_by_xpath('//*[@id="video"]/button').click()
        time.sleep(1)
        page_source = browser.page_source
        sel = Selector(text=page_source)
        begin_time = sel.re(r'<span class="vjs-current-time-display" aria-live="off">(.*?):.*?</span>')
        sleep_time = sel.re(r'<span class="vjs-duration-display" aria-live="off">(.*?):(.*?)</span>')
        time_temp = int(sleep_time[0]) * 60 + int(sleep_time[1]) + 30 - int(begin_time[0]) * 60
        print(time_temp)
        time.sleep(time_temp)
    except NoSuchElementException:
        pass
    pass


'''
<span class="vjs-duration-display" aria-live="off">(.*?)</span>
<span class="vjs-current-time-display" aria-live="off">(.*?):.*?</span>
'''

if __name__ == '__main__':
    get_cookies()
    url = input('输入学习通视频网址:')
    play_video(url)
