from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time
import os
import threading
import urllib.request
from urllib.parse import urlparse

app = Flask(__name__)

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
        print(f"✅ 登录状态已保存为 {STATE_PATH}")
        browser.close()


def publish_image_note(NOTE_TITLE, NOTE_BODY, IMAGE_PATHS):
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


def publish_vedio_note(NOTE_TITLE, NOTE_BODY, VEDIO_PATH):
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


def background_publish_task(IMAGE_PATHS, VEDIO_PATH, NOTE_TITLE, NOTE_BODY, type):
    # 如果没有状态文件，先登录
    # if not os.path.exists(STATE_PATH):
    #     print(f"未找到登录状态文件{STATE_PATH}，开始登录...")
    #     login_and_save_state()
    login_and_save_state()

    # 尝试发布笔记
    try:
        print("尝试发布笔记...")
        if type == "image":
            publish_image_note(NOTE_TITLE, NOTE_BODY, IMAGE_PATHS)
        else:
            publish_vedio_note(NOTE_TITLE, NOTE_BODY, VEDIO_PATH)
    except Exception as e:
        print(f"发布笔记时出错: {e}")
        print("重新登录...")
        # 如果发布出错，重新登录
        login_and_save_state()
        # 重新尝试发布
        print("重新尝试发布笔记...")
        if type == "image":
            publish_image_note(NOTE_TITLE, NOTE_BODY, IMAGE_PATHS)
        else:
            publish_vedio_note(NOTE_TITLE, NOTE_BODY, VEDIO_PATH)


@app.route("/xhs", methods=["GET", "POST"])
def xhs():
    type = request.args.get('type', 'image')  # 默认为图文发布
    # 从请求中获取参数
    if request.method == "POST":
        data = request.get_json() or {}
        img_urls = data.get("img_urls", [
            r"C:\Users\EDY\Desktop\resource\images\img1.png",
            r"C:\Users\EDY\Desktop\resource\images\img2.png",
            r"C:\Users\EDY\Desktop\resource\images\img3.jpg",
        ])
        vedio_url = data.get("vedio_url", r"C:\Users\EDY\Desktop\resource\vedios\vedio1.mp4")
        note_title = data.get("title", "默认标题")
        note_body = data.get("content", "默认正文内容!")
    else:
        # GET 请求使用默认参数
        img_urls = [
            r"https://ts1.tc.mm.bing.net/th/id/R-C.d2b3a4779fd2b9af70103d485bc8b664?rik=Xm7zutXMpsp91Q&riu=http%3a%2f%2fup.deskcity.org%2fpic_source%2fd2%2fb3%2fa4%2fd2b3a4779fd2b9af70103d485bc8b664.jpg&ehk=%2fh%2fipXq8Ihn81SbQdkphnzweLFLUGfD1%2fXncDcbLgRE%3d&risl=&pid=ImgRaw&r=0",
            r"https://img.keaitupian.cn/newupload/09/1664359738368206.jpg",
            r"https://ts3.tc.mm.bing.net/th/id/OIP-C.4DlDdKpUt9zOKljHCRjBrgHaE7?rs=1&pid=ImgDetMain&o=7&rm=3"
        ]
        vedio_url = r"D:\Edge Download/苹果.mp4"
        # vedio_url = r"https://vdept3.bdstatic.com/mda-rcndwh4f64gvajvq/360p/h264/1742723320392353802/mda-rcndwh4f64gvajvq.mp4?v_from_s=hkapp-haokan-nanjing&auth_key=1754042533-0-0-ced244c6ef8982d9d178ec3852458ecd&bcevod_channel=searchbox_feed&cr=0&cd=0&pd=1&pt=3&logid=0133589208&vid=4069115534709571708&klogid=0133589208&abtest="
        note_title = "标题示例：这是一个自动发布的笔记标题"
        note_body = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"

    # 清理 img_urls 列表，去除无效链接
    urls = []
    for url in img_urls:
        if url != "null" and url != None and url != "":
            urls.append(url)
    img_urls = urls

    print(f"标题：\n{note_title}\n")
    print(f"正文：\n{note_body}\n")

    # ---------------- 下载网页链接 ---------------- #
    os.makedirs('temp', exist_ok=True)
    # images
    num = 0
    img_base_name = "tmp"
    for i in range(len(img_urls)):
        if os.path.exists(img_urls[i]):
            continue
        if i == "null" or i ==None:
            continue
        filename = f"{img_base_name}_{num}.jpg"
        num += 1
        file_path = os.path.join('temp', filename)
        req = urllib.request.Request(img_urls[i])
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(file_path, 'wb') as f:
                f.write(response.read())
        f_path = os.path.join(os.getcwd(), file_path)
        print(f"图片已保存到: {f_path}")
        img_urls[i] = f_path
    # vedio
    if vedio_url is not None and not os.path.exists(vedio_url):
        filename = "vedio.mp4"
        file_path = os.path.join('temp', filename)
        req = urllib.request.Request(vedio_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(file_path, 'wb') as f:
                f.write(response.read())
        f_path = os.path.join(os.getcwd(), file_path)
        print(f"视频已保存到: {f_path}")
        vedio_url = f_path

    # 在后台执行任务
    thread = threading.Thread(target=background_publish_task,
                              args=(img_urls, vedio_url, note_title, note_body, type))
    thread.start()

    return jsonify({
        "msg": "success"
    })


@app.route("/hello", methods=["GET"])
def hello():
    return "hello world"


@app.route('/')
def welcome():
    return "my_service is running!"


if __name__ == "__main__":
    # 本地调试用，监听 0.0.0.0:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
