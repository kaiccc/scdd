# coding=utf-8
import time
import sys
import logging
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

chrome_opt = webdriver.ChromeOptions()
# 无gui参数
# chrome_opt.add_argument('--headless')
# chrome_opt.add_argument('--no-sandbox')

chrome_opt.add_argument('lang=zh_CN.GB2312')
browser = webdriver.Chrome(executable_path='chrome/chromedriver.exe', chrome_options=chrome_opt)

player_over_list = []


def login():
    browser.get('http://edu.codmr.com/login')
    browser.find_element_by_id('login-username').send_keys(username)
    browser.find_element_by_id('login-password').send_keys(password)
    verify_code_base = browser.find_element_by_id('verifyCode').screenshot_as_base64
    logging.info(verify_code_base)
    verify = verify_code_identify(verify_code_base)
    browser.find_element_by_id('login-verifycode').send_keys(verify)
    browser.find_element_by_class_name('am-btn-secondary').click()


def verify_code_identify(image):
    url = 'https://v2-api.jsdama.com/upload'
    params = {
        "softwareId": 14013,
        "softwareSecret": "",
        "username": "",
        "password": "",
        "captchaData": image,
        "captchaType": 1001,
        "captchaMinLength": 4
    }
    r = requests.post(url, json=params)
    rest = json.loads(r.text)
    logging.info('验证码识别: %s', rest)
    return rest['data']['recognition']


def course_jump():
    time.sleep(3)
    browser.find_element_by_css_selector("a[title*='开始学习']").click()
    time.sleep(10)


def course_video():
    browser.switch_to.window(browser.window_handles[1])
    video_div_list = []
    time.sleep(2)
    video_class = browser.find_elements_by_css_selector("p[class='am-cf']")

    for video in video_class:
        player_over = video.find_elements_by_tag_name('img')
        if len(player_over) == 1:
            player_over_list.append(video.find_element_by_tag_name('a').get_attribute('title'))
        else:
            video_div_list.append(video.find_element_by_tag_name('a').get_attribute('href'))
    return video_div_list


def player_video(href):
    js = "window.location.href='%s'" % href
    browser.execute_script(js)
    time.sleep(5)
    browser.find_element_by_class_name('pv-icon-btn-play').click()
    v_time = browser.find_element_by_class_name('pv-time-duration').text
    logging.info('视频时长: %s', v_time)
    return v_time


def time_format(v_time):
    times = v_time.split(':')
    if len(times) == 3:
        return int(times[0]) * 3600 + int(times[1]) * 60 + int(times[2]) + 10
    return int(times[0]) * 60 + int(times[1]) + 10


if __name__ == "__main__":
    username = ''
    password = ''

    login()
    course_jump()
    video_list = course_video()
    logging.info("已观看视频: %s", json.dumps(player_over_list))
    logging.info("未观看视频: %s", json.dumps(video_list))
    for video_url in video_list:
        if video_url.find('javascript') > -1:
            continue
        video_time = player_video(video_url)
        logging.info('视频地址:%s , 视频时长:%s' % (video_url, video_time))
        time.sleep(time_format(video_time))

    browser.close()
    browser.__exit__()

    # 3.刷新浏览器
    # browser.refresh()
