"""
Email delivery service for MacroSnap.
Uses Python's standard smtplib and email packages to dispatch nutrition digests via Gmail SMTP SSL.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple


def send_email_digest(
    to_address: str,
    user_name: str,
    summary_text: str,
    gmail_address: str,
    gmail_app_password: str,
) -> Tuple[bool, str]:
    """
    Sends a nutrition summary digest to the specified recipient via Gmail SMTP SSL.

    Parameters:
        to_address: Recipient email address
        user_name: User's display name
        summary_text: AI-generated nutrition digest text
        gmail_address: Sender's Gmail address (from st.secrets)
        gmail_app_password: 16-character Google App Password (from st.secrets)

    Returns:
        (success: bool, message: str)
    """
    if not to_address or not to_address.strip():
        return False, "Recipient email address is missing."

    if not gmail_address or not gmail_app_password:
        return (
            False,
            "Gmail credentials not configured. Please add GMAIL_ADDRESS and GMAIL_APP_PASSWORD in secrets.toml.",
        )

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🥗 MacroSnap Daily Nutrition Digest for {user_name}"
        msg["From"] = f"MacroSnap AI <{gmail_address}>"
        msg["To"] = to_address.strip()

        # Plain-text version (fallback)
        plain_text = (
            f"Hey {user_name}!\n\n"
            f"Here is your MacroSnap Nutrition Summary for today:\n\n"
            f"{summary_text}\n\n"
            f"---\n"
            f"Logged with MacroSnap AI • Powered by Google Gemini\n"
        )
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))

        # Formatted HTML version for modern email clients
        formatted_html_summary = summary_text.replace("\n", "<br>")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      margin: 0;
      padding: 24px;
      color: #1e293b;
    }}
    .wrapper {{
      max-width: 600px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: #ffffff;
      padding: 32px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 6px 0 0;
      font-size: 14px;
      opacity: 0.95;
    }}
    .body-content {{
      padding: 28px 24px;
    }}
    .greeting {{
      font-size: 17px;
      font-weight: 600;
      margin-bottom: 12px;
    }}
    .card {{
      background-color: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 10px;
      padding: 20px;
      margin: 20px 0;
      font-size: 15px;
      line-height: 1.7;
      color: #166534;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 18px 24px;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      border-top: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>🥗 MacroSnap</h1>
      <p>Your Instant Calorie & Macro Intelligence Digest</p>
    </div>
    <div class="body-content">
      <div class="greeting">Hey {user_name}! 👋</div>
      <p>Here is your personalized meal and nutrition summary from today's conversation:</p>
      <div class="card">
        {formatted_html_summary}
      </div>
      <p style="font-size: 13px; color: #64748b; margin-top: 20px;">
        Tip: Consistency is key. Keep snapping your meals to stay on top of your daily nutritional targets!
      </p>
    </div>
    <div class="footer">
      Generated automatically by <strong>MacroSnap AI</strong> • Powered by Google Gemini 3.8 Flash
    </div>
  </div>
</body>
</html>
"""
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        clean_pwd = gmail_app_password.strip().replace(" ", "")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address.strip(), clean_pwd)
            server.send_message(msg)

        return True, "Digest sent directly to your email!"
    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "Gmail authentication failed. Please verify that your Gmail App Password is correct.",
        )
    except Exception as exc:
        return False, f"Email delivery failed: {str(exc)}"
