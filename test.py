a = 1;
b = 2;
c = 3;
d = 4;

list = [];
list .append(a);
list.append(b);
print(list);
list.pop(0);
print(list);
list.append(c);
list.append(d);
print(list);
print(sum(list));
print(sum(list) / len(list));