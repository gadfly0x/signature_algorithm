"""
蛋壳公寓 App API 签名模块。

对请求参数按 key 排序后拼接盐值，计算 MD5 签名。
服务器会校验时间戳，偏差超过 90 秒签名失效。
"""

from signature_algorithm.danke import app
