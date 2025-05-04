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
    app.run(host='192.168.122.2', port=8805,debug=True)