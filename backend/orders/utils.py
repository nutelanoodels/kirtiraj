from urllib.parse import quote

def build_customer_whatsapp_message(order):
    lines = []
    lines.append("🧾 *Order Confirmation*")
    lines.append("")
    lines.append(f"Order ID: {order.id}")
    lines.append(f"Name: {order.name}")
    lines.append(f"Phone: {order.phone}")
    lines.append("")
    lines.append("*Items:*")

    total = 0
    for item in order.items.all():
        line_total = item.price * item.quantity
        total += line_total
        lines.append(
            f"- {item.product_name} × {item.quantity} = ₹{line_total:.2f}"
        )

    lines.append("")
    lines.append(f"*Total Amount: ₹{total:.2f}*")
    lines.append("")
    lines.append("Thank you for ordering with *Kirtiraj* 🙏")

    message = "\n".join(lines)
    return quote(message)