max_profit = 0
max_trades = []
exchange = [[1, 0.48, 1.52, 0.71], [2.05, 1, 3.26, 1.56], [0.64, 0.3, 1, 0.46], [1.41, 0.61, 2.08, 1]]
products = ["pizza", "wasabi", "snowball", "shells"]
capital = 2e6
for first in range(len(exchange)):
    for second in range(len(exchange)):
        for third in range(len(exchange)):
            for fourth in range(len(exchange)):
                profit = capital * exchange[3][first] * exchange[first][second] * exchange[second][third] * exchange[third][fourth] * exchange[fourth][3]
                if profit > max_profit:
                    max_profit = profit
                    max_trades = [first, second, third, fourth]
print(max_profit, [products[i] for i in max_trades])
