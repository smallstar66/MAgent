import requests
from flask import Flask, request, jsonify
import os
import json
import time
import tempfile
import urllib.request
from playwright.sync_api import sync_playwright
import re

"""
    提供的web api服务:
        login_1,login_2: 登录小红书
        publish_image_note: 发布图文笔记
        publish_video_note: 发布视频笔记
        logout: 登出
"""
app = Flask(__name__)

# path = tempfile.gettempdir()
path = r"D:\test"
phone = None
verification_code = None
file_name = "xhs_cookies.json"
phone_pattern = r'^1[3-9]\d{9}$'


@app.route('/')
def welcome():
    # for i in range(10):
    #     print(i)
    #     time.sleep(1)
    return "Welcome to Xiaohongshu Http Server!"


@app.route('/login_1', methods=['GET'])
def login_phone():
    global phone
    phone = request.args.get('phone', '19330021527')

    try:
        res = login_1(phone)
    except Exception as e:
        print(e)
        return jsonify({"msg": f"服务器端出现错误，登录失败！{e}"})
    return jsonify({"msg": res})


@app.route('/login_2', methods=['GET'])
def login_verification_code():
    global phone, verification_code
    verification_code = request.args.get('verification_code', '')

    try:
        res = login_2(phone, verification_code)
    except Exception as e:
        print(e)
        return jsonify({"msg": f"验证码错误 或者 服务器端出现错误，登录失败！请尝试重新输入验证码！ {e}"})
    return jsonify({"msg": res})


@app.route('/publish_image_note', methods=["GET", "POST"])
def _publish_image_note():
    """
        image_urls:image urls
        title: note title
        content: note content
        tags: note tags
    :return: success
    """
    if request.method == 'POST':
        # POST
        data = request.get_json() or {}
        urls = data.get('image_urls', [r"C:\Users\EDY\Desktop\resource\images\img1.png",
                                       r"C:\Users\EDY\Desktop\resource\images\img2.png",
                                       r"C:\Users\EDY\Desktop\resource\images\img3.jpg", ])
        title = data.get('title', '默认标题')
        content = data.get('content', '默认正文内容!')
        tags = data.get('tags', [])
    else:
        # GET
        urls = [
            r"https://ts4.tc.mm.bing.net/th/id/OIP-C.iCTTCiabHLuHxkhMXoiYMQHaNK?rs=1&pid=ImgDetMain&o=7&rm=3",
            r"https://ts3.tc.mm.bing.net/th/id/OIP-C.MPMaJsWePTi45BlSgj8IhQHaO0?rs=1&pid=ImgDetMain&o=7&rm=3",
            r"https://ts1.tc.mm.bing.net/th/id/OIP-C.efoZ1QOnR15IC_R8pDKAGwHaNK?rs=1&pid=ImgDetMain&o=7&rm=3"
        ]
        title = "标题示例：这是一个自动发布的笔记标题"
        content = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"
        tags = ['#我爱学习', '#学习爱我']

    tmp_urls = []
    for url in urls:
        if url != "null" and url is not None and url != "":
            tmp_urls.append(url)
    urls = tmp_urls

    # 下载图片到本地
    urls = download_urls(urls)

    print(f"---------- 标题 ----------\n{title}\n")
    print(f"---------- 正文 ----------\n{content}\n")
    print(urls)

    # 规范性检查
    if len(title) > 20:
        print("标题过长！应≤20字，请重新输入！")
        return jsonify({"msg": "标题过长！应≤20字，请重新输入！"})
    if len(content) + sum(len(tag) for tag in tags) > 950:
        print("正文+标签长度过长！应≤1000字，请重新输入！")
        return jsonify({"msg": "正文+标签长度过长，应≤1000字，请重新输入！"})
    if len(urls) > 18:
        print("图片数量太多！应≤18张，请重新输入！")
        return jsonify({"msg": "图片数量太多！应≤18张，请重新输入！"})

    try:
        res = publish_image_note(title[:20], content[:1000], urls[:18], tags)
    except Exception as e:
        print(e)
        return jsonify({"msg": f"服务器端出现错误，发布失败！{e}"})
    return jsonify({"msg": res})


@app.route('/publish_video_note', methods=["GET", "POST"])
def _publish_video_note():
    """
        video_url:video url 只有一个
        title: note title
        content: note content
        tags: note tags
    :return: success
    """
    if request.method == 'POST':
        # POST
        data = request.get_json() or {}
        urls = data.get('video_url', r"C:\Users\EDY\Desktop\resource\videos\video1.mp4")
        title = data.get('title', '默认标题')
        content = data.get('content', '默认正文内容!')
        tags = data.get('tags', [])
    else:
        # GET
        urls = r"C:\Users\EDY\Desktop\resource\videos\video1.mp4"
        title = "标题示例：这是一个自动发布的笔记标题"
        content = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"
        tags = ['#我爱学习', '#学习爱我']

    if isinstance(urls, str):
        urls = [urls]
    tmp_urls = []
    for url in urls:
        if url != "null" and url is not None and url != "":
            tmp_urls.append(url)
    urls = tmp_urls

    # 下载到本地
    urls = download_urls(urls, if_video=True)

    print(f"---------- 标题 ----------\n{title}\n")
    print(f"---------- 正文 ----------\n{content}\n")
    print(urls)

    # 规范性检查
    if len(title) > 20:
        print("标题过长！应≤20字，请重新输入！")
        return jsonify({"msg": "标题过长！应≤20字，请重新输入！"})
    if len(content) + sum(len(tag) for tag in tags) > 950:
        print("正文+标签长度过长！应≤1000字，请重新输入！")
        return jsonify({"msg": "正文+标签长度过长，应≤1000字，请重新输入！"})

    try:
        res = publish_video_note(title, content, urls[:1], tags)
    except Exception as e:
        print(e)
        return jsonify({"msg": f"服务器端出现错误，发布失败！{e}"})
    return jsonify({"msg": res})


@app.route('/logout', methods=['GET'])
def logout():
    phone_tmp = request.args.get('phone', '19330021527')
    cookies_file = os.path.join(path, f"{phone_tmp}_{file_name}")

    global phone
    if phone_tmp == phone:
        phone = None

    if os.path.exists(cookies_file):
        os.remove(cookies_file)
    print(f"{phone_tmp} cooikes已删除，注销成功。")
    return jsonify({"msg": f"{phone_tmp} cooikes已删除，注销成功。"})


@app.route('/check', methods=['GET'])
def check_phone():
    if phone is None:
        print("当前无登录，请先登录！")
        return jsonify({"msg": "当前无登录，请先登录！"})
    print(f"当前登录为：{phone}！")
    return jsonify({"msg": f"当前登录为：{phone}！"})


def download_url(url, num, if_video=False):
    local_dir = os.path.join(path, "temp")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    # num = len(os.listdir(local_dir))
    file_name = f"img_{num}.png"
    if if_video:
        file_name = f"video_{num}.mp4"

    local_path = os.path.join(local_dir, file_name)  # {path}\temp

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as response:
        with open(local_path, 'wb') as f:
            f.write(response.read())
    print(f"图片已保存到: {local_path}  {url}")

    # with requests.get(url, stream=True) as r:
    #     r.raise_for_status()
    #     with open(local_path, 'wb') as f:
    #         for chunk in r.iter_content(chunk_size=8192):
    #             f.write(chunk)

    return local_path


def download_urls(urls, if_video=False):
    results = []
    num = 0
    for url in urls:
        if os.path.exists(url):
            results.append(url)
            continue
        if url.startswith("http"):
            try:
                tmp_path = download_url(url, num, if_video)
            except:
                continue
            results.append(tmp_path)
            num += 1
    return results


def is_cookie_valid(cookies_file):
    if not os.path.exists(cookies_file):
        print("cookies文件不存在")
        return False
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
    for cookie in cookies:
        if "expires" not in cookie:
            continue
        expires = cookie.get('expires')
        if expires == -1:
            continue
        if expires:
            # 如果 expires 大于当前时间，则认为 Cookie 是有效的
            if expires < time.time():
                print("cookies已过期")
                return False
    return True


def login_1(phone, country_code="+86"):
    """
    使用Playwright登录小红书
    :param phone:
    :param country_code:
    :return:
    """
    if not bool(re.match(phone_pattern, phone)):
        print("手机号错误")
        return "手机号错误"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        cookies_file = os.path.join(path, f"{phone}_{file_name}")

        # 加载cookies
        if is_cookie_valid(cookies_file):
            context = browser.new_context(storage_state=cookies_file)
        else:
            context = browser.new_context()

        page = context.new_page()

        # 加载cookies，访问发布页面
        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(3)

        # 检查是否已经登录
        login_button = page.query_selector('button:has-text(" 登录 ")')
        if not login_button:
            print("使用cookies登录成功")
            context.storage_state(path=cookies_file)
            time.sleep(1)
            return "使用cookies登录成功"
        else:
            print("无效的cookies，继续登录。")

        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(2)

        # 步骤 1: 同意协议
        page.click('div[class="icon-wrapper"]')
        # 步骤 2: 填写手机号
        print("填写手机号")
        try:
            page.fill('input[placeholder="输入手机号"]', phone)
        except:
            try:
                page.fill('input[name="blur"]', phone)
            except Exception as e:
                print("填写手机号失败:", e)
                return "填写手机号失败"
        time.sleep(1)

        # 步骤 3: 点击发送验证码按钮
        print("点击发送验证码按钮")
        page.click('span[class="code-button active"]')  # 点击“发送验证码”按钮，调整选择器以确保其正确
        time.sleep(1)

        print("验证码已发送，请输入验证码。")
        page.close()

    return "验证码已发送，请输入验证码。"


def login_2(phone, verification_code):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        cookies_file = os.path.join(path, f"{phone}_{file_name}")
        # 加载cookies
        if is_cookie_valid(cookies_file):
            context = browser.new_context(storage_state=cookies_file)
        else:
            context = browser.new_context()

        page = context.new_page()

        # 加载cookies，访问发布页面
        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(3)

        # 检查是否已经登录
        login_button = page.query_selector('button:has-text(" 登录 ")')
        if not login_button:
            print("使用cookies登录成功")
            context.storage_state(path=cookies_file)
            time.sleep(1)
            return "使用cookies登录成功"
        else:
            print("无效的cookies，继续登录。")

        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(3)

        # 步骤 1: 同意协议
        page.click('div[class="icon-wrapper"]')
        # 步骤 2: 填写手机号
        print("填写手机号")
        try:
            page.fill('input[placeholder="输入手机号"]', phone)
        except:
            try:
                page.fill('input[name="blur"]', phone)
            except Exception as e:
                print("填写手机号失败:", e)
                return "填写手机号失败"
        time.sleep(1)

        verification_code = str(verification_code)
        # 步骤 4: 填写验证码
        print("填写验证码")
        page.fill('input[placeholder="输入验证码"]', verification_code)  # 填写验证码
        time.sleep(1)

        # 步骤 5: 点击登录按钮
        print("点击登录按钮")
        try:
            page.click('button:has-text(" 登录 ")')  # 点击“登录”按钮，确保选择器正确
        except:
            try:
                page.click('button[class="submit"]')  # 点击“登录”按钮，确保选择器正确
            except Exception as e:
                print("点击登录按钮失败:", e)
                return "点击登录按钮失败"
        time.sleep(3)

        # 保存cookies
        print("保存cookies")
        context.storage_state(path=cookies_file)
        time.sleep(1)

        page.close()
    return "登录成功！"


def publish_image_note(title, content, images, tags):
    # 创作服务平台首页页面: https://creator.xiaohongshu.com/new/home
    # 发布页面: https://creator.xiaohongshu.com/publish/publish?source=official
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        global phone
        cookies_file = os.path.join(path, f"{phone}_{file_name}")
        # 加载cookies
        if is_cookie_valid(cookies_file):
            context = browser.new_context(storage_state=cookies_file)
        else:
            context = browser.new_context()
        page = context.new_page()

        # 加载cookies，访问发布页面
        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(3)

        # 检查是否已经登录
        login_button = page.query_selector('button:has-text(" 登录 ")')
        if not login_button:
            print("使用cookies登录成功")
            context.storage_state(path=cookies_file)
            time.sleep(1)
        else:
            print("发布界面: 登录状态不可用，请前往登录。")
            return "发布界面: 登录状态不可用，请前往登录。"

        page.goto('https://creator.xiaohongshu.com/publish/publish?source=official')
        time.sleep(5)

        # 直接跳转到发布界面，不需要点击跳转
        # print("前往发布")
        # page.click('div[class="btn"]')
        # time.sleep(1)

        # 要是发布视频，则不操作这一步
        # 第一步：切换到图文发布区域
        print("切换到图文发布区域")
        tab_locator = page.locator(
            '//span[text()="上传图文"]/ancestor::div[contains(@class, "creator-tab")]').nth(1)
        tab_locator.scroll_into_view_if_needed()
        tab_locator.click()
        time.sleep(2)

        # 第二步：上传图片（支持多图）
        print("上传图片")
        upload_button_selector = 'input[type="file"]'
        page.set_input_files(upload_button_selector, images)
        time.sleep(2)  # 视图上传速度可调节

        # 第三步：填写标题
        print("填写标题")
        title_input = page.locator('input[class="d-text"][type="text"]')
        title_input.wait_for(timeout=10000)
        title_input.fill(title)
        time.sleep(2)

        # 第四步：填写正文内容
        print("填写正文")
        content_selector = 'div[contenteditable="true"]'
        page.fill(content_selector, content)
        time.sleep(2)

        # 填写标签
        content_input = page.locator(content_selector)
        content_input.focus()
        page.keyboard.press('Control+End')
        content_input.type('\n')
        for tag in tags:
            if not tag.startswith('#'):
                tag = '#' + tag
            content_input.type(tag)
            time.sleep(2)
            page.keyboard.press('Enter')

        # 第五步：点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(2)

        print("图文发布成功")
        time.sleep(2)

    return "图文发布成功！"


def publish_video_note(title, content, video, tags):
    # 创作服务平台首页页面: https://creator.xiaohongshu.com/new/home
    # 发布页面: https://creator.xiaohongshu.com/publish/publish?source=official
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        global phone
        cookies_file = os.path.join(path, f"{phone}_{file_name}")
        # 加载cookies
        if is_cookie_valid(cookies_file):
            context = browser.new_context(storage_state=cookies_file)
        else:
            context = browser.new_context()
        page = context.new_page()

        # 加载cookies，访问发布页面
        page.goto('https://www.xiaohongshu.com/explore')
        time.sleep(3)

        # 检查是否已经登录
        login_button = page.query_selector('button:has-text(" 登录 ")')
        if not login_button:
            print("使用cookies登录成功")
            context.storage_state(path=cookies_file)
            time.sleep(1)
        else:
            print("发布界面: 登录状态不可用，请前往登录。")
            return "发布界面: 登录状态不可用，请前往登录。"

        page.goto('https://creator.xiaohongshu.com/publish/publish?source=official')
        time.sleep(5)

        # 直接跳转到发布界面，不需要点击跳转
        # print("前往发布")
        # page.click('div[class="btn"]')
        # time.sleep(1)

        print("上传视频")
        upload_button_selector = 'input[type="file"]'
        page.set_input_files(upload_button_selector, video)
        time.sleep(10)  # 视图上传速度可调节

        # 填写标题
        print("填写标题")
        # title_input = page.locator('//input[@placeholder="填写标题会有更多赞哦～"]')
        title_input = page.locator('input[class="d-text"][type="text"]')
        title_input.fill(title)
        time.sleep(2)

        # 填写正文内容
        print("填写正文")
        content_selector = 'div[contenteditable="true"]'
        page.fill(content_selector, content)
        time.sleep(2)

        # 填写标签
        content_input = page.locator(content_selector)
        content_input.focus()
        page.keyboard.press('Control+End')
        content_input.type('\n')
        for tag in tags:
            if not tag.startswith('#'):
                tag = '#' + tag
            content_input.type(tag)
            time.sleep(2)
            page.keyboard.press('Enter')

        # 点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(2)

        print("视频发布成功")
        time.sleep(2)

    return "视频发布成功！"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
