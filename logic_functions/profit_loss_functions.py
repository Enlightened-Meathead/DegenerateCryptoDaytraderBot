## Functions that calculate profit or loss and reallocates assets once a trade is made
import asyncio
import logic_functions.scan_functions as scf


# Little function that return the profit or loss percentage in decimal form, ie 10% == 0.10
async def profit_loss_percent(asset, bought_price):
    websocket = await scf.connect_websocket()
    profit_percent = float(await scf.current_percent_difference(asset, bought_price, websocket)) * 0.01
    await websocket.close()
    return profit_percent


# Calculate the profit or loss relative to the proportion sold
def dollar_profit_loss(bought_price, sold_price, asset_amount_sold, asset_sold_total=None):
    sold_portion_cost = float(bought_price) * float(asset_amount_sold)
    sold_portion_revenue = float(sold_price) * float(asset_amount_sold)
    fees = 0
    if asset_sold_total:
        fees = sold_portion_revenue - asset_sold_total
    profit_loss = sold_portion_revenue - sold_portion_cost - fees
    return profit_loss


"""
 Fixed asset buy profit harvesting P/LRP: when a sell is made, any profit is kept and the fixed amount set to trade with
 is used to buy the next position. For example, when you set $100 to trade, if you sell for $105, $5 is kept and $100
 will be used for the next buy position. You can set if you want to just sell the profit and keep your position, or sell
 the entire position and initiate a new buy function to prevent only being sold once the stop limit is reached.
"""


def profit_harvest(asset, bought_price, amount_bought, full_sell=False):
    # Calculate the profit gained . Multiply that percentage by the current price to calculate profit
    if not full_sell:
        profit_loss = asyncio.run(profit_loss_percent(asset, bought_price))
        print(f'Profit loss percent: {profit_loss}')
        profit_to_sell = float(amount_bought) * float(profit_loss)
        # Return the dollar amount to sell
        print(f"Asset amount above/below the swing trade capital amount: {profit_to_sell}")
        return profit_to_sell
    else:
        # If a full sell is selected, sell the entire position
        return 'sell_all'


"""
 Swing trading P/LRP: Use the profits from trades to increase capital for buys, this could theoretically maximize
 profits, but also maximizes losses for large dips. If you plan to do this, keep a tax treasury fund as if you swing
 trade massive amounts, even if you lose it all on a dip, you still owe tax on the short term capital gains, or 15% of
 profit I.E. if you trade from $10,000 up to $100k, $90,000 profit will likely be taxed at minimum 15%, or $13,500. If
 you end up losing it all because you majorly gamble, and drop back down to $10,000 only, capital loss is only a max of
 $3k per year, and you'd still owe $10.5k even if you don't have the money. Swing trading is risky with large amounts,
 be warned. I am not a financial advisor and this is not financial advice. Just giving you a head up, so you don't
 screw over your life by being an ignorant donkey.
"""


def swing_trade(dollar_amount_bought, amount_sold, current_price, skim_percent=0):
    # If a portion of the profit is wanted to be kept, calculate that
    profit_to_keep = 0
    dollar_amount_sold = current_price * float(amount_sold)
    if skim_percent > 0:
        profit_to_keep = ((dollar_amount_sold - dollar_amount_bought) * (skim_percent * 0.01))
    # Return the amount in to use for the next buy order
    next_buy_amount = dollar_amount_sold - profit_to_keep
    print(f"Next_buy_amount: {next_buy_amount}")
    return next_buy_amount


if __name__ == "__main__":
    pass
