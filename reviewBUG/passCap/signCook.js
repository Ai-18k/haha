navigator= {
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    appName: "Netscape"
}
function get_ssion(id) {
    function u(e) {
            return null != e && "[object Object]" === Object.prototype.toString.call(e)
        }
    var l = function() {
        var e = (new Date).getTime();
        return function(t) {
            return Math.ceil((e = (9301 * e + 49297) % 233280) / 233280 * t)
        }
    }();
    function d() {
        if ("function" == typeof Uint32Array) {
            var e = "";
            if ("undefined" != typeof crypto ? e = crypto : "undefined" != typeof msCrypto && (e = msCrypto),
            0 && e.getRandomValues) {
                var t = new Uint32Array(1);
                return e.getRandomValues(t)[0] / Math.pow(2, 32)
            }
        }
        return l(1e19) / 1e19
    }
    var E = function() {
        var e = function() {
            for (var e = 1 * new Date, t = 0; e === 1 * new Date; )
                t++;
            return e.toString(16) + t.toString(16)
        };
        return function() {
            var t = String(768 * 1366);
            return t = t && /\d{5,}/.test(t) ? t.toString(16) : String(31242 * d()).replace(".", "").slice(0, 8),
            e() + "-" + d().toString(16).replace(".", "") + "-" + function() {
                var e, t, n = navigator.userAgent, r = [], o = 0;
                function i(e, t) {
                    var n, o = 0;
                    for (n = 0; n < t.length; n++)
                        o |= r[n] << 8 * n;
                    return e ^ o
                }
                for (e = 0; e < n.length; e++)
                    t = n.charCodeAt(e),
                    r.unshift(255 & t),
                    r.length >= 4 && (o = i(o, r),
                    r = []);
                return r.length > 0 && (o = i(o, r)),
                o.toString(16)
            }() + "-" + t + "-" + e() || (String(d()) + String(d()) + String(d())).slice(2, 15)
        }
    }();
    var device_id=E()
    // var device_id="18edbb6e4cc0-05669c56cee831-26031d51-1049088-18edbb6fcb00"
    arg=JSON.stringify({"$identity_cookie_id":device_id,"$identity_login_id":id})
    function j(e) {
    var t = "";
    try {
        t = btoa(encodeURIComponent(e).replace(/%([0-9A-F]{2})/g, function(e, t) {
            return String.fromCharCode("0x" + t)
        }))
    } catch (r) {
        t = e
    }
    return t
    }
    var identities=j(arg)
    return {"identities":identities,"device_id":device_id}
}

