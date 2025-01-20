from Queue import Queue
from reader import order_repository, orders, trade_price, trades

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
    if order.order_time > MARKET_OPENS_AT:
        break
    if order_number in order_repository:
        # Removes order
        if order.activity_type == "CANCEL":
            if order.is_buy:
                buy_book.remove_PO(order_number)
            else:
                sell_book.remove_PO(order_number)
            continue

        # Removes order
        if order.activity_type == "MODIFY":
            previous_order = order_repository[order_number]
            if previous_order.is_buy:
                buy_book.remove_PO(order_number)
            else:
                sell_book.remove_PO(order_number)

    # Adds order
    if order.is_market_order:
        continue

    if order.is_buy:
        buy_book.add_PO(order)
    else:
        sell_book.add_PO(order)
    order_repository[order_number] = order


for trade in trades:
    if trade.trade_time > MARKET_OPENS_AT:
        break
    volume = trade.trade_quantity
    buyer = trade.buy_order_number
    seller = trade.sell_order_number

    buy_book.remove_PO(buyer, volume)
    sell_book.remove_PO(seller, volume)

buy_book.fetch_price()
sell_book.fetch_price()

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
        buy_book.execute(order, sell_book)
    else:
        sell_book.execute(order, buy_book)
