"""
飞书 Webhook 推送模块
支持纯文本和富文本卡片，带签名验证
"""
import hmac
import hashlib
import base64
import time
import json
import urllib.request
import os


def gen_sign(secret):
    """生成飞书 Webhook 签名"""
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return timestamp, sign


def send_text(text, webhook_url=None, secret=None):
    """发送纯文本消息"""
    webhook_url = webhook_url or os.environ.get("FEISHU_WEBHOOK_URL", "")
    secret = secret or os.environ.get("FEISHU_WEBHOOK_SECRET", "")

    timestamp, sign = gen_sign(secret)
    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {"text": text},
    }
    return _post(webhook_url, payload)


def send_card(title, content_md, webhook_url=None, secret=None, template="blue"):
    """
    发送飞书消息卡片
    title: 卡片标题
    content_md: 正文内容（支持飞书 Markdown）
    template: 颜色主题 (blue/green/red/orange/purple/indigo)
    """
    webhook_url = webhook_url or os.environ.get("FEISHU_WEBHOOK_URL", "")
    secret = secret or os.environ.get("FEISHU_WEBHOOK_SECRET", "")

    timestamp, sign = gen_sign(secret)
    payload = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content_md},
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"via QoderWork Cloud Cron · {time.strftime('%Y-%m-%d %H:%M')}",
                        }
                    ],
                },
            ],
        },
    }
    return _post(webhook_url, payload)


def _post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))
