import os
import re
import json
import execjs
import random
import requests


def get_random_str(length=64, chars='0123456789abcdef'):
    return ''.join(random.choice(chars) for _ in range(length))


class RequestError(Exception):
    pass


class Bangkokair():
    default_user_agent = "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)"

    def __init__(self, request_params, **kwargs):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.common_data = {
            'canvas_img': get_random_str(length=40),
            'webGL_img': get_random_str(length=40),
            'PG_JS_name': '',  # PGxxx文件名
            'PID': '',
            'booking_data': {},
            'html': '',
            'GMT_FORMAT': '%b %d, %Y %I:%M:%S %p',
        }
        # 初始化请求
        self.session = requests.session()
        self.session.proxies = kwargs.get('proxies', {})
        self.user_agent = kwargs.get('user_agent', self.default_user_agent)
        self.request_params = request_params

    def main(self):
        self.booking()
        self.get_pg_js_name()
        self.check_client()
        self.get_pid()
        self.get_cookies()
        self.search()
        self.search_parse()

    def booking(self):
        url = "https://www.bangkokair.com/AdTripFlow/booking"
        method = "POST"
        rst = self.session.request(method, url, data=self.request_params)
        if rst.status_code != 200:
            raise RequestError('booking请求失败:%s' % rst.status_code)
        self.common_data['booking_data'] = rst.json()

    def get_pg_js_name(self):
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
            raise RequestError('获取PGxxx.js请求失败:%s' % rst.status_code)
        patt = r'<script type="text/javascript" src="/(PG\w+.js)"'
        self.common_data['PG_JS_name'] = re.findall(patt, rst.text)[0]

    def check_client(self):
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
            raise RequestError('qlSUmvhsKL请求失败:%s' % rst.status_code)

    def get_pid(self):
        url = "https://flightbook.bangkokair.com/%s" % self.common_data['PG_JS_name']
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": self.user_agent,
        }
        rst = self.session.request("GET", url, headers=headers)
        if rst.status_code != 200:
            raise RequestError('PID获取失败:%s' % rst.status_code)
        # 解析PID
        patt = r'"/PG[a-z]+.js\?PID=([A-Z0-9-]+)"'
        self.common_data['PID'] = re.findall(patt, rst.text)[0]

    def get_cookies(self):
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
            raise RequestError('获取COOKIE失败:%s' % rst.status_code)

    def search(self):
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
            raise RequestError('search失败:%s' % rst.status_code)
        self.common_data['html'] = rst.content.decode()

    def search_parse(self):
        patt = r'plnextv2.utils.pageProvider.PlnextPageProvider.init\({.*?config : (.*?), pageEngine : pageEngine'
        rst = re.findall(patt, self.common_data['html'], re.DOTALL)
        rst = rst[0]

        rst = json.loads(rst)

        proposedFlightsGroup = rst['pageDefinitionConfig']['pageData']['business']['Availability']['proposedBounds'][0][
            'proposedFlightsGroup']

        # 航班号 起飞时间 到达时间 飞行时间 等
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
        "B_LOCATION": "CNX",  # 出发机场
        "E_LOCATION": "BKK",  # 到达机场
        "B_DATE": "201912150000",  # 出发日期
        "E_DATE": "",
        "ADULTS": "1",  # 成人数量
        "CHILDS": "0",  # 儿童数量
        "INFANTS": "0"
    }
    b = Bangkokair(params)
    b.main()
