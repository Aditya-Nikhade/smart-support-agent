from langchain_core.tools import tool

@tool
def check_order_status(order_id: str) -> str:
    """Looks up the status of an order given a unique order ID. Use this for any questions about a specific order."""
    print(f"--- TOOL: Checking status for order {order_id} ---")
    if order_id == "12345":
        return "Your order 12345 is out for delivery and should arrive tomorrow."
    elif order_id == "67890":
        return "Your order 67890 was delivered two days ago."
    else:
        return f"I couldn't find any information for order ID {order_id}. Please double-check the ID."