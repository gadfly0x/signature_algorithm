"""
signature_algorithm - 各种 App 和网站的签名/加密算法集合。

子包:
    - ziroom:      自如 App DES-CBC 加解密
    - xiaohongshu: 小红书 App XOR + MD5 签名
    - danke:       蛋壳公寓 App MD5 签名
    - luckin:      瑞幸咖啡 App AES-ECB 加解密
    - bangkokair:  曼谷航空网站反爬签名
"""

from signature_algorithm import ziroom
from signature_algorithm import xiaohongshu
from signature_algorithm import danke
