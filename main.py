from Queue import Queue
from reader import order_repository, orders, trade_price

MARKET_OPENS_AT = 9.25


sell_book = Queue(False)
buy_book = Queue(True)
ineligible_orders = []
stack = []

# Adds orders to stack
def add_to_stack(order, is_buy=True):
    global stack
    while order.volume_original:
        # Current stack contains no order or similar orders
        if not len(stack) or stack[-1].is_buy == is_buy:
            stack.append(order)
            break
        # Top element of stack has higher volume than current order
        elif stack[-1].volume_original > order.volume_original:
            stack[-1].volume_original -= order.volume_original
            order.volume_original = 0
            del order_repository[order.order_number]
        # Removes top element of stack and reduces volume from current order
        else:
            order.volume_original -= stack[-1].volume_original
            del order_repository[stack[-1].order_number]
            stack.pop()


idx = 0
for order in orders:
    idx += 1
    order_number = order.order_number
    if order.order_time < MARKET_OPENS_AT:
        # Removes order
        if order.activity_type == "CANCEL":
            is_market_order = order.is_market_order
            if order.is_buy:
                buy_book.delete_PO(order_number, is_market_order)
            else:
                sell_book.delete_PO(order_number, is_market_order)
            del order_repository[order_number]
            continue

        # Removes order
        if order.activity_type == "MODIFY":
            previous_order = order_repository[order_number]
            is_market_order = previous_order.is_market_order

            if previous_order.is_buy:
                buy_book.delete_PO(order_number, is_market_order)
            else:
                sell_book.delete_PO(order_number, is_market_order)

        # Adds order
        if order.is_buy:
            buy_book.add_PO(order)
        else:
            sell_book.add_PO(order)
        order_repository[order_number] = order
    # Break out of the loop when PO time ends
    else:
        break

# Add eligible buy limit orders to stack
for key in buy_book.PO_limit_orders.keys():
    order = buy_book.PO_limit_orders[key]
    if order.limit_price < trade_price:
        ineligible_orders.append(order)
    else:
        add_to_stack(stack, order, True)

# Add eligible sell limit orders to stack
for key in sell_book.PO_limit_orders.keys():
    order = sell_book.PO_limit_orders[key]
    if order.limit_price > trade_price:
        ineligible_orders.append(order)
    else:
        add_to_stack(stack, order, False)

if not len(stack) or stack[-1].is_buy:
    # Add residual sell market orders to stack
    for key in sell_book.PO_market_orders.keys():
        order = sell_book.PO_market_orders[key]
        add_to_stack(stack, order, False)

    # Add residual buy market orders to stack
    for key in buy_book.PO_market_orders.keys():
        order = buy_book.PO_market_orders[key]
        add_to_stack(stack, order, True)
else:
    # Add residual buy market orders to stack
    for key in buy_book.PO_market_orders.keys():
        order = buy_book.PO_market_orders[key]
        add_to_stack(stack, order, True)

    # Add residual sell market orders to stack
    for key in sell_book.PO_market_orders.keys():
        order = sell_book.PO_market_orders[key]
        add_to_stack(stack, order, False)

# Since these orders are final, consider them as entry orders
for order in ineligible_orders + stack:
    order.activity_type = "ENTRY"


for order in ineligible_orders + stack:
    if order.is_buy:
        if order.is_market_order:
            buy_book.grab(order, sell_book)
        else:
            buy_book.add(order)
    else:
        if order.is_market_order:
            sell_book.grab(order, buy_book)
        else:
            sell_book.add(order)

for order in orders[idx - 1 :]:
    order_number = order.order_number
    # Removes order
    if order.activity_type == "CANCEL":
        if order.is_buy:
            buy_book.delete(order_number, order.is_stop_loss)
        else:
            sell_book.delete(order_number, order.is_stop_loss)
        continue

    # Removes order
    elif order.activity_type == "MODIFY":
        previous_order = order_repository[order_number]
        if previous_order.is_buy:
            buy_book.delete(order.order_number, order.is_stop_loss)
        else:
            sell_book.delete(order.order_number, order.is_stop_loss)

    # Adds order
    order_repository[order_number] = order
    if order.is_buy:
        if order.is_stop_loss:
            buy_book.add_trigger(order)
        else:
            buy_book.execute(order, sell_book)
    else:
        if order.is_stop_loss:
            sell_book.add_trigger(order)
        else:
            sell_book.execute(order, buy_book)
