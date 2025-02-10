import logging
import smtplib
from email.mime.text import MIMEText
from config import Config

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self):
        self.email_config = {
            'smtp_server': Config.SMTP_SERVER,
            'smtp_port': Config.SMTP_PORT,
            'email': Config.EMAIL,
            'password': Config.EMAIL_PASSWORD,
            'recipients': Config.ALERT_RECIPIENTS
        }

    def send_alert(self, message):
        """发送紧急警报"""
        subject = "Arbitrage Bot Alert"
        self._send_email(subject, message)

    def send_trade_report(self, trade_result):
        """发送交易报告"""
        subject = "Arbitrage Trade Report"
        message = f"""
        Trade Details:
        - Sell Exchange: {trade_result['sell_exchange']}
        - Sell Price: {trade_result['sell_price']}
        - Buy Exchange: {trade_result['buy_exchange']}
        - Buy Price: {trade_result['buy_price']}
        - Quantity: {trade_result['quantity']}
        - Slippage: {trade_result['slippage']:.2f}
        - Estimated Profit: {trade_result['profit']:.2f} USDT
        """
        self._send_email(subject, message)

    def _send_email(self, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email_config['email']
            msg['To'] = ', '.join(self.email_config['recipients'])

            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['email'], self.email_config['password'])
                server.sendmail(self.email_config['email'], self.email_config['recipients'], msg.as_string())
            logger.info("Alert email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
