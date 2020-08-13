import binascii
from Crypto.Cipher import DES
from Crypto.Util.Padding import unpad, pad


class ZiRoom:
    secret_key = b'vpRZ1kmU'
    iv = b'EbpU4WtY'

    @classmethod
    def des_encrypt(cls, content):
        """
        DES 加密
        :param content: 原始字符串
        :return: 加密后字符串，16进制
        """
        cipher = DES.new(cls.secret_key, DES.MODE_CBC, cls.iv)
        encrypted_content = cipher.encrypt(pad(content, DES.block_size))
        return binascii.b2a_hex(encrypted_content)

    @classmethod
    def des_decrypt(cls, content):
        """
        DES 解密
        :param content: 加密后的字符串，16进制
        :return:  解密后的字符串
        """
        cipher = DES.new(cls.secret_key, DES.MODE_CBC, cls.iv)
        decrypted_content = unpad(cipher.decrypt(binascii.a2b_hex(content)), DES.block_size)
        return decrypted_content


if __name__ == '__main__':
    import requests
    import json
    # 以搜索接口为例
    url = "https://ztoread.ziroom.com/phoenix/v7/room/list.json"
    headers = {
        "Content-Type": "application/json"
    }
    data = {'size': 10, 'suggestion_value': '青年路', 'suggestion_type': 3, 'uid': '0', 'city_code': '110000', 'page': 1}
    # 加密请求参数
    data = ZiRoom.des_encrypt(json.dumps(data))
    # 发送请求
    rst = requests.post(url, data, headers=headers)
    # 解密
    room_list = json.loads(ZiRoom.des_decrypt(rst.text))
    print(room_list)
