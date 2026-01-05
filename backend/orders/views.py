from products.models import Product  # 👈 add this import


@api_view(["POST"])
def create_order(request):
    data = request.data

    order = Order.objects.create(
        name=data["name"],
        phone=data["phone"],
        address=data["address"],
        total_amount=0,
    )

    total = 0

    for item in data["items"]:
        product = Product.objects.get(name=item["name"])  # 🔥 DB is source of truth
        qty = item["quantity"]

        OrderItem.objects.create(
            order=order,
            product_name=product.name,
            price=product.price,
            quantity=qty,
        )

        total += product.price * qty

    order.total_amount = total
    order.save()

    return Response({
        "success": True,
        "order_id": order.id
    })