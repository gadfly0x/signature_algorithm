import hashlib


def sign_with_query_items(data):
    salt = 'R2UJE2UNhINnvjfaVPEC7FM8aUBoRVmgtv0zAhAD'
    # 将请求参数按key排序
    data = {k: data[k] for k in sorted(data.keys())}
    # 将key和value拼接成字符串
    data_str = ''
    for k, v in data.items():
        data_str += str(k) + str(v)
    # 首尾都拼接上盐
    pre_str = '{salt}{data}{salt}'.format(salt=salt, data=data_str)
    # md5
    md5 = hashlib.md5()
    md5.update(pre_str.encode())
    salt = md5.hexdigest()
    # 转成大写
    salt = salt.upper()
    return salt


if __name__ == '__main__':
    import time
    import requests

    # 以搜索接口为例
    url = "https://api-room.danke.com/v1/room/list"
    method = "GET"
    # 服务器会校验时间戳，时间戳距离相差90秒，会返回签名失效
    params = {
        "page": "1",
        "timestamp": int(time.time()),
        "search_text": "霍营",
        "city_id": "1",
        "isnewformat": "1"
    }
    headers = {
        "x-app-id": "3",
        "sign": sign_with_query_items(params)
    }

    data = {}
    rst = requests.request(method, url, headers=headers, params=params, data=data)
    print(rst.status_code)
    print(rst.text)
