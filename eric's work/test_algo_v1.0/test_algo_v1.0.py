import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List

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

    def trade_amethysts (self, order_depth: OrderDepth, acceptable_price: int) -> list[Order]:
        """
        AMETHYSTS:
        - min_price: 9,995
        - max_price: 10,005
        
        first plan: (very basic plan, just to get started)
        - when bid price > 10,000, sell
        - when ask price < 10,000, buy
        """
        
        orders: List[Order] = []
        
        for price, amount in order_depth.sell_orders.items():
            if price < acceptable_price:
                orders.append(Order("AMETHYSTS", price, -amount))
        
        for price, amount in order_depth.buy_orders.items():
            if price > acceptable_price:
                orders.append(Order("AMETHYSTS", price, -amount))
        return orders
      
    def trade_starfruit (self, order_depth: OrderDepth, moving_average: int) -> list[Order]:
      """
      STARFRUIT:
      - variable min_price and max_price
      
      first plan:
      - calculate a moving average
      - when bid price > moving average, sell
      - when ask price < moving average, buy
      """
      
      orders: List[Order] = []
      
      for price, amount in order_depth.sell_orders.items():
          if price <= moving_average:
              orders.append(Order("STARFRUIT", price, -amount))
      
      for price, amount in order_depth.buy_orders.items():
          if price >= moving_average:
              orders.append(Order("STARFRUIT", price, -amount))
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
        amethyst_order = self.trade_amethysts(state.order_depths["AMETHYSTS"], 10000)
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
        logger.print("best sf bid price: " + str(best_starfruit_bid_price))
        logger.print("best sf ask price: " + str(best_starfruit_ask_price))
        logger.print("average overall sf price: " + str(average_starfruit_price))
        
        self.list_of_starfruit_averages.append(average_starfruit_price)

        if (len(self.list_of_starfruit_averages) > 10): self.list_of_starfruit_averages.pop(0)
        
        moving_average = sum(self.list_of_starfruit_averages) / len(self.list_of_starfruit_averages)
        logger.print("moving average: " + str(moving_average))
        logger.print(moving_average)
        starfruit_order = self.trade_starfruit(state.order_depths["STARFRUIT"], moving_average)
        
        result["STARFRUIT"] = starfruit_order

        logger.flush(state, result, conversions, trader_data)
        return result, conversions, trader_data