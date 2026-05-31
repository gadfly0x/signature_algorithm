"""
自如 App API 加解密模块。

使用 DES-CBC 模式对自如 API 的请求体和响应体进行加解密。
请求体需先 JSON 序列化后加密，服务端返回的密文需解密后解析。
"""

import binascii
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad, pad


class ZiRoom:
    """自如 API DES-CBC 加解密工具类。

    密钥和 IV 均从 iOS 逆向获得。
    """

    secret_key = b'vpRZ1kmU'
    iv = b'EbpU4WtY'

    @classmethod
    def des_encrypt(cls, content: bytes) -> bytes:
        """DES-CBC 加密，返回 16 进制字符串。

        Args:
            content: 明文字节串

        Returns:
            加密后的 16 进制字节串
        """
        cipher = DES.new(cls.secret_key, DES.MODE_CBC, cls.iv)
        encrypted_content = cipher.encrypt(pad(content, DES.block_size))
        return binascii.b2a_hex(encrypted_content)

    @classmethod
    def des_decrypt(cls, content: str) -> bytes:
        """DES-CBC 解密，输入 16 进制密文。

        Args:
            content: 16 进制密文字符串

        Returns:
            解密后的明文字节串
        """
        cipher = DES.new(cls.secret_key, DES.MODE_CBC, cls.iv)
        decrypted_content = unpad(cipher.decrypt(binascii.a2b_hex(content)), DES.block_size)
        return decrypted_content


if __name__ == '__main__':
    import requests
    import json

    # 搜索接口示例
    url = "https://ztoread.ziroom.com/phoenix/v7/room/list.json"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        'size': 10,
        'suggestion_value': '青年路',
        'suggestion_type': 3,
        'uid': '0',
        'city_code': '110000',
        'page': 2,
    }
    # 将请求体 JSON 序列化后加密
    data = ZiRoom.des_encrypt(json.dumps(data))
    # 发送请求
    rst = requests.post(url, data, headers=headers)
    # 解密响应
    room_list = json.loads(ZiRoom.des_decrypt(rst.text))
    print(room_list)
