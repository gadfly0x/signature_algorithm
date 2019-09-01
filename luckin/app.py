import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class LuckIn:
    secret_key = b'bmk6hcs3FKXUdsZG'  # 密钥

    @classmethod
    def encrypt(cls, text):
        """
        DES 加密
        :param text: 待加密字符串
        :return: 加密后字符串
        """
        # 填充
        text = pad(text.encode(), AES.block_size)
        # AES初始化
        cipher = AES.new(cls.secret_key, AES.MODE_ECB)
        # AES加密
        encrypted_text = cipher.encrypt(text)
        # bytes转换成编码
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode(encoding='utf-8')
        return encrypted_text

    @classmethod
    def decrypt(cls, encrypted_text):
        """
        DES 解密
        :param encrypted_text: 待解密的字符串
        :return:  解密后的字符串
        """
        # "url safe"格式base64转bytes
        base64_decrypted = base64.urlsafe_b64decode(encrypted_text)
        # AES初始化
        aes = AES.new(cls.secret_key, AES.MODE_ECB)
        # AES解密
        decrypted_text = aes.decrypt(base64_decrypted)
        # 去掉填充
        decrypted_text = unpad(decrypted_text, AES.block_size)
        # bytes转字符串
        decrypted_text = decrypted_text.decode(encoding='utf-8')
        return decrypted_text


if __name__ == '__main__':
    text = 'a0fzFzgUe_Oq-7uhPrOt9vDgKrw66ygP7-8rPCHNCfhQEGaydeaCHZNrQ9K-Jv3Y'
    decrypted_text = LuckIn.decrypt(text)
    print(decrypted_text)
    encrypted_text = LuckIn.encrypt(decrypted_text)
    print(encrypted_text)

