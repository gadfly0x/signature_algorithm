import urllib
import hashlib


def sign_with_query_items(data):
    udid = data['deviceId']
    # 将请求参数按key排序
    data = {k: data[k] for k in sorted(data.keys())}
    # 拼接成字符串
    data_str = ''
    for k, v in data.items():
        data_str += '{}={}'.format(k, v)
    data_str = urllib.parse.quote(data_str, 'utf-8')

    # 将url encode之后的字符串的每个字符与对应的udid字符进行异或原形
    xor_str = ''
    udid_length = len(udid)
    for i in range(len(data_str)):
        data_char = data_str[i]
        udid_index = int(i % udid_length)
        udid_char = udid[udid_index]
        rst = ord(udid_char) ^ ord(data_char)
        xor_str += str(rst)

    # 对异或后的字符串MD5
    md5 = hashlib.md5()
    md5.update(xor_str.encode())
    md5_str = md5.hexdigest()

    # 将MD5后的字符串和udid拼接起来，再次MD5
    md5_str += udid
    md5 = hashlib.md5()
    md5.update(md5_str.encode())
    md5_str = md5.hexdigest()
    return md5_str


if __name__ == '__main__':
    # 去掉sign的其他所有参数，参数以字符顺序排序，以搜索接口为例
    # https://www.xiaohongshu.com/api/sns/v9/search/notes
    params = {
        "allow_rewrite": "",
        "api_extra": "",
        "deviceId": "",
        "device_fingerprint": "",
        "device_fingerprint1": "",
        "fid": "",
        "keyword": "",
        "keyword_type": "",
        "lang": "",
        "page": "",
        "page_pos": "",
        "page_size": "",
        "platform": "",
        "search_id": "",
        "sid": "",
        # "sign": "",
        "sort": "",
        "source": "",
        "t": ""
    }
    print(sign_with_query_items(params))
