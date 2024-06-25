import json
import jsonpickle
import math
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List
import collections
import numpy as np
import pandas as pd
from statistics import NormalDist

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

class PickledData:
  def __init__(self, conversions: int = 0) -> None:
    self.conversions = conversions
    self.starfruit_values = collections.deque()
    self.starfruit_sum = 0
    
  def return_conversions(self) -> int:
    return self.conversions
  
  def change_conversions(self, conversions: int) -> None:
    self.conversions = conversions
    

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
    
    undercut_bid = best_buy_price + 1
    undercut_ask = best_sell_price - 1

    bid_pr = min(undercut_bid, acceptable_bid-1) # we will shift this by 1 to beat this price
    sell_pr = max(undercut_ask, acceptable_ask+1)

    current_pos = position;

    # for ask, vol in ordered_dict_sell.items():
    #   if ((ask < acceptable_bid) or ((position<0) and (ask == acceptable_bid))) and current_pos < 20:
    #     order_for = min(-vol, 20 - current_pos)
    #     current_pos += order_for
    #     orders.append(Order(product, ask, order_for))

    # if (current_pos < 20) and (position < 0):
    #   num = min(40, 20 - current_pos)
    #   orders.append(Order(product, min(undercut_bid + 1, acceptable_bid-1), num))
    #   current_pos += num

    # if (current_pos < 20) and (position > 15):
    #   num = min(40, 20 - current_pos)
    #   orders.append(Order(product, min(undercut_bid - 1, acceptable_bid-1), num))
    #   current_pos += num

    # if current_pos < 20:
    #   num = min(40, 20 - current_pos)
    #   orders.append(Order(product, bid_pr, num))
    #   current_pos += num

    # current_pos = position

    # for bid, vol in ordered_dict_buy.items():
    #   if ((bid > acceptable_ask) or ((position>0) and (bid == acceptable_ask))) and current_pos > -20:
    #     order_for = max(-vol, -20-current_pos)
    #     # order_for is a negative number denoting how much we will sell
    #     current_pos += order_for
    #     orders.append(Order(product, bid, order_for))
    
    # if (current_pos > -20) and (position > 0):
    #   num = max(-40, -20-current_pos)
    #   orders.append(Order(product, max(undercut_ask-1, acceptable_ask+1), num))
    #   current_pos += num

    # if (current_pos > -20) and (position < -15):
    #   num = max(-40, -20-current_pos)
    #   orders.append(Order(product, max(undercut_ask+1, acceptable_ask+1), num))
    #   current_pos += num

    # if current_pos > -20:
    #   num = max(-40, -20-current_pos)
    #   orders.append(Order(product, sell_pr, num))
    #   current_pos += num
    
    orders.append(Order(product, 9998, 20 - current_pos))
    orders.append(Order(product, 10002, -20 - current_pos))

    return orders;
    
  def trade_starfruit (self, product: str, order_depth: OrderDepth, position: int , acceptable_bid: int, acceptable_ask: int) -> list[Order]:
      orders: list[Order] = []

      osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
      obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

      sell_vol, best_sell_pr = self.values_extract(osell)
      buy_vol, best_buy_pr = self.values_extract(obuy, 1)

      undercut_bid = best_buy_pr + 1
      undercut_ask = best_sell_pr - 1

      bid_pr = min(undercut_bid, acceptable_bid) # we will shift this by 1 to beat this price
      sell_pr = max(undercut_ask, acceptable_ask)
      logger.print("STARFRUIT bid price: " + str(bid_pr))
      logger.print("STARFRUIT sell price: " + str(sell_pr))

      """ BUYING """
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
      
      """ SELLING """
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
  
  def trade_starfruit_v2 (self, state: TradingState) -> list[Order]:
      #starfruit_order = self.trade_starfruit("STARFRUIT", state.order_depths["STARFRUIT"], state.position.get("STARFRUIT", 0), round(moving_average-1), round(moving_average+1))
      product = "STARFRUIT"
      order_depth = state.order_depths["STARFRUIT"]
      position = state.position.get("STARFRUIT", 0)
      
      orders: list[Order] = []

      osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
      obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

      sell_vol, best_sell_pr = self.values_extract(osell)
      buy_vol, best_buy_pr = self.values_extract(obuy, 1)

      worst_sell_pr = next(reversed(osell)) # take cheapest sell price
      worst_buy_pr = next(reversed(obuy))
      mid_price = (worst_sell_pr + worst_buy_pr)/2
      
      self.list_of_starfruit_averages.append(mid_price)
      if (len(self.list_of_starfruit_averages) > 5): self.list_of_starfruit_averages.pop(0)
      moving_average = sum(self.list_of_starfruit_averages) / len(self.list_of_starfruit_averages)
      
      # attempt 1:
      acceptable_bid = round(moving_average - 1)
      acceptable_ask = round(moving_average + 1)
      
      undercut_bid = best_buy_pr + 1
      undercut_ask = best_sell_pr - 1

      bid_pr = min(undercut_bid, acceptable_bid) # we will shift this by 1 to beat this price
      sell_pr = max(undercut_ask, acceptable_ask)
      logger.print("STARFRUIT bid price: " + str(bid_pr))
      logger.print("STARFRUIT sell price: " + str(sell_pr))

      """ BUYING """
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
      
      """ SELLING """
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
    
  def trade_orchids (self, product: str, order_depth: OrderDepth, position: int, observation: Observation, conversions: int) -> list[Order]:
    """
Summarizing trading microstructure of ORCHIDs:
1.	ConversionObservation (https://imc-prosperity.notion.site/Writing-an-Algorithm-in-Python-658e233a26e24510bfccf0b1df647858#44efb36257b94733887ae00f46a805f1) shows quotes of ORCHID offered by the ducks from South Archipelago
2.	If you want to purchase 1 unit of ORCHID from the south, you will purchase at the askPrice, pay the TRANSPORT_FEES, IMPORT_TARIFF 
3.	If you want to sell 1 unit of ORCHID to the south, you will sell at the bidPrice, pay the TRANSPORT_FEES, EXPORT_TARIFF
4.	You can ONLY trade with the south via the conversion request with applicable conditions as mentioned in the wiki
5.	For every 1 unit of ORCHID net long position you hold, you will pay 0.1 Seashells per timestamp you hold that position. No storage cost applicable to net short position
6.	Negative ImportTariff would mean you would receive premium for importing ORCHIDs to your island
7.	Each Day in ORCHID trading is equivalent to 12 hours on the island. You can assume the ORCHID quality doesn't deteriorate overnight
8.	Sunlight unit: Average sunlight per hour is 2500 units. The data/plot shows instantaneous rate of sunlight on any moment of the day
    """

    orders: list[Order] = []

    osell = collections.OrderedDict(sorted(order_depth.sell_orders.items())) # {12: -3, 11: -2}
    obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True)) # {9: 5, 10: 4}

    sell_vol, best_sell_pr = self.values_extract(osell) # best sale price to buy everything
    buy_vol, best_buy_pr = self.values_extract(obuy, 1) # best buy price to sell everything
    
    lowest_sell_price = list(osell.keys())[0]
    highest_buy_price = list(obuy.keys())[0]
    
    # sell to south, sell at bidprice + pay transport fees + export tariff
    south_bid = observation.conversionObservations["ORCHIDS"].bidPrice
    export_tariff = observation.conversionObservations["ORCHIDS"].exportTariff
    
    # buy from south, buy at askprice + pay transport fees + import tariff 
    south_ask = observation.conversionObservations["ORCHIDS"].askPrice
    import_tariff = observation.conversionObservations["ORCHIDS"].importTariff
    
    transport_fees = observation.conversionObservations["ORCHIDS"].transportFees
    
    """ BUYING """ # buy from north, sell to the south
    
    total_conversions = 0
    # cpos = position + conversions # should be 0 99% of the time
    south_sell_price = south_bid - transport_fees - export_tariff
    
    # for ask, vol in osell.items():
    #   if (ask < south_sell_price) and cpos < 100:
    #     order_for = min(-vol, 100 - cpos)
    #     cpos += order_for
    #     total_conversions += -order_for
    #     orders.append(Order(product, ask, order_for))

    # if cpos < 100:
    #   num = 100-cpos
    #   orders.append(Order(product, math.floor(south_sell_price)-1, num))
    #   cpos += num
    #   total_conversions += -num
      
    """ SELLING """ # sell to the north, buy from the south PROFITABLE
    
    cpos = position + conversions # should be 0 99% of the time
    south_buy_price = south_ask + transport_fees + import_tariff 
    rounded_sbp = math.ceil(south_buy_price)
    
    # for bid, vol in obuy.items():
    #   if (bid > south_buy_price) and cpos > -100:
    #     order_for = max(-vol, -100-cpos)
    #     # order_for is a negative number denoting how much we will sell
    #     cpos += order_for
    #     total_conversions += -order_for
    #     orders.append(Order(product, bid, order_for))
      
    
    # if cpos > -100: 
    #   num = -100-cpos
    #   orders.append(Order(product, rounded_sbp+2, num))
    #   cpos += num
    #   total_conversions += -num
    
    if cpos > -100 and rounded_sbp >= highest_buy_price + 1:
      num = -100-cpos
      orders.append(Order(product, rounded_sbp+1, num))
      cpos += num
      total_conversions += -num
    # elif cpos > -100: #and rounded_sbp > highest_buy_price:
    #   num = -100-cpos
    #   orders.append(Order(product, rounded_sbp+2, num))
    #   cpos += num
    #   total_conversions += -num
    # elif cpos > -100:
    #   num = -100-cpos
    #   orders.append(Order(product, rounded_sbp+3, num))
    #   cpos += num
    #   total_conversions += -num

    # observation.conversionObservations["ORCHIDS"].sunlight
    # observation.conversionObservations["ORCHIDS"].humidity
    
    logger.print("South BidPrice: " + str(south_bid))
    logger.print("South AskPrice: " + str(south_ask))
    # logger.print("Import Tariff:" + str(import_tariff))
    # logger.print("Export Tariff: " + str(export_tariff))
    # logger.print("Transport Fees: " + str(transport_fees))
    logger.print("Highest Buy: " + str(highest_buy_price))
    logger.print("Lowest Sell: " + str(lowest_sell_price))
    logger.print("South Buy: " + str(south_buy_price))
    logger.print("South Sell: " + str(south_sell_price))
    
    return total_conversions, orders
    
  def trade_basket (self, state: TradingState) -> list[Order]: 
    orders = {'CHOCOLATE': [], 'ROSES': [], 'STRAWBERRIES': [], 'GIFT_BASKET': []}
    products = ['CHOCOLATE', 'ROSES', 'STRAWBERRIES', 'GIFT_BASKET']
    position_limit = {'CHOCOLATE': 250, 'ROSES': 350, 'STRAWBERRIES': 60, 'GIFT_BASKET': 60}
    osell, obuy, best_sell, best_buy, worst_sell, worst_buy, mid_price, vol_buy, vol_sell = {}, {}, {}, {}, {}, {}, {}, {}, {}
    
    for p in products:
      if len(state.order_depths[p].sell_orders) == 0 or len(state.order_depths[p].buy_orders) == 0: return orders
      
      osell[p] = collections.OrderedDict(sorted(state.order_depths[p].sell_orders.items())) # {12: -3, 11: -2}
      obuy[p] = collections.OrderedDict(sorted(state.order_depths[p].buy_orders.items(), reverse=True)) # {9: 5, 10: 4}
      
      best_sell[p] = next(iter(osell[p])) # take most expensive sell price
      best_buy[p] = next(iter(obuy[p]))

      worst_sell[p] = next(reversed(osell[p])) # take cheapest sell price
      worst_buy[p] = next(reversed(obuy[p]))

      mid_price[p] = (best_sell[p] + best_buy[p])/2
      vol_buy[p], vol_sell[p] = 0, 0
      
      for price, vol in obuy[p].items():
        vol_buy[p] += vol 

      for price, vol in osell[p].items():
        vol_sell[p] += -vol 


    mean = 20.525583333333334
    STD = 76.4202568412432

    # res_buy = mid_price['GIFT_BASKET'] - mid_price['CHOCOLATE']*4 - mid_price['STRAWBERRIES']*6 - mid_price['ROSES'] - 400 + mean
    # res_sell = mid_price['GIFT_BASKET'] - mid_price['CHOCOLATE']*4 - mid_price['STRAWBERRIES']*6 - mid_price['ROSES'] - 400 + mean
    
    res_price = mid_price['GIFT_BASKET'] - mid_price['CHOCOLATE']*4 - mid_price['STRAWBERRIES']*6 - mid_price['ROSES'] - 400 + mean
    
    logger.print("res_price:" + str(res_price))
    
    trade_at = STD*0.8
    close_at = STD*0
    
    logger.print("trade_at:" + str(trade_at))
    logger.print("best:" + str(best_buy))
    logger.print("worst:" + str(worst_buy))

    if res_price > trade_at: #i will sell
      vol = state.position.get('GIFT_BASKET', 0) + position_limit['GIFT_BASKET']
      if vol > 0:
        orders['GIFT_BASKET'].append(Order('GIFT_BASKET', worst_buy['GIFT_BASKET'], -vol)) 
    elif res_price < -trade_at: #i will buy
      vol = position_limit['GIFT_BASKET'] - state.position.get('GIFT_BASKET', 0)
      if vol > 0:
        orders['GIFT_BASKET'].append(Order('GIFT_BASKET', worst_sell['GIFT_BASKET'], vol))
        
    return orders
  
  def black_scholes_price(self, S, K, t, r, sigma, option_type):
      d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
      d2 = d1 - sigma * np.sqrt(t)
      if option_type == 'call':
          price = S * NormalDist().cdf(d1) - K * np.exp(-r * t) * NormalDist().cdf(d2)
      elif option_type == 'put':
          price = K * np.exp(-r * t) * NormalDist().cdf(-d2) - S * NormalDist().cdf(-d1)
      return price

  def trade_coconut (self, state: TradingState) -> list[Order]:
    orders = {'COCONUT': [], 'COCONUT_COUPON': []}
    products = ['COCONUT', 'COCONUT_COUPON']
    position_limit = {'COCONUT': 300, 'COCONUT_COUPON': 600}
    osell, obuy, best_sell, best_buy, worst_sell, worst_buy, mid_price, vol_buy, vol_sell = {}, {}, {}, {}, {}, {}, {}, {}, {}
    
    for p in products:
      if (len(state.order_depths[p].sell_orders) == 0 or len(state.order_depths[p].buy_orders) == 0): continue

      osell[p] = collections.OrderedDict(sorted(state.order_depths[p].sell_orders.items())) # {12: -3, 11: -2}
      obuy[p] = collections.OrderedDict(sorted(state.order_depths[p].buy_orders.items(), reverse=True)) # {9: 5, 10: 4}
      
      best_sell[p] = next(iter(osell[p])) # take most expensive sell price
      best_buy[p] = next(iter(obuy[p]))

      worst_sell[p] = next(reversed(osell[p])) # take cheapest sell price
      worst_buy[p] = next(reversed(obuy[p]))

      mid_price[p] = (best_sell[p] + best_buy[p])/2
      vol_buy[p], vol_sell[p] = 0, 0
      
      for price, vol in obuy[p].items():
        vol_buy[p] += vol 
        # if vol_buy[p] >= self.POSITION_LIMIT[p]/10:
        #   break
      for price, vol in osell[p].items():
        vol_sell[p] += -vol 
        # if vol_sell[p] >= self.POSITION_LIMIT[p]/10:
        #   break
    
    if "COCONUT" in mid_price:
      coco_benchmark = mid_price["COCONUT"] - 10000
      
    if "COCONUT_COUPON" in mid_price:
      #call = self.black_scholes_price(mid_price['COCONUT'], 10000, 248/365, 0, 0.1933295134, 'call')
      call = self.black_scholes_price(mid_price['COCONUT'], 10000, 246/252, 0, 0.1606393714, 'call')
      STD = 13.530582431810915
      trade_at = STD*0.5
      
      coup_benchmark = mid_price["COCONUT_COUPON"] - 637.63
      call_benchmark = call - 637.63
      
      if (coup_benchmark > call_benchmark + trade_at):
        vol = state.position.get('COCONUT_COUPON', 0) + position_limit['COCONUT_COUPON']
        if vol > 0:# and boolean == True:
          orders['COCONUT_COUPON'].append(Order('COCONUT_COUPON', worst_buy['COCONUT_COUPON'], -vol))
        # elif 'COCONUT_COUPON' not in state.position:
        #   boolean = False
        # elif state.position.get('COCONUT_COUPON', 0) < -550:
        #   boolean = False
        
        # coco_vol = state.position.get('COCONUT', 0) + position_limit['COCONUT']
        # if coco_vol > 0:
        #   orders['COCONUT'].append(Order('COCONUT', worst_buy['COCONUT'], -coco_vol))

        # coco_vol = position_limit['COCONUT'] - state.position.get('COCONUT', 0)
        # if coco_vol > 0:
        #   orders['COCONUT'].append(Order('COCONUT', worst_sell['COCONUT'], coco_vol))
          
      elif (coup_benchmark < call_benchmark - trade_at):
        vol = position_limit['COCONUT_COUPON'] - state.position.get('COCONUT_COUPON', 0)
        if vol > 0:# and boolean == False:
          orders['COCONUT_COUPON'].append(Order('COCONUT_COUPON', worst_sell['COCONUT_COUPON'], vol))
        # elif 'COCONUT_COUPON' not in state.position:
        #   boolean = True
        # elif state.position.get('COCONUT_COUPON', 0) > 550:
        #   boolean = True
        
        # coco_vol = position_limit['COCONUT'] - state.position.get('COCONUT', 0)
        # if coco_vol > 0:
        #   orders['COCONUT'].append(Order('COCONUT', worst_sell['COCONUT'], coco_vol))
        
        # coco_vol = state.position.get('COCONUT', 0) + position_limit['COCONUT']
        # if coco_vol > 0:
          # orders['COCONUT'].append(Order('COCONUT', worst_buy['COCONUT'], -coco_vol))
      
      logger.print("buy: " + str(call))
    
    # diff = 15
    # market_trades = state.market_trades.get("COCONUT_COUPON", [])
    # if len(market_trades) > 0:
    #   last_trade = market_trades[-1]
    #   if last_trade.buyer == "Vladimir":
    #     if (last_trade.price > call + diff) or (last_trade.price < call - diff):
    #       vol = state.position.get('COCONUT_COUPON', 0)
    #       if (vol > 0):
    #         orders['COCONUT_COUPON'].append(Order('COCONUT_COUPON', worst_buy['COCONUT_COUPON'], -vol))
    #       elif (vol < 0):
    #         orders['COCONUT_COUPON'].append(Order('COCONUT_COUPON', worst_sell['COCONUT_COUPON'], vol))
    
    return orders

  def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
    """
    Only method required. It takes all buy and sell orders for all symbols as an input,
    and outputs a list of orders to be sent
    """
    result = {}
    conversions = 0
    trader_data = ""
    
    if (state.traderData != ""):
      pickled_data = jsonpickle.decode(state.traderData)
    else:
      pickled_data = PickledData()
    
    # # product = "AMETHYSTS"
    amethyst_order = self.trade_amethysts("AMETHYSTS", state.order_depths["AMETHYSTS"], state.position.get("AMETHYSTS", 0), 10000, 10000)
    result["AMETHYSTS"] = amethyst_order
    
    """
    # #! product = "STARFRUIT" v1
    # worst_starfruit_bid_price = list(state.order_depths["STARFRUIT"].buy_orders.keys())[0]
    # worst_starfruit_ask_price = list(state.order_depths["STARFRUIT"].sell_orders.keys())[0]
    # average_starfruit_price = (worst_starfruit_bid_price + worst_starfruit_ask_price) / 2
    
    # self.list_of_starfruit_averages.append(average_starfruit_price)
    # if (len(self.list_of_starfruit_averages) > 5): self.list_of_starfruit_averages.pop(0)
    # moving_average = round(sum(self.list_of_starfruit_averages) / len(self.list_of_starfruit_averages))

    # logger.print("moving average: " + str(moving_average))
    # starfruit_order = self.trade_starfruit("STARFRUIT", state.order_depths["STARFRUIT"], state.position.get("STARFRUIT", 0), round(moving_average-1), round(moving_average+1))
    """
    
    # #! product = "STARFRUIT" v2
    starfruit_order = self.trade_starfruit_v2(state)
    
    result["STARFRUIT"] = starfruit_order

    # # product = "ORCHIDS"
    conversions = pickled_data.return_conversions()
    
    if conversions > state.position.get("ORCHIDS", 0): 
      conversions = -state.position.get("ORCHIDS", 0)
      
    new_conversions, orchid_order = self.trade_orchids("ORCHIDS", state.order_depths["ORCHIDS"], state.position.get("ORCHIDS", 0), state.observations, conversions)
    result["ORCHIDS"] = orchid_order
    
    pickled_data.change_conversions(new_conversions)
      
    # product = "GIFT_BASKETS"
    basket_order = self.trade_basket(state)
    result['GIFT_BASKET'] = basket_order['GIFT_BASKET']
    result['ROSES'] = basket_order['ROSES']
    result['STRAWBERRIES'] = basket_order['STRAWBERRIES']
    result['CHOCOLATE'] = basket_order['CHOCOLATE']
    
    # product = "COCONUT"
    coconut_order = self.trade_coconut(state)
    result['COCONUT_COUPON'] = coconut_order['COCONUT_COUPON']
    result['COCONUT'] = coconut_order['COCONUT']
      
    trader_data = jsonpickle.encode(pickled_data)
    
    logger.flush(state, result, conversions, trader_data)
    return result, conversions, trader_data