from playwright.sync_api import sync_playwright
import tempfile
import time
import json
import os

'''
    base_dir:存储cookie、图片、视频   
    temp文件夹:tempfile.gettempdir()
    当前工作文件夹:os.path.dirname(os.path.abspath(__file__))
'''


class XiaohongshuPoster:
    def __init__(self, path=tempfile.gettempdir()):
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)
        self.current_page = self.browser.new_page()
        self.base_dir = path
        self.login_status = False
        self.cookies_file = os.path.join(path, "xhs_cookies.json")
        self._load_cookies()

    def is_cookie_valid(self):
        if not os.path.exists(self.cookies_file):
            print("cookies文件不存在")
            return False
        with open(self.cookies_file, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            expires = cookie.get('expires')
            if expires:
                # 如果 expires 大于当前时间，则认为 Cookie 是有效的
                if expires < time.time():
                    print("cookies已过期")
                    return False
        return True

    def _load_cookies(self):
        """从文件加载cookies"""
        if self.is_cookie_valid():
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                self.browser.contexts[0].add_cookies(cookies)
            except Exception as e:
                print(e)

    def _save_cookies(self):
        """保存cookies到文件"""
        cookies = self.browser.contexts[0].cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

    def login(self, phone, country_code="+86"):
        """
        使用Playwright登录小红书
        :param phone:
        :param country_code:
        :return:
        """

        # 访问登录页面
        self._load_cookies()
        self.current_page.goto('https://creator.xiaohongshu.com/login')
        self.current_page.reload()
        time.sleep(3)
        # 检查是否已经登录
        if self.current_page.url != 'https://creator.xiaohongshu.com/login':
            print("使用cookies登录成功")
            self._save_cookies()
            time.sleep(1)
            self.login_status = True
            return "使用cookies登录成功"
        else:
            # 清理无效的cookies
            self.current_page.context.clear_cookies()
            print("无效的cookies，已清理，继续登录。")

        self.current_page.goto('https://creator.xiaohongshu.com/login')

        # 步骤 1: 设置号码区号 +86
        # print("设置号码区号 +86")
        # code_input = self.current_page.locator('input[placeholder="请选择选项"]')
        # code_input.clear()
        # code_input.fill(country_code)
        # time.sleep(60)

        # 步骤 2: 填写手机号
        print("填写手机号")
        try:
            self.current_page.fill('input[placeholder="手机号"]', phone)
        except:
            try:
                self.current_page.fill('input[class="css-19z0sa3 css-nt440g dyn"]', phone)
            except Exception as e:
                print("填写手机号失败:", e)
        time.sleep(1)

        # 步骤 3: 点击发送验证码按钮
        print("点击发送验证码按钮")
        self.current_page.click('div[class="css-uyobdj"]')  # 点击“发送验证码”按钮，调整选择器以确保其正确
        time.sleep(1)

        verification_code = input("请输入验证码: ")
        verification_code = str(verification_code)
        # 步骤 4: 填写验证码
        print("填写验证码")
        self.current_page.wait_for_selector('input[placeholder="验证码"]')  # 等待验证码输入框加载
        self.current_page.fill('input[placeholder="验证码"]', verification_code)  # 填写验证码
        time.sleep(1)

        # 步骤 5: 点击登录按钮
        print("点击登录按钮")
        try:
            self.current_page.click('button:has-text(" 登 录 ")')  # 点击“登录”按钮，确保选择器正确
        except:
            try:
                self.current_page.click('span[class="btn-content"]')  # 点击“登录”按钮，确保选择器正确
            except Exception as e:
                print("点击登录按钮失败:", e)
        time.sleep(3)

        # 保存cookies
        print("保存cookies")
        self._save_cookies()
        time.sleep(1)

        self.login_status = True
        return "登录成功。"

    def login_1(self, phone, country_code="+86"):
        """
        使用Playwright登录小红书
        :param phone:
        :param country_code:
        :return:
        """

        # 访问登录页面
        self._load_cookies()
        self.current_page.goto('https://creator.xiaohongshu.com/login')
        self.current_page.reload()
        time.sleep(3)
        # 检查是否已经登录
        if self.current_page.url != 'https://creator.xiaohongshu.com/login':
            print("使用cookies登录成功")
            self._save_cookies()
            time.sleep(1)
            self.login_status = True
            return "使用cookies登录成功"
        else:
            # 清理无效的cookies
            self.current_page.context.clear_cookies()
            print("无效的cookies，已清理，继续登录。")

        self.current_page.goto('https://creator.xiaohongshu.com/login')

        # 步骤 1: 设置号码区号 +86
        # print("设置号码区号 +86")
        # code_input = self.current_page.locator('input[placeholder="请选择选项"]')
        # code_input.clear()
        # code_input.fill(country_code)
        # time.sleep(60)

        # 步骤 2: 填写手机号
        print("填写手机号")
        try:
            self.current_page.fill('input[placeholder="手机号"]', phone)
        except:
            try:
                self.current_page.fill('input[class="css-19z0sa3 css-nt440g dyn"]', phone)
            except Exception as e:
                print("填写手机号失败:", e)
                return "填写手机号失败"
        time.sleep(1)

        # 步骤 3: 点击发送验证码按钮
        print("点击发送验证码按钮")
        # 等待发送验证码按钮加载
        self.current_page.wait_for_selector('div[class="css-uyobdj"]')
        self.current_page.click('div[class="css-uyobdj"]')  # 点击“发送验证码”按钮，调整选择器以确保其正确
        time.sleep(1)
        print("验证码已发送，请输入验证码。")
        return "验证码已发送，请输入验证码。"

    def login_2(self, phone, verification_code):
        if self.login_status:
            return "已登录成功"

        # 访问登录页面
        self.current_page.goto('https://creator.xiaohongshu.com/login')
        time.sleep(1)
        # 检查是否已经登录
        if self.current_page.url != 'https://creator.xiaohongshu.com/login':
            print("使用cookies登录成功")
            self._save_cookies()
            time.sleep(1)
            self.login_status = True
            return "使用cookies登录成功"
        else:
            # 清理无效的cookies
            self.current_page.context.clear_cookies()
            print("无效的cookies，已清理，继续登录。")

        self.current_page.goto('https://creator.xiaohongshu.com/login')

        # 步骤 2: 填写手机号
        print("填写手机号")
        try:
            self.current_page.fill('input[placeholder="手机号"]', phone)
        except:
            try:
                self.current_page.fill('input[class="css-19z0sa3 css-nt440g dyn"]', phone)
            except Exception as e:
                print("填写手机号失败:", e)
                return "填写手机号失败"
        time.sleep(1)

        verification_code = str(verification_code)
        # 步骤 4: 填写验证码
        print("填写验证码")
        self.current_page.wait_for_selector('input[placeholder="验证码"]')  # 等待验证码输入框加载
        self.current_page.fill('input[placeholder="验证码"]', verification_code)  # 填写验证码
        time.sleep(1)

        # 步骤 5: 点击登录按钮
        print("点击登录按钮")
        try:
            self.current_page.click('button:has-text(" 登 录 ")')  # 点击“登录”按钮，确保选择器正确
        except:
            try:
                self.current_page.click('span[class="btn-content"]')  # 点击“登录”按钮，确保选择器正确
            except Exception as e:
                print("点击登录按钮失败:", e)
                return "点击登录按钮失败"
        time.sleep(3)

        # 保存cookies
        print("保存cookies")
        self._save_cookies()
        time.sleep(1)

        self.login_status = True
        return "登录成功！"

    def close(self):
        """关闭浏览器"""
        self.browser.close()
        self.p.stop()

    def publish_image_note(self, title, content, images):
        self._load_cookies()
        self.current_page.goto('https://creator.xiaohongshu.com/new/home')
        self.current_page.reload()
        time.sleep(2)

        if self.current_page.url != 'https://creator.xiaohongshu.com/new/home':
            print("登录状态不可用，请重新登录。")
            self.current_page.context.clear_cookies()
            return "登录状态不可用，请重新登录。"
        else:
            self._save_cookies()
            time.sleep(1)
            self.login_status = True
            print("使用cookies登录成功")

        print("前往发布")
        self.current_page.click('div[class="btn"]')

        # 要是发布视频，则不操作这一步
        # 第一步：切换到图文发布区域
        print("切换到图文发布区域")
        tab_locator = self.current_page.locator(
            '//span[text()="上传图文"]/ancestor::div[contains(@class, "creator-tab")]').nth(1)
        tab_locator.scroll_into_view_if_needed()
        tab_locator.click()
        time.sleep(2)

        # 第二步：上传图片（支持多图）
        print("上传图片")
        upload_button_selector = 'input[type="file"]'
        self.current_page.set_input_files(upload_button_selector, images)
        time.sleep(2)  # 视图上传速度可调节

        # 第三步：填写标题
        print("填写标题")
        title_input = self.current_page.locator('input[class="d-text"][type="text"]')
        title_input.wait_for(timeout=10000)
        title_input.fill(title)
        time.sleep(2)

        # 第四步：填写正文内容
        print("填写正文")
        body_selector = 'div[contenteditable="true"]'
        self.current_page.fill(body_selector, content)
        time.sleep(2)

        # 第五步：点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        self.current_page.click(publish_button_selector)
        time.sleep(2)

        print("图文发布成功")
        time.sleep(2)

        return "图文发布成功！"

    def publish_vedio_note(self, title, content, vedio):
        self._load_cookies()
        self.current_page.goto('https://creator.xiaohongshu.com/new/home')
        self.current_page.reload()
        time.sleep(2)

        if self.current_page.url != 'https://creator.xiaohongshu.com/new/home':
            print("登录状态不可用，请重新登录。")
            self.current_page.context.clear_cookies()
            return "登录状态不可用，请重新登录。"
        else:
            self._save_cookies()
            time.sleep(1)
            self.login_status = True
            print("使用cookies登录成功")

        print("前往发布")
        self.current_page.click('div[class="btn"]')

        print("上传视频")
        upload_button_selector = 'input[type="file"]'
        self.current_page.set_input_files(upload_button_selector, vedio)
        time.sleep(10)  # 视图上传速度可调节

        # 填写标题
        print("填写标题")
        # title_input = page.locator('//input[@placeholder="填写标题会有更多赞哦～"]')
        title_input = self.current_page.locator('input[class="d-text"][type="text"]')
        title_input.fill(title)
        time.sleep(2)

        # 填写正文内容
        print("填写正文")
        body_selector = 'div[contenteditable="true"]'
        self.current_page.fill(body_selector, content)
        time.sleep(2)

        # 点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        self.current_page.click(publish_button_selector)
        time.sleep(2)

        print("视频发布成功")
        time.sleep(2)

        return "视频发布成功！"
