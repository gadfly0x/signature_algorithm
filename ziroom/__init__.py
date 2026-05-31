"""
自如 App API 加解密模块。

使用 DES-CBC 模式对自如 API 的请求和响应进行加解密。
密钥和 IV 从 iOS 逆向获得。
"""

from signature_algorithm.ziroom import app
