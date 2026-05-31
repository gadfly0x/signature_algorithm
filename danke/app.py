"""
蛋壳公寓 App API 签名模块。

签名算法为 MD5：将请求参数按 key 字典序排序后拼接 key+value，
在首尾各加一次盐值，取 MD5 后转为大写。
"""

import hashlib


def sign_with_query_items(data: dict) -> str:
    """对请求参数生成 MD5 签名。

    算法步骤：
    1. 将请求参数按 key 排序
    2. 将所有 key 和 value 拼接成字符串
    3. 首尾拼接盐值 (salt)
    4. 计算 MD5 并转为大写

    Args:
        data: 请求参数字典（不含 sign 字段）

    Returns:
        大写的 MD5 签名字符串
    """
    salt = 'R2UJE2UNhINnvjfaVPEC7FM8aUBoRVmgtv0zAhAD'
    # 将请求参数按 key 字典序排序
    data = {k: data[k] for k in sorted(data.keys())}
    # 将 key 和 value 拼接
    data_str = ''
    for k, v in data.items():
        data_str += str(k) + str(v)
    # 首尾拼接盐值
    pre_str = '{salt}{data}{salt}'.format(salt=salt, data=data_str)
    # 计算 MD5
    md5 = hashlib.md5()
    md5.update(pre_str.encode())
    sign = md5.hexdigest()
    # 转为大写
    sign = sign.upper()
    return sign


if __name__ == '__main__':
    import time
    import requests

    # 搜索接口示例
    url = "https://api-room.danke.com/v1/room/list"
    method = "GET"
    # 服务器会校验时间戳，时间戳偏差超过 90 秒返回签名失效
    params = {
        "page": "1",
        "timestamp": int(time.time()),
        "search_text": "霍营",
        "city_id": "1",
        "isnewformat": "1",
    }
    headers = {
        "x-app-id": "3",
        "sign": sign_with_query_items(params),
    }

    data = {}
    rst = requests.request(method, url, headers=headers, params=params, data=data)
    print(rst.status_code)
    print(rst.text)
