"""
瑞幸咖啡 App API 加解密模块。

使用 AES-ECB 模式进行加解密，密钥从 iOS 逆向获得。
注意：sign 算法尚未实现。
"""

import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class LuckIn:
    """瑞幸咖啡 AES-ECB 加解密工具类。

    使用 16 字节密钥进行 AES-ECB 加解密，
    密文采用 URL-safe base64 编码。
    """

    secret_key = b'bmk6hcs3FKXUdsZG'

    @classmethod
    def encrypt(cls, text: str) -> str:
        """AES-ECB 加密。

        Args:
            text: 明文字符串

        Returns:
            URL-safe base64 编码的密文字符串
        """
        # PKCS7 填充
        text = pad(text.encode(), AES.block_size)
        # AES-ECB 加密
        cipher = AES.new(cls.secret_key, AES.MODE_ECB)
        encrypted_text = cipher.encrypt(text)
        # URL-safe base64 编码
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode(encoding='utf-8')
        return encrypted_text

    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """AES-ECB 解密。

        Args:
            encrypted_text: URL-safe base64 编码的密文

        Returns:
            解密后的明文字符串
        """
        # URL-safe base64 解码
        base64_decrypted = base64.urlsafe_b64decode(encrypted_text)
        # AES-ECB 解密
        aes = AES.new(cls.secret_key, AES.MODE_ECB)
        decrypted_text = aes.decrypt(base64_decrypted)
        # 去掉 PKCS7 填充
        decrypted_text = unpad(decrypted_text, AES.block_size)
        # bytes 转字符串
        decrypted_text = decrypted_text.decode(encoding='utf-8')
        return decrypted_text


if __name__ == '__main__':
    text = 'a0fzFzgUe_Oq-7uhPrOt9vDgKrw66ygP7-8rPCHNCfhQEGaydeaCHZNrQ9K-Jv3Y'
    decrypted_text = LuckIn.decrypt(text)
    print(decrypted_text)
    encrypted_text = LuckIn.encrypt(decrypted_text)
    print(encrypted_text)
