## 12-生成Excel数据表

[dify AI教程：Dify_Flask_Excel_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1WKkzYhEAM?spm_id_from=333.788.videopod.sections&vd_source=c47fbb8166930edc486d8fdc405bf569)

## 12.1 任务定义

利用大语言模型生成内容，将内容写入excel数据表中。该功能涉及两大核心；其一如何创建并保存excel文件;其二如何动态写入数据表字段和字段条目。

## 12.2 整体的流程图

![img](file:///C:\Users\Claire\AppData\Local\Temp\ksohtml88872\wps21.jpg) 

## 12.3 提示

提示词如上述所示，给了具体的任务要求，每个字段的具体要求，输出形式

```
请根据以下描述生成一个包5个条目的JSON对象，每个条目有六个字段："姓名"、"年龄"、"职业"、"姓名A"、"年龄A"和"职业A"。具体要求如下：

\- "姓名"字段应包含30个不同的中国名字。

\- "年龄"字段应包含30个介于20到65之间的整数。

\- "职业"字段应包含30个常见的职业名称，可以从以下列表中随机选择："工程师", "医生", "教师", "律师", "设计师", "会计师", "程序员", "科学家", "艺术家", "作家"。

\- "姓名A"字段应包含30个不同的中国名字。

\- "年龄A"字段应包含30个介于20到65之间的整数。

\- "职业A"字段应包含30个常见的职业名称，可以从以下列表中随机选择："工程师", "医生", "教师", "律师", "设计师", "会计师", "程序员", "科学家", "艺术家", "作家"。

 

请确保生成的内容是一个单一的、有效的JSON对象，并按照以下格式组织：

 

\```json

{

"姓名": ["张三", "李四", "王五", ...], // 5个不同的中国名字

"年龄": [23, 34, 45, ...], // 5个介于20到65之间的整数

"职业": ["工程师", "医生", "教师", ...], // 5个常见的职业名称

"姓名A": ["张三", "李四", "王五", ...], // 5个不同的中国名字

"年龄A": [23, 34, 45, ...], // 5个介于20到65之间的整数

"职业A": ["工程师", "医生", "教师", ...] // 5个常见的职业名称

}
```

## 12.4 参数提取

需要将大模型的输出进行一个内容提取，去掉不相关的内容，只保留想要的内容。

 

```
请确保生成的内容是一个单一的、有效的JSON对象，并按照以下格式组织：

 

\```json

{

"姓名": ["张三", "李四", "王五", ...], // 30个不同的中国名字

"年龄": [23, 34, 45, ...], // 30个介于20到65之间的整数

"职业": ["工程师", "医生", "教师", ...], // 30个常见的职业名称

"姓名A": ["张三", "李四", "王五", ...], // 30个不同的中国名字

"年龄A": [23, 34, 45, ...], // 30个介于20到65之间的整数

"职业A": ["工程师", "医生", "教师", ...] // 30个常见的职业名称

}
```

## 12.5 模板转化

为了使输出的参数存为一个字符串输出，对后面节点能够有一个输出的值。

## 12.6 HTTP请求

首先将LLM输出转化为EXCEL写入的代码文件进行运行，得到HTTP地址，之后添加HTTP节点，定义输入到内容的形式，最后返回EXCEL的下载地址，能够得到生成的EXCEL表。

代码：【Excel_flask_Server.py】代码

```
import logging
from flask import Flask, request, jsonify,send_file
import pandas as pd
import os
from datetime import datetime

# 以上是包

app = Flask(__name__)# 创建Flask应用实例

# 配置日志记录级别为DEBUG，记录所有级别的日志
logging.basicConfig(level=logging.DEBUG)

# 确保data目录存在
# os.path.dirname(os.path.abspath(__file__)) 获取当前脚本的绝对路径的目录名
# abspath绝对路径
# dirname目录名
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):# DATA_DIR是否存在
    os.makedirs(DATA_DIR)# 创建路径
logging.info(f'DATA_DIR的路径：{DATA_DIR}')

# 定义路由和处理函数
@app.route('/create_excel', methods=['POST'])
def create_excel():
    app.logger.debug('Received POST request to /create_excel')
    
    try:
        # 获取请求中的数据，注意这个是json的请求，其实我就好奇怎么用，我之前看到视频都是raw
        print(f'request{request}')
        logging.info(f'request{request}')
        data = request.json
        logging.info(f'data:{data}')
        print(f'data:{data}')
        fields = data.get('fields', [])
        values = data.get('values', {})
        logging.info(f'data.values:{values}')
        print(f'data.values:{values}')

        if isinstance(values, list):
            values = values[0]

        # 输入验证，fields不为空的列表
        if not fields or not isinstance(fields, list) or len(fields) == 0:
            return jsonify({"error": "'fields' must be a non-empty list."}), 400

        # 必须是一个字典
        if not values or not isinstance(values, dict):
            return jsonify({"error": "'values' must be a dictionary."}), 400

        # 检查所有值列表是否长度一致
        expected_length = None
        for field in fields:
            if field not in values: ## 如果字段不在values中，返回400错误
                return jsonify({"error": f"Missing values for field '{field}'."}), 400

            current_length = len(values[field])
            if expected_length is None:
                expected_length = current_length
            elif current_length != expected_length:
                return jsonify(
                    {"error": f"All value lists must have the same length. Field '{field}' does not match."}), 400

        app.logger.debug(f'Fields received: {fields}')
        app.logger.debug(f'Values received: {values}')

        # 创建带有数据的DataFrame
        # # 使用字典推导式创建数据字典，确保所有字段都有值(用None填充缺失值)
        df_data = {field: values.get(field, [None] * expected_length) for field in fields}
        df = pd.DataFrame(df_data) # 从字典创建DataFrame

        # 定义文件名和完整路径，确保文件名唯一
        base_filename = 'output_{}.xlsx'
        # # 生成时间戳字符串，精确到毫秒(去掉微秒的最后3位)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 使用毫秒级时间戳确保唯一性
        # 还可以这么写！！！！！！！
        filename = base_filename.format(timestamp)
        file_path = os.path.join(DATA_DIR, filename)

        # 检查文件是否存在，如果存在则添加序号以保证文件名唯一
        counter = 1
        while os.path.exists(file_path):
            filename = base_filename.format(f"{timestamp}_{counter}")
            file_path = os.path.join(DATA_DIR, filename)
            counter += 1

        # 保存到Excel文件
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)

        app.logger.debug(f'Excel file saved to: {file_path}')

        download_url = request.host_url + 'download/' + os.path.basename(file_path)
        print(download_url)
        return {'download_url': download_url}

        # 返回文件路径作为响应
        return jsonify({
            "message": "File created successfully.",
            "file_path": file_path
        }), 200

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

    

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join('data', filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='XXX.2', port=8805,debug=True)
```

## 12.7 最后输出下载链接

直接回复节点，输出的是HTTP请求节点的body。

![image-20250504160137088](C:\Users\Claire\AppData\Roaming\Typora\typora-user-images\image-20250504160137088.png)

![image-20250504160142399](C:\Users\Claire\AppData\Roaming\Typora\typora-user-images\image-20250504160142399.png)