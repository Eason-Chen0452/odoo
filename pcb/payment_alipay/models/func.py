# -*- coding: utf-8 -*-

import json
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA, SHA256
from base64 import encodestring as encodebytes, decodestring as decodebytes
from urllib import quote_plus


# 请求时 进行签名
def sign_data(data, private_key, sign_type, check=False):
    data.pop("sign", None)
    # 排序后的字符串
    ordered_items = _ordered_data(data)
    unsigned_string = "&".join("{}={}".format(k, v) for k, v in ordered_items)
    sign = _sign(unsigned_string, private_key, sign_type)
    if check:
        quoted_string = "&".join("{}={}".format(k, quote_plus(str(v))) for k, v in ordered_items)
        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string
    return str(sign)


# 整理成一个个元组
def _ordered_data(data):
    complex_keys = [k for k, v in data.items() if isinstance(v, dict)]
    # 将字典类型的数据dump出来
    for key in complex_keys:
        data[key] = json.dumps(data[key], separators=(',', ':'))
    return sorted([(k, v) for k, v in data.items()])


def _sign(unsigned_string, private_key, sign_type):
    """
    通过如下方法调试签名
    方法1
        key = rsa.PrivateKey.load_pkcs1(open(self._app_private_key_path).read())
        sign = rsa.sign(unsigned_string.encode("utf8"), key, "SHA-1")
        # base64 编码，转换为unicode表示并移除回车
        sign = base64.encodebytes(sign).decode("utf8").replace("\n", "")
    方法2
        key = RSA.importKey(open(self._app_private_key_path).read())
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA.new(unsigned_string.encode("utf8")))
        # base64 编码，转换为unicode表示并移除回车
        sign = base64.encodebytes(signature).decode("utf8").replace("\n", "")
    方法3
        echo "abc" | openssl sha1 -sign alipay.key | openssl base64

    """
    # 开始计算签名
    private_key = '-----BEGIN RSA PRIVATE KEY-----' + '\n' + str(private_key) + '\n' + '-----END RSA PRIVATE KEY-----'
    key = RSA.importKey(private_key)
    signer = PKCS1_v1_5.new(key)
    if sign_type == "RSA":
        signature = signer.sign(SHA.new(unsigned_string))
    else:
        signature = signer.sign(SHA256.new(unsigned_string))
    # base64 编码，转换为unicode表示并移除回车
    sign = encodebytes(signature).decode("utf8").replace("\n", "")
    return sign


# 返回的响应
def _verify(data, sign, public_key, sign_type):
    # 开始计算签名
    public_key = '-----BEGIN PUBLIC KEY-----' + '\n' + str(public_key) + '\n' + '-----END PUBLIC KEY-----'
    key = RSA.importKey(public_key)
    signer = PKCS1_v1_5.new(key)
    if sign_type == "RSA":
        digest = SHA.new()
    else:
        digest = SHA256.new()
    digest.update(data.encode("utf8"))
    if signer.verify(digest, decodebytes(sign.encode("utf8"))):
        return True
    return False


def verify(data, sign_type):
    if "sign_type" in data:
        if data.get('sign_type') != sign_type:
            raise Exception(None, "Unknown sign type: {}".format(data.get('sign_type')))
        else:
            data.pop('sign_type')
    # 排序后的字符串
    unsigned_items = _ordered_data(data)
    message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
    return message


# 验证签名
def VerifySign(data, sign, public_key, sign_type):
    data.pop('sign')
    message = verify(data, sign_type)
    message = _verify(str(message), str(sign), str(public_key), str(sign_type))
    return message

