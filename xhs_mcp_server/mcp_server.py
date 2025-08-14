import concurrent
import os
import tempfile
import time
import requests

# from mcp.server import FastMCP
# from mcp.types import TextContent
from fastmcp import FastMCP

from xhsPoster import XiaohongshuPoster

mcp = FastMCP("xhs")
phone = os.getenv("phone", "19330021527")
path = os.getenv("json_path", r"D:/test")
slow_mode = os.getenv("slow_mode", "False").lower() == "true"


def login():
    poster = XiaohongshuPoster(path)
    poster.login(phone)
    time.sleep(1)
    poster.close()


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


def download_urls(urls):
    """
    并行下载图片到本地缓存地址
    """
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     results = list(executor.map(download_url, urls))

    results = []
    for url in urls:
        results.append(download_url(url))
    return results


@mcp.tool()
def create_note(title: str, content: str, images: list):
    """Create a note (post) to xiaohongshu (rednote) with title, description, and images

    Args:
        title: the title of the note (post), which should not exceed 20 words
        content: the description of the note (post).
        images: the list of image paths or URLs to be included in the note (post)
    """
    poster = XiaohongshuPoster(path)
    poster.login(phone)
    res = ""
    try:
        if len(images) > 0 and images[0].startswith("http"):
            # 使用并行下载图片
            local_images = download_urls(images)
        else:
            local_images = images
        code, info = poster.login_to_publish(title, content, local_images, slow_mode)
        poster.close()
        res = info
    except Exception as e:
        res = "error:" + str(e)

    return res


@mcp.tool()
def create_video_note(title: str, content: str, videos: list):
    """Create a note (post) to xiaohongshu (rednote) with title, description, and videos

    Args:
        title: the title of the note (post), which should not exceed 20 words
        content: the description of the note (post).
        videos: the list of video paths or URLs to be included in the note (post)
    """
    poster = XiaohongshuPoster(path)
    poster.login(phone)
    res = ""
    try:
        # 使用并行下载视频
        if len(videos) > 0 and videos[0].startswith("http"):
            # 使用并行下载图片
            local_videos = download_urls(videos)
        else:
            local_videos = videos

        # local_videos = download_urls(videos)

        code, info = poster.login_to_publish_video(title, content, local_videos, slow_mode)
        poster.close()
        res = info
    except Exception as e:
        res = "error:" + str(e)

    return res


def main():
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()


