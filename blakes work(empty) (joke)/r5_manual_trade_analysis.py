#pnl = 750000 * %/100 * expected gain ratio - fees. fees = 90%^2
#maximum when derivative of pnl wrt % = 0
#% = 750000/18000 * expected gain ratio
def pnl(expected_ratio):
    return 75e4/180e2 * expected_ratio
def inv(pnl):
    return 180e2 * pnl/75e4
import matplotlib.pyplot as plt
plt.plot([i for i in range(101)], [pnl(i/100) for i in range(101)])
plt.xlabel("Expected Gain Ratio (%)")
plt.ylabel("PnL (Rs.)")
plt.show()
