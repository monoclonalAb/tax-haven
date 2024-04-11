max_profit = 0
max_upper_bid = 0
max_lower_bid = 0
for lower_bid in range(900, 1000):
    for upper_bid in range(lower_bid, 1000):
        profit = 0
        for reserved_price in range(900, 1000):
            for number_of_agents in range(reserved_price-900):
                price = 1000
                if lower_bid > reserved_price:
                    price = lower_bid
                elif upper_bid > reserved_price:
                    price = upper_bid
                profit += 1000 - price
        if profit > max_profit:
            max_profit = profit
            max_upper_bid = upper_bid
            max_lower_bid = lower_bid
print(max_profit, max_upper_bid, max_lower_bid)