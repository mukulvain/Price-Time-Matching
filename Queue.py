import math
from sortedcontainers import SortedDict
from reader import order_repository


class Queue:
    def __init__(self, buy=True):
        self.buy = buy
        # Mathematical cosmetic
        self.buy_var = 2 * buy - 1

        self.queue = SortedDict()
        self.orders = {}
        self.stop_loss_orders = {}

    def register_trade(self, active, passive, volume):
        print(active.order_number, passive.order_number, volume, passive.limit_price)

    # Updates the best price of the queue
    def fetch_price(self):
        if self.buy:
            self.current_price = self.queue.peekitem()[0]
        else:
            self.current_price = self.queue.peekitem(0)[0]

    # Adds pre open market order to appropriate dictionary
    def add_PO(self, order):
        self.orders[order.order_number] = order.limit_price
        if order.limit_price not in self.queue:
            self.queue[order.limit_price] = [order]
        else:
            self.queue[order.limit_price].append(order)

    # Removes pre open market order from appropriate dictionary
    def remove_PO(self, order_number, volume=0):
        if order_number in self.orders:
            price = self.orders[order_number]
            for i in range(len(self.queue[price])):
                if self.queue[price][i].order_number == order_number:
                    if not volume or self.queue[price][i].volume_original == volume:
                        self.queue[price].pop(i)
                        del self.orders[order_number]
                        del order_repository[order_number]
                    else:
                        self.queue[price][i].volume_original -= volume
                    break
            if not len(self.queue[price]):
                del self.queue[price]

    def add(self, order):
        # Adds order to the queue
        self.orders[order.order_number] = order.limit_price
        if order.limit_price not in self.queue:
            self.queue[order.limit_price] = [order]
        else:
            self.queue[order.limit_price].append(order)
        self.fetch_price()

    def grab(self, order, opp_book):
        global order_repository

        if order.is_market_order:
            # Matches and removes order from opposite order book
            while order.volume_original:
                # Best order from opposite order book has higher volume than current order
                if (
                    self.queue[self.current_price][0].volume_original
                    > order.volume_original
                ):
                    self.queue[self.current_price][
                        0
                    ].volume_original -= order.volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        order.volume_original,
                    )
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        self.queue[self.current_price][0].volume_original,
                    )

                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]

                    # Updates price of their best element
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]
                        self.fetch_price()
        elif order.is_ioc:
            while order.volume_original:
                # Best order from opposite order book has higher volume than current order
                if (
                    self.queue[self.current_price][0].volume_original
                    > order.volume_original
                ):
                    self.queue[self.current_price][
                        0
                    ].volume_original -= order.volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        order.volume_original,
                    )
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        self.queue[self.current_price][0].volume_original,
                    )
                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]

                    # Updates price of their best element
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]
                        self.fetch_price()

                        # Cancel order if still not satisfied
                        if (
                            self.buy_var * self.current_price
                            < self.buy_var * order.limit_price
                        ):
                            del order_repository[order.order_number]
                            break
        else:
            while order.volume_original:
                # Best order from opposite order book has higher volume than current order
                if (
                    self.queue[self.current_price][0].volume_original
                    > order.volume_original
                ):
                    self.queue[self.current_price][
                        0
                    ].volume_original -= order.volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        order.volume_original,
                    )
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original
                    self.register_trade(
                        order,
                        self.queue[self.current_price][0],
                        self.queue[self.current_price][0].volume_original,
                    )
                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]
                        self.fetch_price()

                        # If best price element becomes infeasible for current limit order, add limit order to order book
                        if (
                            self.buy_var * self.current_price
                            < self.buy_var * order.limit_price
                        ):
                            opp_book.add(order)
                            break

    def execute(self, order, opp_book):
        if order.is_stop_loss:
            if order.order_number in self.stop_loss_orders:
                del self.stop_loss_orders[order.order_number]
                order.is_stop_loss = False
                self.execute(order, opp_book)
            else:
                self.stop_loss_orders[order.order_number] = order

        # Adds order to limit order book
        elif (
            not order.is_market_order
            and not order.is_ioc
            and self.buy_var * order.limit_price < self.buy_var * opp_book.current_price
        ):
            self.add(order)

        # Removes order from the opposite limit order book
        else:
            opp_book.grab(order, self)

    def delete(self, order_number, is_stop_loss):
        if is_stop_loss:
            del self.stop_loss_orders[order_number]

        # Removes order from queue
        elif order_number in self.orders:
            price = self.orders[order_number]
            for i in range(len(self.queue[price])):
                if self.queue[price][i].order_number == order_number:
                    self.queue[price].pop(i)
                    del self.orders[order_number]
                    del order_repository[order_number]
                    break
            if not len(self.queue[price]):
                del self.queue[price]
            self.fetch_price()
