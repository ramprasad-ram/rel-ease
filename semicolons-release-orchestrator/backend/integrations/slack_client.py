"""
Slack integration for sending notifications.
Supports webhook-based messaging for deployment events.
"""
import aiohttp
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackClient:
    """Client for sending messages to Slack via webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack client.
        
        Args:
            webhook_url: Slack webhook URL for posting messages
        """
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
        
        if not self.enabled:
            logger.warning("Slack webhook URL not configured. Notifications will be logged only.")
    
    async def send_message(
        self,
        text: str,
        blocks: Optional[list] = None,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send a message to Slack.
        
        Args:
            text: Plain text message (fallback)
            blocks: Rich message blocks (optional)
            channel: Override default channel (optional)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"[SLACK DISABLED] Would send: {text}")
            return False
        
        payload: Dict[str, Any] = {"text": text}
        
        if blocks:
            payload["blocks"] = blocks
        
        if channel:
            payload["channel"] = channel
        
        try:
            if not self.webhook_url:
                logger.error("Slack webhook URL is not configured")
                return False
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Slack message sent successfully: {text[:50]}...")
                        return True
                    else:
                        logger.error(f"Slack API error: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False
    
    async def send_rollback_alert(
        self,
        service_name: str,
        current_version: str,
        rollback_version: str,
        error_details: str,
        deployment_id: str
    ) -> bool:
        """
        Send a formatted rollback alert to Slack.
        
        Args:
            service_name: Name of the service being rolled back
            current_version: Version that failed
            rollback_version: Version to rollback to
            error_details: Description of the error
            deployment_id: Deployment identifier
            
        Returns:
            True if alert sent successfully
        """
        text = (
            f"🚨 *Rollback Initiated*\n"
            f"Error detected in '{service_name}'. Reverting to v{rollback_version}."
        )
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Automatic Rollback Initiated",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed Version:*\nv{current_version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Rollback To:*\nv{rollback_version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Deployment ID:*\n`{deployment_id}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Details:*\n```{error_details}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    }
                ]
            }
        ]
        
        return await self.send_message(text=text, blocks=blocks)
    
    async def send_deployment_success(
        self,
        service_name: str,
        version: str,
        deployment_id: str,
        duration_seconds: int
    ) -> bool:
        """
        Send a deployment success notification.
        
        Args:
            service_name: Name of the deployed service
            version: Deployed version
            deployment_id: Deployment identifier
            duration_seconds: Deployment duration
            
        Returns:
            True if notification sent successfully
        """
        text = f"✅ Deployment successful: {service_name} v{version}"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ Deployment Successful",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Version:*\nv{version}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{duration_seconds}s"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Deployment ID:*\n`{deployment_id}`"
                    }
                ]
            }
        ]
        
        return await self.send_message(text=text, blocks=blocks)
    
    async def send_error_spike_detected(
        self,
        service_name: str,
        error_rate: float,
        threshold: float,
        deployment_id: str
    ) -> bool:
        """
        Send an error spike detection alert.
        
        Args:
            service_name: Name of the service
            error_rate: Current error rate (0-1)
            threshold: Threshold that was exceeded
            deployment_id: Related deployment ID
            
        Returns:
            True if alert sent successfully
        """
        text = f"⚠️ Error spike detected in {service_name}: {error_rate:.1%} (threshold: {threshold:.1%})"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ Error Spike Detected",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Error Rate:*\n{error_rate:.1%}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Threshold:*\n{threshold:.1%}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Deployment ID:*\n`{deployment_id}`"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🤖 *Rollback Agent is analyzing the situation...*"
                }
            }
        ]
        
        return await self.send_message(text=text, blocks=blocks)

# Made with Bob
