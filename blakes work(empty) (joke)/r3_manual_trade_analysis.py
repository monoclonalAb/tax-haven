import matplotlib.pyplot as plt
mults = [24, 70, 41, 21, 60, 47, 82, 87, 80, 35, 73, 89, 100, 90, 17, 77, 83, 85, 79, 55, 12, 27, 52, 15, 30]
hunters = [2, 4, 3, 2, 4, 3, 5, 5, 5, 3, 4, 5, 8, 7, 2, 5, 5, 5, 5, 4, 2, 3, 4, 2, 3]
values = [i/j for i, j in zip(mults, hunters)]
altered = []
threshold = [a for a in values if a >= 10]
for i in range(len(values)):
    if values[i] in threshold:
        altered.append(mults[i]/(hunters[i] + (100/len(threshold))))
    else:
        altered.append(mults[i]/hunters[i])
for i in range(len(values)):
    print("{: ^10} {: ^20} {: ^20}".format(mults[i], values[i], altered[i]))
plt.plot(mults, values, 'ro')
plt.plot(mults, altered, 'bo')
plt.show()
#This code assumes people choose values with a step distribution above a certain threshold. Our choices for this ended up being 52 and 100. 52 was the top tile, 100 was around the middle.
