import pandas as pd
from Order import Order
from Trade import Trade

orders_file = "OrderFile_bbbbbbINFY.csv"
trades_file = "TradeFile_bbbbbbINFY.csv"
orders_df = pd.read_csv(orders_file)
trades_df = pd.read_csv(trades_file)

order_repository = {}

orders = [
    Order(
        row.Record_ind,
        row.order_no,
        row.time,
        row.buysell == "B",
        row.activity_typ,
        row.symbol,
        row.vol_discl,
        row.vol_orgnl,
        row.limit_prc,
        row.trig_prc,
        row.mkt_ord_flg == "Y",
        row.stp_loss_flg == "Y",
        row.ioc_flg == "Y",
        row.algo_ind,
        row.client_flg,
    )
    for row in orders_df.itertuples(index=False)
]

trades = [
    Trade(
        row.Record_ind,
        row.trade_no,
        row.time,
        row.symbol,
        row.trd_prc,
        row.trd_q,
        row.buy_order_no,
        row.buy_algo_ind,
        row.buy_client_flg,
        row.sell_order_no,
        row.sell_algo_ind,
        row.sell_client_flg,
    )
    for row in trades_df.itertuples(index=False)
]

trade_price = trades_df["trd_prc"].iloc[0]
