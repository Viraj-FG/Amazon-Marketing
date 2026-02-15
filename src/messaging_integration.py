# messaging_integration.py - Send product approvals via WhatsApp

from message import send_message

CHANNEL = "whatsapp"  # Example channel, can be replaced with actual config


def send_approval_request(products):
    """Send approval requests for a list of products via WhatsApp."""
    message_text = "--- Trending Products for Approval ---\n"
    for idx, product in enumerate(products, start=1):
        message_text += f"{idx}. {product}\n"
    message_text += "\nReply with ✅ for approval or ❌ to skip."

    # Simulate sending via WhatsApp (update 'to' with WhatsApp ID or group ID)
    send_message(channel=CHANNEL, to="user_id_or_group_id", message=message_text)
    return "Approval request sent."

if __name__ == "__main__":
    demo_products = ["Product Trend 1", "Product Trend 2", "Product Trend 3"]
    print(send_approval_request(demo_products))