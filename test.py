# import xiaohongshu_mcp
# import xiaohongshu_tools
from exceptiongroup import catch
from playwright.sync_api import sync_playwright
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

def func1():
    from xhs_mcp_server.xhsPoster import XiaohongshuPoster
    poster = XiaohongshuPoster(r"D:\test")
    poster.login_1("19330021527")

def func2():
    with sync_playwright() as p:
        country_code = "+1 "
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://creator.xiaohongshu.com/login')
        print("设置号码区号 +86")
        page.click('input[placeholder="请选择选项"]')
        time.sleep(1)
        page.click(f'div:has-text("{country_code}")')
        # code_input = page.locator('input[placeholder="请选择选项"]')
        # code_input.click()
        # print("清空")
        # code_input.clear()
        print("填写")
        # code_input.fill(country_code)
        print("填写完成")
        time.sleep(60)



if __name__ == '__main__':
    # func1()
    func2()