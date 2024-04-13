import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List
import collections

class Logger:
  def __init__(self) -> None:
    self.logs = ""

  def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
    self.logs += sep.join(map(str, objects)) + end

  def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
    print(json.dumps([
        self.compress_state(state),
        self.compress_orders(orders),
        conversions,
        trader_data,
        self.logs,
    ], cls=ProsperityEncoder, separators=(",", ":")))

    self.logs = ""

  def compress_state(self, state: TradingState) -> list[Any]:
    return [
      state.timestamp,
      state.traderData,
      self.compress_listings(state.listings),
      self.compress_order_depths(state.order_depths),
      self.compress_trades(state.own_trades),
      self.compress_trades(state.market_trades),
      state.position,
      self.compress_observations(state.observations),
    ]

  def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
    compressed = []
    for listing in listings.values():
      compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

    return compressed

  def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
    compressed = {}
    for symbol, order_depth in order_depths.items():
      compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

    return compressed

  def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
    compressed = []
    for arr in trades.values():
      for trade in arr:
        compressed.append([
          trade.symbol,
          trade.price,
          trade.quantity,
          trade.buyer,
          trade.seller,
          trade.timestamp,
        ])

    return compressed

  def compress_observations(self, observations: Observation) -> list[Any]:
    conversion_observations = {}
    for product, observation in observations.conversionObservations.items():
      conversion_observations[product] = [
        observation.bidPrice,
        observation.askPrice,
        observation.transportFees,
        observation.exportTariff,
        observation.importTariff,
        observation.sunlight,
        observation.humidity,
      ]

    return [observations.plainValueObservations, conversion_observations]

  def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
    compressed = []
    for arr in orders.values():
      for order in arr:
        compressed.append([order.symbol, order.price, order.quantity])

    return compressed

logger = Logger()

class Trader:
  
  list_of_starfruit_averages = []

  def values_extract(self, order_dict, buy=0):
    total_vol = 0
    best_val = -1
    mxvol = -1

    # dictionary pair with asking price and volume
    for ask, vol in order_dict.items():
      if(buy==0):
        vol *= -1
      total_vol += vol
      if total_vol > mxvol:
        mxvol = vol
        best_val = ask
    
    return total_vol, best_val
  
  def trade_amethysts (self, product: str, order_depth: OrderDepth, position: int , acceptable_bid: int, acceptable_ask: int) -> list[Order]:
    orders: List[Order] = []
    
    ordered_dict_sell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
    ordered_dict_buy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
    
    sell_vol, best_sell_price = self.values_extract(ordered_dict_sell)
    buy_vol, best_buy_price = self.values_extract(ordered_dict_buy, 1)
    
    undercut_buy = best_buy_price + 1
    undercut_sell = best_sell_price - 1

    bid_pr = min(undercut_buy, acceptable_bid-1) # we will shift this by 1 to beat this price
    sell_pr = max(undercut_sell, acceptable_ask+1)

    current_pos = position;

    for ask, vol in ordered_dict_sell.items():
      if ((ask < acceptable_bid) or ((position<0) and (ask == acceptable_bid))) and current_pos < 20:
        order_for = min(-vol, 20 - current_pos)
        current_pos += order_for
        orders.append(Order(product, ask, order_for))

    if (current_pos < 20) and (position >= 15):
      num = min(40, 20 - current_pos)
      orders.append(Order(product, min(undercut_buy - 1, acceptable_bid-1), num))
      current_pos += num
    
    if current_pos < 20 and (position >= 0) and (position < 15):
      num = min(40, 20 - current_pos)
      orders.append(Order(product, bid_pr, num))
      current_pos += num

    if (current_pos < 20) and (position < 0) and (position > -15):
      num = min(40, 20 - current_pos)
      orders.append(Order(product, min(undercut_buy + 1, acceptable_bid-1), num))
      current_pos += num

    if (current_pos < 20) and (position <= -15):
      num = min(40, 20 - current_pos)
      orders.append(Order(product, max(undercut_buy + 1, acceptable_bid-1), num))
      current_pos += num

    current_pos = position

    for bid, vol in ordered_dict_buy.items():
      if ((bid > acceptable_ask) or ((position>0) and (bid == acceptable_ask))) and current_pos > -20:
        order_for = max(-vol, -20-current_pos)
        # order_for is a negative number denoting how much we will sell
        current_pos += order_for
        orders.append(Order(product, bid, order_for))
    
    if (current_pos > -20) and (position <= -15):
      num = max(-40, -20-current_pos)
      orders.append(Order(product, max(undercut_sell+1, acceptable_ask+1), num))
      current_pos += num
      
    if (current_pos > -20) and (position > -15) and (position <= 0) :
      num = max(-40, -20-current_pos)
      orders.append(Order(product, sell_pr, num))
      current_pos += num

    if (current_pos > -20) and (position > 0) and (position < 15):
      num = max(-40, -20-current_pos)
      orders.append(Order(product, max(undercut_sell-1, acceptable_ask+1), num))
      current_pos += num

    if (current_pos > -20) and (position >= 15):
      num = max(-40, -20-current_pos)
      orders.append(Order(product, min(undercut_sell-1, acceptable_ask+1), num))
      current_pos += num

    return orders;
    
  def trade_starfruit (self, product: str, order_depth: OrderDepth, position: int , acceptable_bid: int, acceptable_ask: int) -> list[Order]:
      orders: list[Order] = []

      osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
      obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

      sell_vol, best_sell_pr = self.values_extract(osell)
      buy_vol, best_buy_pr = self.values_extract(obuy, 1)

      undercut_buy = best_buy_pr + 1
      undercut_sell = best_sell_pr - 1

      bid_pr = min(undercut_buy, acceptable_bid) # we will shift this by 1 to beat this price
      sell_pr = max(undercut_sell, acceptable_ask)
      logger.print("STARFRUIT bid price: " + str(bid_pr))
      logger.print("STARFRUIT sell price: " + str(sell_pr))

      """ BIDS """
      cpos = position

      for ask, vol in osell.items():
          if ((ask <= acceptable_bid) or ((position<0) and (ask == acceptable_bid+1))) and cpos < 20:
              order_for = min(-vol, 20 - cpos)
              cpos += order_for
              orders.append(Order(product, ask, order_for))

      if cpos < 20:
          num = 20 - cpos
          orders.append(Order(product, bid_pr, num))
          cpos += num
      
      """ ASKS """
      cpos = position

      for bid, vol in obuy.items():
        if ((bid >= acceptable_ask) or ((position>0) and (bid+1 == acceptable_ask))) and cpos > -20:
          order_for = max(-vol, -20-cpos)
          # order_for is a negative number denoting how much we will sell
          cpos += order_for
          orders.append(Order(product, bid, order_for))

      if cpos > -20:
        num = -20-cpos
        orders.append(Order(product, sell_pr, num))
        cpos += num

      return orders
    


  def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
    """
    Only method required. It takes all buy and sell orders for all symbols as an input,
    and outputs a list of orders to be sent
    """
    result = {}
    conversions = 0
    trader_data = ""
    
    # products = "AMETHYSTS"
    amethyst_order = self.trade_amethysts("AMETHYSTS", state.order_depths["AMETHYSTS"], state.position.get("AMETHYSTS", 0), 10000, 10000)
    result["AMETHYSTS"] = amethyst_order
    
    #product = "STARFRUIT"
    
    # average_starfruit_bid_price = sum(state.order_depths["STARFRUIT"].buy_orders.keys()) / len(state.order_depths["STARFRUIT"].buy_orders)
    # average_starfruit_ask_price = sum(state.order_depths["STARFRUIT"].sell_orders.keys()) / len(state.order_depths["STARFRUIT"].sell_orders)
    # average_starfruit_price = (average_starfruit_bid_price + average_starfruit_ask_price) / 2
    # logger.print("average sf bid price: " + str(average_starfruit_bid_price))
    # logger.print("average sf ask price: " + str(average_starfruit_ask_price))
    # logger.print("average overall sf price: " + str(average_starfruit_price))
    
    best_starfruit_bid_price = list(state.order_depths["STARFRUIT"].buy_orders.keys())[0]
    best_starfruit_ask_price = list(state.order_depths["STARFRUIT"].sell_orders.keys())[0]
    average_starfruit_price = (best_starfruit_bid_price + best_starfruit_ask_price) / 2
    # logger.print("best sf bid price: " + str(best_starfruit_bid_price))
    # logger.print("best sf ask price: " + str(best_starfruit_ask_price))
    # logger.print("average overall sf price: " + str(average_starfruit_price))
    
    self.list_of_starfruit_averages.append(average_starfruit_price)

    if (len(self.list_of_starfruit_averages) > 5): self.list_of_starfruit_averages.pop(0)
    
    moving_average = round(sum(self.list_of_starfruit_averages) / len(self.list_of_starfruit_averages))
    logger.print("moving average: " + str(moving_average))
    starfruit_order = self.trade_starfruit("STARFRUIT", state.order_depths["STARFRUIT"], state.position.get("STARFRUIT", 0), moving_average-1, moving_average+1)
    
    result["STARFRUIT"] = starfruit_order

    logger.flush(state, result, conversions, trader_data)
    return result, conversions, trader_data