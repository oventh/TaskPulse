"""Notification services — send alerts through configured channels."""

import json
import logging

from app.models.notification import NotificationChannel

logger = logging.getLogger("taskpulse.notification")


class NotificationService:
    """Dispatch alert messages through the appropriate channel provider."""

    async def send(self, channel: NotificationChannel, message: str):
        provider = self._get_provider(channel.channel_type)
        config = json.loads(channel.config) if isinstance(channel.config, str) else channel.config
        await provider(config, message)

    def _get_provider(self, channel_type: str):
        providers = {
            "feishu_cli": self._send_feishu,
            "email": self._send_email,
            "webhook": self._send_webhook,
        }
        provider = providers.get(channel_type)
        if not provider:
            raise ValueError(f"Unsupported channel type: {channel_type}")
        return provider

    async def _send_feishu(self, config: dict, message: str):
        """Send via Feishu webhook (supports both CLI-style and webhook)."""
        import httpx

        webhook_url = config.get("webhook_url", "")
        if not webhook_url:
            logger.warning("Feishu webhook URL not configured")
            return

        payload = {
            "msg_type": "text",
            "content": {"text": message},
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
            logger.info("Feishu notification sent: %s", resp.status_code)

    async def _send_email(self, config: dict, message: str):
        """Send via SMTP."""
        import smtplib
        from email.mime.text import MIMEText

        smtp_host = config.get("smtp_host", "")
        smtp_port = config.get("smtp_port", 587)
        smtp_user = config.get("smtp_user", "")
        smtp_pass = config.get("smtp_password", "")
        to_addr = config.get("to_address", "")
        from_addr = config.get("from_address", smtp_user)

        if not all([smtp_host, smtp_user, smtp_pass, to_addr]):
            logger.warning("Email config incomplete, skipping")
            return

        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = "[TaskPulse] 定时任务告警"
        msg["From"] = from_addr
        msg["To"] = to_addr

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            logger.info("Email notification sent to %s", to_addr)

    async def _send_webhook(self, config: dict, message: str):
        """Send via generic webhook."""
        import httpx

        url = config.get("url", "")
        if not url:
            logger.warning("Webhook URL not configured")
            return

        payload = {"text": message, "source": "taskpulse"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Webhook notification sent: %s", resp.status_code)
