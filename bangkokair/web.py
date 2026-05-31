"""
曼谷航空 (Bangkok Airways) 网站反爬签名模块。

该网站使用 Distil Networks 反爬方案：通过 JS 脚本生成 proof-of-work 签名，
需要在 Python 中执行 JS 代码来完成客户端指纹验证和签名的计算。

工作流程：
1. 提交订票请求 → booking
2. 从返回的 HTML 提取 PGxxx.js 文件名 → get_pg_js_name
3. 执行 check_client JS (qlSUmvhsKL.js) 做客户端指纹验证
4. 请求 PGxxx.js 获取 PID → get_pid
5. 执行 proof JS (PGxxx.js) 获取 cookie → get_cookies
6. 重新提交订票请求 → search
7. 解析航班数据 → search_parse
"""

import os
import re
import json
import execjs
import random
import requests


def get_random_str(length: int = 64, chars: str = '0123456789abcdef') -> str:
    """生成指定长度的随机十六进制字符串，用于模拟浏览器指纹。"""
    return ''.join(random.choice(chars) for _ in range(length))


class RequestError(Exception):
    """曼谷航空 API 请求异常。"""
    pass


class Bangkokair:
    """曼谷航空反爬签名客户端。

    模拟浏览器环境，执行网站的 JS 脚本生成 proof-of-work 签名，
    完成订票流程中的各步骤，最终获取航班和价格信息。

    示例用法:
        params = {
            "B_LOCATION": "CNX",     # 出发机场
            "E_LOCATION": "BKK",     # 到达机场
            "B_DATE": "201912150000", # 出发日期
            "ADULTS": "1",
            ...
        }
        b = Bangkokair(params)
        b.main()
    """

    default_user_agent = (
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)"
    )

    def __init__(self, request_params: dict, **kwargs):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.common_data = {
            'canvas_img': get_random_str(length=40),
            'webGL_img': get_random_str(length=40),
            'PG_JS_name': '',       # PGxxx.js 文件名，从 HTML 中解析
            'PID': '',              # 页面 ID
            'booking_data': {},     # 初始订票请求的返回数据
            'html': '',             # 搜索结果页面 HTML
            'GMT_FORMAT': '%b %d, %Y %I:%M:%S %p',
        }
        # 初始化 HTTP 会话
        self.session = requests.session()
        self.session.proxies = kwargs.get('proxies', {})
        self.user_agent = kwargs.get('user_agent', self.default_user_agent)
        self.request_params = request_params

    def main(self):
        """执行完整的订票查询流程。"""
        self.booking()
        self.get_pg_js_name()
        self.check_client()
        self.get_pid()
        self.get_cookies()
        self.search()
        self.search_parse()

    def booking(self):
        """步骤 1：提交初始订票请求，获取后续需要的 token 和 URL。"""
        url = "https://www.bangkokair.com/AdTripFlow/booking"
        method = "POST"
        rst = self.session.request(method, url, data=self.request_params)
        if rst.status_code != 200:
            raise RequestError('booking 请求失败: %s' % rst.status_code)
        self.common_data['booking_data'] = rst.json()

    def get_pg_js_name(self):
        """步骤 2：从返回 HTML 中提取 PGxxx.js 文件名。

        PGxxx.js 是 Distil Networks 的指纹脚本，
        每请求一次文件名都会变化。
        """
        booking_data = self.common_data['booking_data']
        url = booking_data['url']
        method = "POST"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.user_agent,
        }
        data = {
            "LANGUAGE": booking_data['LANGUAGE'],
            "EMBEDDED_TRANSACTION": booking_data['EMBEDDED_TRANSACTION'],
            "SITE": booking_data['SITE'],
            "ENCT": booking_data['ENCT'],
            "ENC": booking_data['ENC'],
        }
        rst = self.session.request(method, url, headers=headers, data=data)
        if rst.status_code != 200:
            raise RequestError('获取 PGxxx.js 失败: %s' % rst.status_code)
        # 从 HTML 中正则匹配 PGxxxx.js 文件名
        patt = r'<script type="text/javascript" src="/(PG\w+.js)"'
        self.common_data['PG_JS_name'] = re.findall(patt, rst.text)[0]

    def check_client(self):
        """步骤 3：执行 qlSUmvhsKL.js 做客户端环境校验。

        构造模拟浏览器指纹（canvas、webGL、字体、插件等），
        将指纹对象传入 JS proof 函数生成签名，提交给服务器验证。
        """
        interrogation = {
            "userAgent": self.user_agent,
            "language": "en-US",
            "screen": {
                "width": 1920,
                "height": 1050,
                "availHeight": 955,
                "availWidth": 1920,
                "pixelDepth": 24,
                "innerWidth": 1660,
                "innerHeight": 264,
                "outerWidth": 1660,
                "outerHeight": 955,
                "devicePixelRatio": 2
            },
            "timezone": -8,
            "indexedDb": True,
            "addBehavior": False,
            "openDatabase": True,
            "cpuClass": "unknown",
            "platform": "MacIntel",
            "doNotTrack": "unknown",
            "plugins": "",
            "canvas": {
                "winding": "yes",
                "towebp": True,
                "blending": True,
                "img": self.common_data['canvas_img'],
            },
            "webGL": {
                "img": self.common_data['webGL_img'],
                "extensions": "",
                "aliased line width range": "[1, 1]",
                "aliased point size range": "[0.125, 8192]",
                "alpha bits": 8,
                "antialiasing": "yes",
                "blue bits": 8,
                "depth bits": 24,
                "green bits": 8,
                "max anisotropy": 16,
                "max combined texture image units": 32,
                "max cube map texture size": 8192,
                "max fragment uniform vectors": 261,
                "max render buffer size": 8192,
                "max texture image units": 16,
                "max texture size": 8192,
                "max varying vectors": 32,
                "max vertex attribs": 32,
                "max vertex texture image units": 16,
                "max vertex uniform vectors": 256,
                "max viewport dims": "[8192, 8192]",
                "red bits": 8,
                "renderer": "WebKit WebGL",
                "shading language version": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
                "stencil bits": 0,
                "vendor": "WebKit",
                "version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
                "vertex shader high float precision": 23,
                "vertex shader high float precision rangeMin": 127,
                "vertex shader high float precision rangeMax": 127,
                "vertex shader medium float precision": 23,
                "vertex shader medium float precision rangeMin": 127,
                "vertex shader medium float precision rangeMax": 127,
                "vertex shader low float precision": 23,
                "vertex shader low float precision rangeMin": 127,
                "vertex shader low float precision rangeMax": 127,
                "fragment shader high float precision": 23,
                "fragment shader high float precision rangeMin": 127,
                "fragment shader high float precision rangeMax": 127,
                "fragment shader medium float precision": 23,
                "fragment shader medium float precision rangeMin": 127,
                "fragment shader medium float precision rangeMax": 127,
                "fragment shader low float precision": 23,
                "fragment shader low float precision rangeMin": 127,
                "fragment shader low float precision rangeMax": 127,
                "vertex shader high int precision": 0,
                "vertex shader high int precision rangeMin": 31,
                "vertex shader high int precision rangeMax": 30,
                "vertex shader medium int precision": 0,
                "vertex shader medium int precision rangeMin": 31,
                "vertex shader medium int precision rangeMax": 30,
                "vertex shader low int precision": 0,
                "vertex shader low int precision rangeMin": 31,
                "vertex shader low int precision rangeMax": 30,
                "fragment shader high int precision": 0,
                "fragment shader high int precision rangeMin": 31,
                "fragment shader high int precision rangeMax": 30,
                "fragment shader medium int precision": 0,
                "fragment shader medium int precision rangeMin": 31,
                "fragment shader medium int precision rangeMax": 30,
                "fragment shader low int precision": 0,
                "fragment shader low int precision rangeMin": 31,
                "fragment shader low int precision rangeMax": 30
            },
            "touch": {
                "maxTouchPoints": 0,
                "touchEvent": False,
                "touchStart": False
            },
            "video": {
                "ogg": "probably",
                "h264": "probably",
                "webm": "probably"
            },
            "audio": {
                "ogg": "probably",
                "mp3": "probably",
                "wav": "probably",
                "m4a": "maybe"
            },
            "vendor": "Google Inc.",
            "product": "Gecko",
            "productSub": "20030107",
            "browser": {
                "ie": False,
                "chrome": True,
                "webdriver": False
            },
            "window": {
                "historyLength": 3,
                "hardwareConcurrency": 8,
                "iframe": False
            },
            "fonts": ""
        }

        with open(self.base_path + '/qlSUmvhsKL.js') as fp:
            js = fp.read()
            ctx = execjs.compile(js)
        proof = ctx.call('proof', interrogation)
        kwargs = {
            "method": "POST",
            "url": "https://flightbook.bangkokair.com/qlSUmvhsKL",
            "params": {
                "d": "flightbook.bangkokair.com"
            },
            "headers": {
                "accept": "application/json; charset=utf-8",
                "origin": "https://flightbook.bangkokair.com",
                "user-agent": self.user_agent,
                "content-type": "text/plain; charset=utf-8",
                "referer": "https://flightbook.bangkokair.com/plnext/BangkokAir/Override.action",
                "accept-language": "en-US,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            "data": json.dumps({
                "solution": {
                    "interrogation": interrogation,
                    "proof": proof,
                    "version": "stable"
                },
                "old_token": None
            }),
        }
        rst = self.session.request(**kwargs)
        if rst.status_code != 200:
            raise RequestError('qlSUmvhsKL 请求失败: %s' % rst.status_code)

    def get_pid(self):
        """步骤 4：访问 PGxxx.js 并从页面中提取 PID。

        PID 用于后续 cookie 获取步骤的鉴权参数。
        """
        url = "https://flightbook.bangkokair.com/%s" % self.common_data['PG_JS_name']
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.user_agent,
        }
        rst = self.session.request("GET", url, headers=headers)
        if rst.status_code != 200:
            raise RequestError('PID 获取失败: %s' % rst.status_code)
        # 从 JavaScript URL 中解析 PID 参数
        patt = r'"/PG[a-z]+.js\?PID=([A-Z0-9-]+)"'
        self.common_data['PID'] = re.findall(patt, rst.text)[0]

    def get_cookies(self):
        """步骤 5：执行 PGxxx.js 的 proof 函数获取签名 cookie。

        重新构造一份浏览器指纹（fp2），调用 JS proof 函数生成签名，
        服务器验证通过后会在响应中 Set-Cookie。
        """
        url = "https://flightbook.bangkokair.com/%s" % self.common_data['PG_JS_name']
        method = "POST"
        headers = {
            "origin": "https://flightbook.bangkokair.com",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": self.user_agent,
            "content-type": "text/plain;charset=UTF-8",
            "accept": "*/*",
            "referer": "https://flightbook.bangkokair.com/plnext/BangkokAir/Override.action",
            "authority": "flightbook.bangkokair.com",
            "x-distil-ajax": "dffavbcsxwsvsdsd"
        }
        params = {
            "PID": self.common_data['PID'],
        }
        # 随机生成设备 ID，模拟多个音频/视频设备
        groupId = get_random_str()
        groupId2 = get_random_str()
        p = {
            "proof": "",
            "fp2": {

                "userAgent": self.user_agent.replace(' ', ''),
                "language": "en-US",
                "screen": {
                    "width": 1920,
                    "height": 1050,
                    "availHeight": 955,
                    "availWidth": 1920,
                    "pixelDepth": 24,
                    "innerWidth": 1920,
                    "innerHeight": 328,
                    "outerWidth": 1920,
                    "outerHeight": 1050,
                    "devicePixelRatio": 2
                },
                "timezone": -8,
                "indexedDb": True,
                "addBehavior": False,
                "openDatabase": True,
                "cpuClass": "unknown",
                "platform": "MacIntel",
                "doNotTrack": "unknown",
                "plugins": "",
                "canvas": {
                    "winding": "yes",
                    "towebp": True,
                    "blending": True,
                    "img": self.common_data['canvas_img']
                },
                "webGL": {
                    "img": self.common_data['webGL_img'],
                    "extensions": "",
                    "aliasedlinewidthrange": "[1,1]",
                    "aliasedpointsizerange": "[0.125,8192]",
                    "alphabits": 8,
                    "antialiasing": "yes",
                    "bluebits": 8,
                    "depthbits": 24,
                    "greenbits": 8,
                    "maxanisotropy": 16,
                    "maxcombinedtextureimageunits": 32,
                    "maxcubemaptexturesize": 8192,
                    "maxfragmentuniformvectors": 261,
                    "maxrenderbuffersize": 8192,
                    "maxtextureimageunits": 16,
                    "maxtexturesize": 8192,
                    "maxvaryingvectors": 32,
                    "maxvertexattribs": 32,
                    "maxvertextextureimageunits": 16,
                    "maxvertexuniformvectors": 256,
                    "maxviewportdims": "[8192,8192]",
                    "redbits": 8,
                    "renderer": "WebKitWebGL",
                    "shadinglanguageversion": "",
                    "stencilbits": 0,
                    "vendor": "WebKit",
                    "version": "WebGL1.0(OpenGLES2.0Chromium)",
                    "vertexshaderhighfloatprecision": 23,
                    "vertexshaderhighfloatprecisionrangeMin": 127,
                    "vertexshaderhighfloatprecisionrangeMax": 127,
                    "vertexshadermediumfloatprecision": 23,
                    "vertexshadermediumfloatprecisionrangeMin": 127,
                    "vertexshadermediumfloatprecisionrangeMax": 127,
                    "vertexshaderlowfloatprecision": 23,
                    "vertexshaderlowfloatprecisionrangeMin": 127,
                    "vertexshaderlowfloatprecisionrangeMax": 127,
                    "fragmentshaderhighfloatprecision": 23,
                    "fragmentshaderhighfloatprecisionrangeMin": 127,
                    "fragmentshaderhighfloatprecisionrangeMax": 127,
                    "fragmentshadermediumfloatprecision": 23,
                    "fragmentshadermediumfloatprecisionrangeMin": 127,
                    "fragmentshadermediumfloatprecisionrangeMax": 127,
                    "fragmentshaderlowfloatprecision": 23,
                    "fragmentshaderlowfloatprecisionrangeMin": 127,
                    "fragmentshaderlowfloatprecisionrangeMax": 127,
                    "vertexshaderhighintprecision": 0,
                    "vertexshaderhighintprecisionrangeMin": 31,
                    "vertexshaderhighintprecisionrangeMax": 30,
                    "vertexshadermediumintprecision": 0,
                    "vertexshadermediumintprecisionrangeMin": 31,
                    "vertexshadermediumintprecisionrangeMax": 30,
                    "vertexshaderlowintprecision": 0,
                    "vertexshaderlowintprecisionrangeMin": 31,
                    "vertexshaderlowintprecisionrangeMax": 30,
                    "fragmentshaderhighintprecision": 0,
                    "fragmentshaderhighintprecisionrangeMin": 31,
                    "fragmentshaderhighintprecisionrangeMax": 30,
                    "fragmentshadermediumintprecision": 0,
                    "fragmentshadermediumintprecisionrangeMin": 31,
                    "fragmentshadermediumintprecisionrangeMax": 30,
                    "fragmentshaderlowintprecision": 0,
                    "fragmentshaderlowintprecisionrangeMin": 31,
                    "fragmentshaderlowintprecisionrangeMax": 30,
                    "unmaskedvendor": "GoogleInc.",
                    "unmaskedrenderer": "GoogleSwiftShader"
                },
                "touch": {
                    "maxTouchPoints": 0,
                    "touchEvent": False,
                    "touchStart": False
                },
                "video": {
                    "ogg": "probably",
                    "h264": "probably",
                    "webm": "probably"
                },
                "audio": {
                    "ogg": "probably",
                    "mp3": "probably",
                    "wav": "probably",
                    "m4a": "maybe"
                },
                "vendor": "GoogleInc.",
                "product": "Gecko",
                "productSub": "20030107",
                "browser": {
                    "ie": False,
                    "chrome": True,
                    "webdriver": False
                },
                "window": {
                    "historyLength": 10,
                    "hardwareConcurrency": 8,
                    "iframe": False,
                    "battery": True
                },
                "location": {
                    "protocol": "https:"
                },
                "fonts": "",
                "devices": {
                    "count": 5,
                    "data": {
                        "0": {
                            "deviceId": "default",
                            "groupId": groupId,
                            "kind": "audioinput",
                            "label": ""
                        },
                        "1": {
                            "deviceId": get_random_str(),
                            "groupId": groupId,
                            "kind": "audioinput",
                            "label": ""
                        },
                        "2": {
                            "deviceId": get_random_str(),
                            "groupId": groupId2,
                            "kind": "videoinput",
                            "label": ""
                        },
                        "3": {
                            "deviceId": "default",
                            "groupId": groupId,
                            "kind": "audiooutput",
                            "label": ""
                        },
                        "4": {
                            "deviceId": get_random_str(),
                            "groupId": groupId,
                            "kind": "audiooutput",
                            "label": ""
                        }
                    }
                }
            },
            "cookies": 1,
            "setTimeout": 0,
            "setInterval": 0,
            "appName": "Netscape",
            "platform": "MacIntel",
            "syslang": "en-US",
            "userlang": "en-US",
            "cpu": "",
            "productSub": "20030107",
            "plugins": {
                "0": "ChromePDFPlugin",
                "1": "ChromePDFViewer",
                "2": "NativeClient"
            },
            "mimeTypes": {
                "0": "application/pdf",
                "1": "PortableDocumentFormatapplication/x-google-chrome-pdf",
                "2": "NativeClientExecutableapplication/x-nacl",
                "3": "PortableNativeClientExecutableapplication/x-pnacl"
            },
            "screen": {
                "width": 1920,
                "height": 1050,
                "colorDepth": 24
            },
            "fonts": {}
        }
        with open(self.base_path + '/PGxxx.js') as fp:
            js = fp.read()
            ctx = execjs.compile(js)
        p['proof'] = ctx.call('proof')
        data = {
            "p": json.dumps(p)
        }
        rst = self.session.request(method, url, headers=headers, params=params, data=data)
        if rst.status_code != 200:
            raise RequestError('获取 Cookie 失败: %s' % rst.status_code)

    def search(self):
        """步骤 6：带上 cookie 重新提交订票请求，获取航班搜索结果。"""
        booking_data = self.common_data['booking_data']
        url = self.common_data['booking_data']['url']
        method = "POST"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.user_agent,
        }
        data = {
            "LANGUAGE": booking_data['LANGUAGE'],
            "EMBEDDED_TRANSACTION": booking_data['EMBEDDED_TRANSACTION'],
            "SITE": booking_data['SITE'],
            "ENCT": booking_data['ENCT'],
            "ENC": booking_data['ENC'],
        }
        rst = self.session.request(method, url, headers=headers, data=data)
        if rst.status_code != 200:
            raise RequestError('search 请求失败: %s' % rst.status_code)
        self.common_data['html'] = rst.content.decode()

    def search_parse(self):
        """步骤 7：解析搜索结果，提取航班和价格信息。

        从 HTML 中正则提取 pageProvider 配置 JSON，
        解析出 proposedFlightsGroup（航班信息）和
        recommendationList（价格信息）。
        """
        patt = r'plnextv2.utils.pageProvider.PlnextPageProvider.init\({.*?config : (.*?), pageEngine : pageEngine'
        rst = re.findall(patt, self.common_data['html'], re.DOTALL)
        rst = rst[0]

        rst = json.loads(rst)

        proposedFlightsGroup = rst['pageDefinitionConfig']['pageData']['business']['Availability']['proposedBounds'][0][
            'proposedFlightsGroup']

        # 航班号、起飞时间、到达时间、飞行时间等
        print(proposedFlightsGroup)
        # 价格信息
        print(rst['pageDefinitionConfig']['pageData']['business']['Availability']['recommendationList'])


if __name__ == "__main__":
    params = {
        "TRIP_TYPE": "1",
        "OFFICE_ORIGIN": "TH",
        "OFFICE_DESTINATION": "TH",
        "FARE_TYPE": "",
        "DATA_TARGET": "1",
        "PROMO_ID": "",
        "PROMO_CODE": "",
        "CC_BIN": "",
        "B_LOCATION": "CNX",          # 出发机场代码
        "E_LOCATION": "BKK",          # 到达机场代码
        "B_DATE": "201912150000",     # 出发日期 (YYYYMMDDHHMM)
        "E_DATE": "",
        "ADULTS": "1",                # 成人数量
        "CHILDS": "0",                # 儿童数量
        "INFANTS": "0"                # 婴儿数量
    }
    b = Bangkokair(params)
    b.main()
