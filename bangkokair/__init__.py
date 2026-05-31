"""
曼谷航空网站反爬签名模块。

模拟浏览器环境，执行网站 JS 脚本完成客户端指纹验证
和 proof-of-work 签名，绕过 Distil Networks 反爬系统。
"""

from signature_algorithm.bangkokair import web
