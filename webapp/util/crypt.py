# -*- coding: utf-8 -*-

import pyDes
import time
import random
import base64
import hashlib

from util import log
logger = log.LogService().getLogger()

APP_KEYS = {
    '100001': {'key': 'b2ad379df9486edbe80b5399b8f59902',
               'info': 'kuaizhan'},
    '100002': {}
}


def genAppkey(appid):
    salt = 'sohukz'
    return (hashlib
            .md5(APP_KEYS.get(appid, {}).get('key', '') + salt)
            .hexdigest()
            .decode('hex'))

# appkey = genAppkey(appid)


# Different APP has different key, configured in APP_KEYS
TOKEN_KEY = hashlib.md5('sohuec').hexdigest().decode('hex')
des = pyDes.triple_des(TOKEN_KEY, pyDes.ECB, None, None, pyDes.PAD_PKCS5)


def encrypt(key='', dynamic_token=True):
    # token = key + '@' + (dynamic_token and str(int(time.time() * 1000)))

    token = (
        key +
        '@' +
        (str(int(time.time() * 1000)) if dynamic_token else '')
    )
    return base64.b64encode(des.encrypt(token))


def decrypt(v, valid_span=None):
    # :param valid_span: in millisecond

    try:
        key, gen_time = des.decrypt(base64.b64decode(v)).split('@')[:2]

        if ((not valid_span) or
                abs(int(gen_time) - int(time.time() * 1000)) < valid_span):
            return key, gen_time
        else:
            return None, None
    except:
        return None, None


def sign(**kws):
    kws.pop('so_sig', None)
    appid = kws.get('appid', '')

    items = [
        '{0}={1}'.format(k, v.encode('utf-8'))
        for k, v in kws.iteritems()
    ]
    items.sort()
    sign_str = ''.join(items) + APP_KEYS.get(appid, {}).get('key', '')
    return hashlib.md5(sign_str).hexdigest()


if __name__ == '__main__':
    raw = '0'
    en = encrypt(raw)
    print repr(en)
    de = decrypt(en)
    print repr(de)
