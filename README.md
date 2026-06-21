# QoderWork Cloud Cron

从 QoderWork 本地定时任务迁移到 GitHub Actions 的云端提醒服务。
关机也能收到推送，通过飞书 Webhook 发送到手机端。

## 已迁移的任务

| 任务 | 时间 | 说明 |
|------|------|------|
| 催还款-谦润 | 每月12号 12:00 | 纯文本推送 |
| 催还款-胡隽 | 每月19号 19:00 | 纯文本推送 |
| 工作日外卖提醒 | 每天10:30 | 自动判断中国工作日 |
| 每日天气推送 | 每天08:00 | 查询上海天气 |

## 依赖

- 飞书群机器人 Webhook（带签名密钥）
- GitHub Secrets: `FEISHU_WEBHOOK_URL`, `FEISHU_WEBHOOK_SECRET`

## 本地测试

```bash
# 天气（不推送）
python scripts/get_weather.py 上海 --dry-run

# 工作日判断
python scripts/check_workday.py

# 完整推送测试
export FEISHU_WEBHOOK_URL="your-webhook-url"
export FEISHU_WEBHOOK_SECRET="your-secret"
python scripts/get_weather.py 上海
```
