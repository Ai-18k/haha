var CryptoJS = require('crypto-js')

function get_jsl(_0x15dfa1) {
        function hash(_0x4c85ed) {
        if (_0x15dfa1.ha=="sha1"){
          return CryptoJS.SHA1(_0x4c85ed).toString();
        }else if(_0x15dfa1.ha=="md5")
        {
            return CryptoJS.MD5(_0x4c85ed).toString();
        }else{
            return CryptoJS.SHA256(_0x4c85ed).toString();
        }
    }
        var _0x313a8c = new Date();
        function _0x2decb6(_0xf89e76, _0x173eda) {
                var _0x2cedff = _0x15dfa1["chars"]["length"];

                for (var _0x1b9a29 = 0; _0x1b9a29 < _0x2cedff; _0x1b9a29++) {
                for (var _0x571a24 = 0; _0x571a24 < _0x2cedff; _0x571a24++) {
                var _0x4c85ed = _0x173eda[0] + _0x15dfa1["chars"]["substr"](_0x1b9a29, 1) + _0x15dfa1["chars"]["substr"](_0x571a24, 1) + _0x173eda[1];

                if (hash(_0x4c85ed) == _0xf89e76) {
                  return [_0x4c85ed, new Date() - _0x313a8c];
        }
      }
    }
  }
        var _0x3f42e2 = _0x2decb6(_0x15dfa1['ct'], _0x15dfa1["bts"])
        return _0x3f42e2
}

par={'bts': ['1712492394.523|0|dO5', 'fJ%2F4kDOTLZ9Wx226zwDqa4%3D'], 'chars': 'uBVomApBrrugIIWAaiItQR', 'ct': 'cf382d974114ed8b8e167e55b84a421d', 'ha': 'md5', 'is': true, 'tn': '__jsl_clearance_s', 'vt': '3600', 'wt': '1500'}

console.log(get_jsl(par));













