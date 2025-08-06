import requests
# 698a9966ca734932517e108636330708
# Scrapestack API 密钥
API_KEY = '698a9966ca734932517e108636330708'
url = 'https://www.yicai.com/'

# Scrapestack 请求头
params = {
    'access_key': API_KEY,
    'url': url
}

# 发送请求获取页面内容
response = requests.get('http://api.scrapestack.com/scrape', params=params)

# 打印网页内容
if response.status_code == 200:
    print(response.text)  # 输出网页的HTML内容
else:
    print('请求失败:', response.status_code)
