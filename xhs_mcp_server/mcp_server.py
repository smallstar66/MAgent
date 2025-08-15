from fastmcp import FastMCP
import requests
import os
import json
import tempfile
import time
from playwright.sync_api import sync_playwright

"""
    提供的mcp服务:
        login_1,login_2: 登录小红书
        publish_image_note: 发布图文笔记
        publish_video_note: 发布视频笔记
"""

mcp = FastMCP("xhs_auto_server")

# path = tempfile.gettempdir()
path = r"D:\test"
cookies_file = os.path.join(path, "xhs_cookies.json")


@mcp.tool()
def login_phone(phone: str) -> str:
    """
        登录的第一步，先输入手机号，获取验证码。
    :param phone: 手机号，11位
    :return: 返回执行结果，成功则返回"验证码已发送，请输入验证码。"，失败则返回错误信息。
    """
    try:
        res = login_1(phone)
    except Exception as e:
        print(e)
        return f"服务器端出现错误，登录失败！{e}"
    return res


@mcp.tool()
def login_verification_code(phone: str, verification_code: int):
    """
        登录的第二步，输入验证码，完成登录。
    :param phone: 手机号，11位
    :param verification_code: 验证码
    :return: 返回执行结果，成功则返回"登录成功！"，失败则返回错误信息。
    """
    try:
        res = login_2(phone, verification_code)
    except Exception as e:
        print(e)
        return f"服务器端出现错误，登录失败！{e}"
    return res


@mcp.tool()
def _publish_image_note(title: str, content: str, images: list):
    """
        自动发布图文笔记，支持多图发布。
    :param title: 标题
    :param content: 正文
    :param images: image urls，图片链接数组
    :return: 返回执行结果，失败则返回错误信息。
    """

    tmp_urls = []
    for url in images:
        if url != "null" and url is not None and url != "":
            tmp_urls.append(url)
    urls = tmp_urls

    # 下载图片到本地
    urls = download_urls(urls)

    print(f"---------- 标题 ----------\n{title}\n")
    print(f"---------- 正文 ----------\n{content}\n")
    print(urls)

    try:
        res = publish_image_note(title, content, urls[:18])
    except Exception as e:
        print(e)
        return f"服务器端出现错误，发布失败！{e}"
    return res


@mcp.tool()
def _publish_video_note(title: str, content: str, video: list | str):
    """
        自动发布视频笔记，仅支持单个视频发布。
    :param title: 标题
    :param content: 正文
    :param video: 一个视频链接，可以是str也可以是list
    :return: 返回执行结果，失败则返回错误信息。
    """
    if isinstance(video, str):
        video = [video]
    tmp_urls = []
    for url in video:
        if url != "null" and url is not None and url != "":
            tmp_urls.append(url)
    urls = tmp_urls

    # 下载图片到本地
    urls = download_urls(urls, if_video=True)

    print(f"---------- 标题 ----------\n{title}\n")
    print(f"---------- 正文 ----------\n{content}\n")
    print(urls)
    try:
        res = publish_video_note(title, content, urls[:1])
    except Exception as e:
        print(e)
        return f"服务器端出现错误，发布失败！{e}"
    return res


def download_url(url, if_video=False):
    local_dir = os.path.join(path, "temp")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    num = len(os.listdir(local_dir))
    file_name = f"img_{num}.png"
    if if_video:
        file_name = f"video_{num}.mp4"

    local_path = os.path.join(local_dir, file_name)  # {path}\temp
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path


def download_urls(urls, if_video=False):
    results = []
    for url in urls:
        if os.path.exists(url):
            results.append(url)
            continue
        if url.startswith("http"):
            results.append(download_url(url, if_video))
    return results


def is_cookie_valid():
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        # 加载cookies
        if is_cookie_valid():
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
        context = browser.new_context()
        page = context.new_page()
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


def publish_image_note(title, content, images):
    # 创作服务平台首页页面: https://creator.xiaohongshu.com/new/home
    # 发布页面: https://creator.xiaohongshu.com/publish/publish?source=official
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # 加载cookies
        if is_cookie_valid():
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
        time.sleep(2)

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
        body_selector = 'div[contenteditable="true"]'
        page.fill(body_selector, content)
        time.sleep(2)

        # 第五步：点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(2)

        print("图文发布成功")
        time.sleep(2)

    return "图文发布成功！"


def publish_video_note(title, content, video):
    # 创作服务平台首页页面: https://creator.xiaohongshu.com/new/home
    # 发布页面: https://creator.xiaohongshu.com/publish/publish?source=official
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # 加载cookies
        if is_cookie_valid():
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
        time.sleep(2)

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
        body_selector = 'div[contenteditable="true"]'
        page.fill(body_selector, content)
        time.sleep(2)

        # 点击发布按钮
        print("发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(2)

        print("视频发布成功")
        time.sleep(2)

    return "视频发布成功！"


def main():
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
