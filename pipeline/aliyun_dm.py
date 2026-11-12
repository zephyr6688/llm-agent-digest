"""阿里云邮件推送（DirectMail）发信：RPC 签名 + SingleSendMail（仅标准库）。

环境变量：
  ALIYUN_ACCESS_KEY_ID      RAM AccessKey
  ALIYUN_ACCESS_KEY_SECRET  RAM Secret
发信地址（AccountName）由调用方传入，需先在阿里云邮件推送控制台创建并验证。

参考：https://help.aliyun.com/zh/direct-mail/api-dm-2015-11-23-overview
"""
import base64
import datetime
import hashlib
import hmac
import json
import urllib.parse
import urllib.request
import uuid

ENDPOINT = "https://dm.aliyuncs.com/"
VERSION = "2015-11-23"


def _rfc3986(s) -> str:
    return urllib.parse.quote(str(s), safe="-_.~")


def _percent_params(params: dict) -> str:
    return "&".join(f"{_rfc3986(k)}={_rfc3986(v)}" for k, v in params.items())


def sign(params: dict, access_key_secret: str) -> str:
    """阿里云 RPC 风格 HMAC-SHA1 签名。"""
    canonical = "&".join(
        f"{_rfc3986(k)}={_rfc3986(v)}" for k, v in sorted(params.items())
    )
    string_to_sign = "POST&" + _rfc3986("/") + "&" + _rfc3986(canonical)
    digest = hmac.new(
        (access_key_secret + "&").encode(), string_to_sign.encode(), hashlib.sha1
    ).digest()
    return base64.b64encode(digest).decode()


def send_mail(to: str, subject: str, html_body: str, from_addr: str,
              access_key_id: str, access_key_secret: str, reply_to: bool = True):
    """发送单封邮件，返回阿里云 JSON 响应（dict）。"""
    params = {
        "Action": "SingleSendMail",
        "AccountName": from_addr,
        "AddressType": "1",
        "ReplyToAddress": "true" if reply_to else "false",
        "ToAddress": to,
        "Subject": subject,
        "HtmlBody": html_body,
        "Version": VERSION,
        "Format": "JSON",
        "AccessKeyId": access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": uuid.uuid4().hex,
        "Timestamp": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    params["Signature"] = sign(params, access_key_secret)
    data = _percent_params(params).encode()
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())
