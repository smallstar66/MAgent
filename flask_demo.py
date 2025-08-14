from flask import Flask

# 创建 Flask 应用
app = Flask(__name__)

# 首页路由
@app.route('/')
def home():
    return '欢迎来到 Flask 示例主页！'

# 问候页面，支持动态 URL
@app.route('/hello/<name>')
def hello(name):
    return f'你好，{name}！欢迎使用 Flask。'

# 启动服务器
if __name__ == '__main__':
    app.run(port=5001,debug=True)
