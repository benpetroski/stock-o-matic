import yahoo_fin.stock_info as si
import yahoo_fin.options as ops

si.get_quote_table("aapl")

ops.get_calls('AAPL')

