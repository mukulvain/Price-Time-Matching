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

        self.PO_limit_orders = {}
        self.PO_market_orders = {}

        self.trigger_orders = {}
        self.trigger_queue = SortedDict()

    # Adds pre open market order to appropriate dictionary
    def add_PO(self, order):
        if order.is_market_order:
            self.PO_market_orders[order.order_number] = order
        else:
            self.PO_limit_orders[order.order_number] = order

    # Removes pre open market order from appropriate dictionary
    def delete_PO(self, order_number, is_market_order):
        if is_market_order:
            del self.PO_market_orders[order_number]
        else:
            del self.PO_limit_orders[order_number]

    def add(self, order):
        # Adds order to the queue
        self.orders[order.order_number] = order.limit_price
        if order.limit_price not in self.queue:
            self.queue[order.limit_price] = [order]
        else:
            self.queue[order.limit_price].append(order)
        # Updates the best price of the queue
        if self.buy:
            self.current_price = self.queue.peekitem()[0]
        else:
            self.current_price = self.queue.peekitem(0)[0]

    def add_trigger(self, order):
        # Adds stop loss orders to trigger queue
        self.trigger_orders[order.order_number] = order.trigger_price
        if order.trigger_price not in self.trigger_queue:
            self.trigger_queue[order.trigger_price] = [order]
        else:
            self.trigger_queue[order.trigger_price].append(order)
        # Udates trigger price
        if self.buy:
            self.trigger_price = self.trigger_queue.peekitem()[0]
        else:
            self.trigger_price = self.trigger_queue.peekitem(0)[0]

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
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original

                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]

                    # Updates price of their best element
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]
                        if self.buy:
                            self.current_price = self.queue.peekitem()[0]
                        else:
                            self.current_price = self.queue.peekitem(0)[0]
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
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original

                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]

                    # Updates price of their best element
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]
                        if self.buy:
                            self.current_price = self.queue.peekitem()[0]
                        else:
                            self.current_price = self.queue.peekitem(0)[0]

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
                    order.volume_original = 0
                    del order_repository[order.order_number]

                # Removes best element and reduces volume from current order
                else:
                    order_number = self.queue[self.current_price][0].order_number
                    order.volume_original -= self.queue[self.current_price][
                        0
                    ].volume_original
                    self.queue[self.current_price].pop(0)
                    del self.orders[order_number]
                    del order_repository[order_number]
                    if not len(self.queue[self.current_price]):
                        del self.queue[self.current_price]

                        # Updates price of their best element
                        if self.buy:
                            self.current_price = self.queue.peekitem()[0]
                        else:
                            self.current_price = self.queue.peekitem(0)[0]

                        # If best price element becomes infeasible for current limit order, add limit order to order book
                        if (
                            self.buy_var * self.current_price
                            < self.buy_var * order.limit_price
                        ):
                            opp_book.add(order)
                            break

    def trigger(self, opp_book):
        if len(self.trigger_queue):
            while (
                self.buy_var * self.trigger_price
                <= self.buy_var * opp_book.current_price
            ):
                # If triggered, removes the order from trigger queue
                price = self.trigger_price
                order = self.trigger_queue[price][0]
                order.is_stop_loss = False
                order.activity_type = "ENTRY"
                self.trigger_queue[price].pop(0)
                del self.trigger_orders[order.order_number]

                if not len(self.trigger_queue[price]):
                    del self.trigger_queue[price]

                # If the queue becomes empty, trigger price is pushed to extremes
                if not len(self.trigger_queue):
                    if self.buy:
                        self.trigger_price = math.inf
                    else:
                        self.trigger_price = 0
                # Updates trigger price
                else:
                    if self.buy:
                        self.trigger_price = self.trigger_queue.peekitem()[0]
                    else:
                        self.trigger_price = self.trigger_queue.peekitem(0)[0]
                # Places the order in order book
                self.execute(order, opp_book)

    def execute(self, order, opp_book):
        # Adds order to limit order book and triggers the stop loss order of opposite order book
        if (
            not order.is_market_order
            and not order.is_ioc
            and self.buy_var * order.limit_price < self.buy_var * opp_book.current_price
        ):
            self.add(order)
            opp_book.trigger(self)

        # Removes order from the opposite limit order book
        else:
            opp_book.grab(order, self)

    def delete(self, order_number, is_stop_loss):
        if is_stop_loss:
            # Removes stop loss order from trigger queue
            if order_number in self.trigger_orders:
                price = self.trigger_orders[order_number]
                for i in range(len(self.trigger_queue[price])):
                    if self.trigger_queue[price][i].order_number == order_number:
                        self.trigger_queue[price].pop(i)
                        del self.trigger_orders[order_number]
                        del order_repository[order_number]
                        break
                if not len(self.trigger_queue[price]):
                    del self.trigger_queue[price]
                if self.trigger_price == price:
                    # If the queue becomes empty, trigger price is pushed to extremes
                    if not len(self.trigger_queue):
                        if self.buy:
                            self.trigger_price = math.inf
                        else:
                            self.trigger_price = 0
                    # Otherwise, the trigger price is updated
                    else:
                        if self.buy:
                            self.trigger_price = self.trigger_queue.peekitem()[0]
                        else:
                            self.trigger_price = self.trigger_queue.peekitem(0)[0]

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
            # Updates current price
            if self.current_price == price:
                if self.buy:
                    self.current_price = self.queue.peekitem()[0]
                else:
                    self.current_price = self.queue.peekitem(0)[0]
