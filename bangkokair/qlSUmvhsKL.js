var getRandomStringWithEntropy = function (e) {
    e = Math["ceil"](e / 6)
    for (var t = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz", r = "", n = 0; e > n; ++n)
        r += t.substr(Math.floor(Math.random() * t.length), 1);
    return r
};

function n(e, x) {
    for (var t, a = 0, r = 0; r < e["length"]; r++)
        if (t = e["charCodeAt"](r),
            128 > t) {
            var o = x.charCodeAt(r % x["length"]);
            a = (a + 2089 * (t ^ o)) % 65535
        }
    return a
}

function i(e, x) {
    if (typeof e === "string")
        return e;
    if (typeof e === "number")
        return Math["round"](e)["toString"]();
    if ('boolean' == typeof e)
        return e["toString"]();
    if (null === e || void 0 === e)
        return 'null';
    if ('[object Array]' === Object["prototype"]["toString"]["call"](e))
        return '[' + e["map"](function (e) {
            return i(e, x)
        })["join"](',') + ']';
    if (typeof e["toJSON"] === "function")
        return i(e["toJSON"](), x);
    var t = Object.keys(e)["map"](function (e) {
        return {
            'key': e,
            'order': n(e, x)
        }
    });
    return t["sort"](function (e, x) {
        var t = e["order"] - x["order"];
        return 0 == t ? e["key"] >= x.key ? 1 : -1 : t
    }),
        '{' + t["map"](function (t) {
            var a = t.key
                , r = e[a]
                , o = i(r, x);
            return a + ':' + o
        })["join"](',') + '}'
}

var x = {};
x.f = function(e, x, t, a) {
    return 0 === e ? x & t ^ ~x & a : 1 === e ? x ^ t ^ a : 2 === e ? x & t ^ x & a ^ t & a : 3 === e ? x ^ t ^ a : void 0
}
,
x["ROTL"] = function(e, x) {
    return e << x | e >>> 32 - x
}
,
x["toHexStr"] = function(e) {
    for (var x, t = '', a = 7; 0 <= a; a--)
        x = 15 & e >>> 4 * a,
        t += x["toString"](16);
    return t
}

var auth = function (e) {
    e = unescape(encodeURIComponent(e));
    var t = [1518500249, 1859775393, 2400959708, 3395469782];
    e += String["fromCharCode"](128);
    for (var a = e["length"] / 4 + 2, r = Math["ceil"](a / 16), o = Array(r), n = 0; n < r; n++) {
        o[n] = Array(16);
        for (var i = 0; 16 > i; i++)
            o[n][i] = e.charCodeAt(64 * n + 4 * i) << 24 | e["charCodeAt"](64 * n + 4 * i + 1) << 16 | e.charCodeAt(64 * n + 4 * i + 2) << 8 | e["charCodeAt"](64 * n + 4 * i + 3)
    }
    o[r - 1][14] = 8 * (e["length"] - 1) / Math.pow(2, 32),
        o[r - 1][14] = Math["floor"](o[r - 1][14]),
        o[r - 1][15] = 4294967295 & 8 * (e.length - 1);
    for (var d, s, c, b, l, f = 1732584193, u = 4023233417, p = 2562383102, g = 271733878, h = 3285377520, m = Array(80), n = 0; n < r; n++) {
        for (var _ = 0; 16 > _; _++)
            m[_] = o[n][_];
        for (var _ = 16; 80 > _; _++)
            m[_] = x["ROTL"](m[_ - 3] ^ m[_ - 8] ^ m[_ - 14] ^ m[_ - 16], 1);
        d = f,
            s = u,
            c = p,
            b = g,
            l = h;
        for (var _ = 0; 80 > _; _++) {
            var y = Math.floor(_ / 20)
                , T = 4294967295 & x["ROTL"](d, 5) + x.f(y, s, c, b) + l + t[y] + m[_];
            l = b,
                b = c,
                c = x["ROTL"](s, 30),
                s = d,
                d = T
        }
        f = 4294967295 & f + d,
            u = 4294967295 & u + s,
            p = 4294967295 & p + c,
            g = 4294967295 & g + b,
            h = 4294967295 & h + l
    }
    return x["toHexStr"](f) + x["toHexStr"](u) + x.toHexStr(p) + x["toHexStr"](g) + x["toHexStr"](h)
}

var hashJsonPredictably = function (browser, x) {
    return auth(i(browser, x))
};

function mine(e, x) {
    for (var t = 0; ; t++) {
        var r = t["toString"](16)
            , o = r + ':' + e
            , n = auth(o);
        var i = parseInt(n["substr"](0, 8), 16);
        if (i < 1 << 32 - x)
            return o
    }
}

var proof = function (interrogation) {
    return randomStr = getRandomStringWithEntropy(128),
        nowMicrotime = new Date()["getTime"](),
        r = randomStr + ':' + nowMicrotime,
        o = hashJsonPredictably(interrogation, r),
        n = r + ':' + o,
        mine(n, 8);
}
