# signature_algorithm

各种 App、小程序、网站的签名或加密算法 Python 实现。逆向对象均为 iOS 版本，可能与 Android 版本不同。

## 目录结构

```
signature_algorithm/
├── ziroom/          # 自如 - DES 加解密
├── danke/           # 蛋壳公寓 - MD5 签名
├── xiaohongshu/     # 小红书 - XOR + MD5 签名
├── luckin/          # 瑞幸咖啡 - AES 加解密
└── bangkokair/      # 曼谷航空 - 反爬脚本执行
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

各模块可直接运行，均包含 `if __name__ == '__main__'` 示例代码：

```bash
python ziroom/app.py        # 自如搜索接口加解密
python danke/app.py         # 蛋壳公寓搜索签名
python xiaohongshu/app.py   # 小红书 sign 算法
python luckin/app.py        # 瑞幸咖啡加解密
python bangkokair/web.py    # 曼谷航空航班查询
```

## API 参考

### 自如 (ziroom)

DES-CBC 加解密，用于自如 API 请求体加密和响应解密。

```python
from signature_algorithm.ziroom.app import ZiRoom

encrypted = ZiRoom.des_encrypt(b'plain text')   # 加密 -> hex 字符串
decrypted = ZiRoom.des_decrypt(encrypted)        # 解密 -> bytes
```

### 蛋壳公寓 (danke)

MD5 签名算法，用于蛋壳 API 请求参数签名。

```python
from signature_algorithm.danke.app import sign_with_query_items

sign = sign_with_query_items({'page': '1', 'search_text': '关键词', ...})
```

### 小红书 (xiaohongshu)

XOR + 双重 MD5 签名，需配合 deviceId 使用。

```python
from signature_algorithm.xiaohongshu.app import sign_with_query_items

sign = sign_with_query_items({'deviceId': '...', 'keyword': '...', ...})
```

### 瑞幸咖啡 (luckin)

AES-ECB 加解密，用于瑞幸 API 数据加密。

```python
from signature_algorithm.luckin.app import LuckIn

encrypted = LuckIn.encrypt('plain text')       # 加密
decrypted = LuckIn.decrypt(encrypted_text)      # 解密
```

### 曼谷航空 (bangkokair)

反爬签名，模拟浏览器环境执行 JS 脚本实现 proof-of-work。

```python
from signature_algorithm.bangkokair.web import Bangkokair

b = Bangkokair(request_params)
b.main()
```

## App 列表

| App | 起始版本 | 状态 |
|---|---|---|
| 自如 | 6.3.3 | 完成 |
| 蛋壳公寓 | 1.20.0 | 完成 |
| 小红书 | 6.0 | 仅 sign，shield 未实现 |
| 瑞幸咖啡 | 2.8.5 | sign 未实现 |

## 网站列表

| 网站 | 起始日期 | 状态 |
|---|---|---|
| bangkokair (曼谷航空) | 2019.12.07 | 完成 |

> [曼谷航空算法详解](https://github.com/gadfly0x/signature_algorithm/wiki/bangkokair%E6%9B%BC%E8%B0%B7%E8%88%AA%E7%A9%BA)

## 贡献

如果发现有趣的 App、小程序、网站这里没有，欢迎提 issue。

## 免责声明

本项目所有内容仅供技术交流，请勿用于商业及非法用途，因此产生的任何法律纠纷均与本人无关。
