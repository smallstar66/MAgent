import requests
from flask import Flask, request
import os
import concurrent.futures
import threading
from playwright.sync_api import sync_playwright
from xhsPoster import XiaohongshuPoster

"""
    提供的web api服务:
        login_1,login_2: 登录小红书
        publish_image_note: 发布图文笔记
        publish_video_note: 发布视频笔记
"""
app = Flask(__name__)

# 全局poster
# poster = XiaohongshuPoster(r"D:\test")
path = r"D:\test"
phone = None
verification_code = None

@app.route('/')
def welcome():
    return "Welcome to Xiaohongshu Http Server!"


def task1(phone):
    poster = XiaohongshuPoster(path)
    res = poster.login_1(phone)
    return res

@app.route('/login_1', methods=['GET'])
def login_phone():
    # 获取Query参数
    global phone
    phone = request.args.get('phone', '19330021527')
    thread = threading.Thread(target=task1,args=(phone,))
    thread.start()
    return "res"


def task2(verification_code):
    poster = XiaohongshuPoster(path)
    res = poster.login_2(phone,verification_code)
    return res

@app.route('/login_2', methods=['GET'])
def login_verification_code():
    global verification_code
    verification_code = request.args.get('verification_code', '')
    thread = threading.Thread(target=task2, args=(verification_code,))
    thread.start()
    return "res"


@app.route('/publish_image_note', methods=["GET", "POST"])
def publish_image_note():
    """
        urls:image urls
        title: note title
        content: note content
    :return: success
    """
    if request.method == 'POST':
        # POST
        data = request.get_json() or {}
        urls = data.get('urls', [r"C:\Users\EDY\Desktop\resource\images\img1.png",
                                 r"C:\Users\EDY\Desktop\resource\images\img2.png",
                                 r"C:\Users\EDY\Desktop\resource\images\img3.jpg", ])
        title = data.get('title', '默认标题')
        content = data.get('content', '默认正文内容!')
    else:
        # GET
        urls = [
            r"https://ts4.tc.mm.bing.net/th/id/OIP-C.iCTTCiabHLuHxkhMXoiYMQHaNK?rs=1&pid=ImgDetMain&o=7&rm=3",
            r"https://ts3.tc.mm.bing.net/th/id/OIP-C.MPMaJsWePTi45BlSgj8IhQHaO0?rs=1&pid=ImgDetMain&o=7&rm=3",
            r"https://ts1.tc.mm.bing.net/th/id/OIP-C.efoZ1QOnR15IC_R8pDKAGwHaNK?rs=1&pid=ImgDetMain&o=7&rm=3"
        ]
        title = "标题示例：这是一个自动发布的笔记标题"
        content = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"

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

    res = poster.publish_image_note(title, content, urls[:18])
    return res


@app.route('/publish_video_note', methods=["GET", "POST"])
def publish_video_note():
    """
        urls:vedio urls 只有一个
        title: note title
        content: note content
    :return: success
    """
    if request.method == 'POST':
        # POST
        data = request.get_json() or {}
        urls = data.get('urls', [r"C:\Users\EDY\Desktop\resource\vedios\vedio1.mp4"])
        title = data.get('title', '默认标题')
        content = data.get('content', '默认正文内容!')
    else:
        # GET
        urls = [r"C:\Users\EDY\Desktop\resource\vedios\vedio1.mp4"]
        title = "标题示例：这是一个自动发布的笔记标题"
        content = "正文示例：这是一个自动发布的笔记正文内容。可以包含多行文本，甚至是一些格式化内容。"

    tmp_urls = []
    for url in urls:
        if url != "null" and url is not None and url != "":
            tmp_urls.append(url)
    urls = tmp_urls

    # 下载图片到本地
    urls = download_urls(urls, if_vedio=True)

    print(f"---------- 标题 ----------\n{title}\n")
    print(f"---------- 正文 ----------\n{content}\n")
    print(urls)

    res = poster.publish_vedio_note(title, content, urls[:1])
    return res

def download_url(url, if_vedio=False):
    local_dir = os.path.join(path, "temp")
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    num = len(os.listdir(local_dir))
    file_name = f"img_{num}.png"
    if if_vedio:
        file_name = f"video_{num}.mp4"

    local_path = os.path.join(local_dir, file_name)  # {path}\temp
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path


def download_urls(urls, if_vedio=False):
    results = []
    for url in urls:
        if os.path.exists(url):
            results.append(url)
            continue
        if url.startswith("http"):
            results.append(download_url(url, if_vedio))
    return results

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
