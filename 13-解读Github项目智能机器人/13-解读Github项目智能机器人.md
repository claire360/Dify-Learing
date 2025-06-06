# 13-解读Github项目智能机器人

[BannyLon/DifyAIA: 基于Dify自主创建的AI应用DSL工作流，你可以免费获取，无论是出于个人需求还是学习目的，它都能为您开启一段充满无限可能的智能之旅。](https://github.com/BannyLon/DifyAIA/tree/main)

## 13.1 任务定义

这是一个解读Github项目的工作流，用户输入一个github项目的url，通过HTTP请求获取GitHub项目的README文件，并将README文件转换为纯文本，然后HTTP请求获取GitHub项目的README文件的完整结构，利用大语言模型对GitHub项目进行归纳总结，最后输出。这个工作流帮助用户快速了解Github项目。

## 13.2 整体流程图

![image-20250504161823876](C:\Users\Claire\AppData\Roaming\Typora\typora-user-images\image-20250504161823876.png)

## 13.3 代码

【05-Gitub.py】

```
import requests
import base64  # 添加这一行
import re
import urllib.parse
from flask import Flask, request, jsonify

app = Flask(__name__)

# 设置 GitHub API 的默认超时时间为 10 秒
requests.DEFAULT_REQUESTS_TIMEOUT = 60

def decode_content(content):
    decoded_bytes = base64.b64decode(content)
    return decoded_bytes.decode("utf-8")

# 定义路由和函数
@app.route('/get_readme', methods=['GET'])
def get_readme():
    print(f'开始')
    # 获取并解码 URL 参数
    github_url = request.args.get('url')
    print(f'github_url的地址：{github_url}')

    # 如果没有提供 GitHub URL，则返回错误信息
    if not github_url:
        print(f'没有')
        return jsonify({"error": "No GitHub URL provided"}), 400

    # 解码 URL 参数
    print(f'开始解析')
    github_url = urllib.parse.unquote(github_url)
    print(f'github_url的地址：{github_url}')

    # 使用正则表达式提取有效的 GitHub URL
    match = re.search(r'https://github\.com/([^/]+)/([^/]+).git', github_url)
    if not match:
        print(f'不符合')
        return jsonify({"error": "Invalid GitHub URL format"}), 400

    
    owner = match.group(1)
    repo = match.group(2)
    print(f'owner:{owner}')
    print(f'repo:{repo}')


    # GitHub API endpoint 用于获取 README
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    print(f'api_url:{api_url}')

    try:
        response = requests.get(api_url, timeout=requests.DEFAULT_REQUESTS_TIMEOUT)
        response.raise_for_status()  # 对于非2xx状态码抛出异常

        print(f'开始检查检查 GitHub API 的速率限制头')

        # 检查 GitHub API 的速率限制头
        rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining"))
        if rate_limit_remaining <= 0:
            return jsonify({"error": "Rate limit exceeded"}), 429

        data = response.json()

        print(f'data:{data}')

        # 检查 content 字段是否存在
        if 'content' in data and data['content']:
            readme_content = base64.b64decode(data['content']).decode('utf-8')
            print(f'readme_content:{readme_content}')
            return jsonify({"readme": readme_content})
        else:
            return jsonify({"error": "README file not found or empty"}), 404

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_structure', methods=['GET'])
def get_structure():
    # 获取并清理 URL 参数
    github_url = request.args.get('url')

    # 如果没有提供 GitHub URL，则返回错误信息
    if not github_url:
        return jsonify({"error": "No GitHub URL provided"}), 400

    # 清理 URL，去除可能的干扰字符
    github_url = github_url.replace(" ", "").replace("'", "")

    # 使用正则表达式提取有效的 GitHub URL
    match = re.search(r'https://github\.com/([^/]+)/([^/]+).git', github_url)
    if not match:
        return jsonify({"error": "Invalid GitHub URL format"}), 400

    owner = match.group(1)
    repo = match.group(2)

    # GitHub API 端点用于获取仓库结构
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        # 发送请求并获取响应
        response = requests.get(api_url, timeout=requests.DEFAULT_REQUESTS_TIMEOUT)
        response.raise_for_status()  # 对于非2xx状态码抛出异常
        data = response.json()

        # 打印响应数据以供调试
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response data: {data}")

        # 返回仓库结构
        return jsonify({"structure": data})

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='XXXX.2', port=8805,debug=True)
```

## 13.4 输入输出

输入Github的url 从下图中得到

![image-20250504162250436](C:\Users\Claire\AppData\Roaming\Typora\typora-user-images\image-20250504162250436.png)

![image-20250504162300661](C:\Users\Claire\AppData\Roaming\Typora\typora-user-images\image-20250504162300661.png)

