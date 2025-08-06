from exceptiongroup import catch
from playwright.sync_api import sync_playwright
import time
import os

# 浏览器状态保存路径（登录后会保存到这里）
STATE_PATH = "xhs_state.json"


def login_and_save_state():
    """首次运行，人工扫码登录并保存登录状态"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("请手动扫码登录小红书")
        page.goto("https://www.xiaohongshu.com")

        # input("✅ 登录完成后按回车继续...")
        time.sleep(30)  # 等待用户扫码登录，30秒后继续

        context.storage_state(path=STATE_PATH)
        print("✅ 登录状态已保存为 state.json")
        browser.close()


def publish_image_note(IMAGE_PATHS, NOTE_TITLE, NOTE_BODY):
    sleep_time = 3
    """自动打开发布页面并发布图文笔记"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        # 打开发布页面
        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
        time.sleep(sleep_time)

        # ✅ 第一步：点击“上传图文”标签页
        print("🧭 切换到图文发布区域")
        tab_locator = page.locator('//span[text()="上传图文"]/ancestor::div[contains(@class, "creator-tab")]').nth(1)
        tab_locator.scroll_into_view_if_needed()
        tab_locator.click()
        print("✅ 切换完成")
        time.sleep(sleep_time)

        # ✅ 第二步：上传图片（支持多图）
        print("📸 上传图片")
        upload_button_selector = 'input[type="file"]'
        page.set_input_files(upload_button_selector, IMAGE_PATHS)
        time.sleep(sleep_time)  # 视图上传速度可调节

        # ✅ 第三步：填写标题
        print("✍️ 填写标题")
        title_input = page.locator('input[class="d-text"][type="text"]')
        title_input.wait_for(timeout=10000)
        title_input.fill(NOTE_TITLE)
        time.sleep(sleep_time)

        # ✅ 第四步：填写正文内容
        print("📝 填写正文")
        body_selector = 'div[contenteditable="true"]'
        page.fill(body_selector, NOTE_BODY)
        time.sleep(sleep_time)

        # ✅ 第五步：点击发布按钮
        print("🚀 发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(sleep_time)

        print("✅ 发布成功")
        time.sleep(sleep_time)
        browser.close()


def publish_vedio_note(VEDIO_PATH, NOTE_TITLE, NOTE_BODY):
    sleep_time = 3
    """自动打开发布页面并发布图文笔记"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        # 打开发布页面
        page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
        time.sleep(sleep_time)

        print("📸 上传视频")
        upload_button_selector = 'input[type="file"]'
        page.set_input_files(upload_button_selector, VEDIO_PATH)
        time.sleep(sleep_time)  # 视图上传速度可调节

        # ✅ 填写标题
        print("✍️ 填写标题")
        # title_input = page.locator('//input[@placeholder="填写标题会有更多赞哦～"]')
        title_input = page.locator('input[class="d-text"][type="text"]')
        title_input.wait_for(timeout=10000)
        title_input.fill(NOTE_TITLE)
        time.sleep(sleep_time)

        # ✅ 填写正文内容
        print("📝 填写正文")
        body_selector = 'div[contenteditable="true"]'
        page.fill(body_selector, NOTE_BODY)
        time.sleep(sleep_time)

        # ✅ 点击发布按钮
        print("🚀 发布笔记")
        publish_button_selector = 'button:has-text("发布")'
        page.click(publish_button_selector)
        time.sleep(sleep_time)

        print("✅ 发布成功")
        time.sleep(sleep_time)
        browser.close()


def main(type, NOTE_TITLE, NOTE_BODY, IMAGE_PATHS, VEDIO_PATH=None):
    type = type
    # 如果没有状态文件，先登录
    if not os.path.exists(STATE_PATH):
        print("未找到登录状态文件，开始登录...")
        login_and_save_state()

    # 尝试发布笔记
    try:
        print("尝试发布笔记...")
        publish_image_note(IMAGE_PATHS, NOTE_TITLE, NOTE_BODY) if type == "image" else publish_vedio_note(VEDIO_PATH, NOTE_TITLE, NOTE_BODY)
    except Exception as e:
        print(f"发布笔记时出错: {e}")
        print("重新登录...")
        # 如果发布出错，重新登录
        login_and_save_state()
        # 重新尝试发布
        print("重新尝试发布笔记...")
        publish_image_note(IMAGE_PATHS, NOTE_TITLE, NOTE_BODY) if type == "image" else publish_vedio_note(VEDIO_PATH, NOTE_TITLE, NOTE_BODY)


if __name__ == "__main__":
    # 你的图片路径
    IMAGE_PATHS = [
        r"C:\Users\EDY\Desktop\resource\images\img1.png",
        r"C:\Users\EDY\Desktop\resource\images\img2.png",
        r"C:\Users\EDY\Desktop\resource\images\img3.jpg",
    ]  # < 18张

    VEDIO_PATH = r"C:\Users\EDY\Desktop\resource\vedios\vedio1.mp4"

    # 标题和正文
    NOTE_TITLE = "标题示例：这是一个自动发布的笔记标题"  # < 20字
    NOTE_BODY = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"  # < 1000字
    main("image",NOTE_TITLE,NOTE_BODY,IMAGE_PATHS,VEDIO_PATH)
