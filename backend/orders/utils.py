import urllib.parse

def build_whatsapp_message(order):
    lines = [
        f"Hello {order.name} 👋",
        "",
        f"Your order #{order.id} has been placed successfully.",
        "",
        "Order details:",
    ]

    for item in order.items.all():
        lines.append(f"- {item.product_name} × {item.quantity}")

    lines.extend([
        "",
        f"Total Amount: ₹{order.total_amount}",
        "",
        "Thank you for ordering with us 🙏",
    ])

    message = "\n".join(lines)
    return urllib.parse.quote(message)