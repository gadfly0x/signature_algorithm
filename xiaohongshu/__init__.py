"""
小红书 App API 签名模块。

使用 XOR + 双重 MD5 算法对请求参数生成签名。
需要传入 deviceId 作为异或因子。
注意：仅实现了 sign 算法，shield 算法未实现。
"""

from signature_algorithm.xiaohongshu import app
