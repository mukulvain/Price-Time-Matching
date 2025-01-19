class Order:
    def __init__(
        self,
        record,
        order_number,
        order_time,
        is_buy,
        activity_type,
        symbol,
        volume_disclosed,
        volume_original,
        limit_price,
        trigger_price,
        is_market_order,
        is_stop_loss,
        is_ioc,
        algo,
        client,
    ):
        self.activities = {1: "ENTRY", 3: "CANCEL", 4: "MODIFY"}
        self.record = record
        self.segment = "CASH"
        self.order_number = order_number
        self.order_time = order_time
        self.is_buy = is_buy
        self.activity_type = self.activities[activity_type]
        self.symbol = symbol
        self.series = "EQ"
        self.volume_disclosed = volume_disclosed
        self.volume_original = volume_original
        self.limit_price = limit_price
        self.trigger_price = trigger_price
        self.is_market_order = is_market_order
        self.is_stop_loss = is_stop_loss
        self.is_ioc = is_ioc
        self.algo = algo
        self.client = client

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}({self.order_number})"
