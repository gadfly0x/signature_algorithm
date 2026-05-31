"""
小红书 App API sign 签名模块。

签名算法基于 deviceId 的 XOR + 双重 MD5：
1. 请求参数按 key 排序后拼接为 k=v 格式
2. URL encode 后与 deviceId 逐字符 XOR
3. XOR 结果取 MD5
4. MD5 结果拼接 deviceId 后再取一次 MD5

注意：该模块仅实现了 sign 算法，shield 算法未实现。
"""

import urllib
import hashlib


def sign_with_query_items(data: dict) -> str:
    """对请求参数生成 sign 签名。

    使用 deviceId 作为异或因子，对 URL 编码后的参数字符串
    逐字符异或，再经过两次 MD5 得到最终签名。

    Args:
        data: 请求参数字典，必须包含 deviceId 字段

    Returns:
        MD5 签名字符串
    """
    udid = data['deviceId']
    # 将请求参数按 key 字典序排序
    data = {k: data[k] for k in sorted(data.keys())}
    # 拼接为 k=v 格式
    data_str = ''
    for k, v in data.items():
        data_str += '{}={}'.format(k, v)
    data_str = urllib.parse.quote(data_str, 'utf-8')

    # 将 URL 编码后的每个字符与对应位置的 deviceId 字符进行 XOR
    xor_str = ''
    udid_length = len(udid)
    for i in range(len(data_str)):
        data_char = data_str[i]
        udid_index = int(i % udid_length)
        udid_char = udid[udid_index]
        rst = ord(udid_char) ^ ord(data_char)
        xor_str += str(rst)

    # 第一次 MD5
    md5 = hashlib.md5()
    md5.update(xor_str.encode())
    md5_str = md5.hexdigest()

    # 拼接 deviceId 后第二次 MD5
    md5_str += udid
    md5 = hashlib.md5()
    md5.update(md5_str.encode())
    md5_str = md5.hexdigest()
    return md5_str


if __name__ == '__main__':
    # 以搜索接口为例，参数需按字符顺序排序
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
        # "sign": "",   # sign 由本函数生成，不需要传入
        "sort": "",
        "source": "",
        "t": "",
    }
    print(sign_with_query_items(params))
