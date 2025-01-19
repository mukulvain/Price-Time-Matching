import pandas as pd
from Order import Order

orders_file = "OrderFile_bbbbbbINFY.csv"
orders_df = pd.read_csv(orders_file)
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

trade_price = 78520