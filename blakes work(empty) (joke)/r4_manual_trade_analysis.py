#adapted from r1

max_profit = 0
max_upper_bid = 0
max_lower_bid = 0

def pnl(lower_bid, upper_bid):
    assert(lower_bid <= upper_bid)
    profit = 0
    average = 979
    for reserved_price in range(900, 1000):
        for number_of_agents in range(reserved_price-900):
            price = 1000
            additional = 0
            if lower_bid > reserved_price:
                price = lower_bid
                additional = 1000 - price
            elif upper_bid > reserved_price:
                price = upper_bid
                additional = 1000 - price
                if upper_bid < average:
                    additional *= (1000-average)/(1000-upper_bid)
            profit += additional
    return profit

for l in range(900, 1000):
    for u in range(l, 1000):
        profit = pnl(l, u)
        if profit > max_profit:
            max_profit = profit
            max_upper_bid = u
            max_lower_bid = l
print(max_profit, max_upper_bid, max_lower_bid)
print(pnl(952, 978))
print(pnl(953, 979))
print(pnl(953, 980))
