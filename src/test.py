import pprint

from pyautogui import *

from monitor import Monitor
from windowcontroller import WindowController

offset1 = 297
offset2 = 340
offset3 = 382
offset4 = 403

center1 = 799
center2 = 959
center3 = 1279
print(center1 - offset1, center1, center1 + offset1)
print(center1 - offset2, center1, center1 + offset2)
print(center1 - offset3, center1, center1 + offset3)
print(center1 - offset4, center1, center1 + offset4)
print()
print(center2 - offset1, center2, center2 + offset1)
print(center2 - offset2, center2, center2 + offset2)
print(center2 - offset3, center2, center2 + offset3)
print(center2 - offset4, center2, center2 + offset4)
print()
print(center3 - offset1, center3, center3 + offset1)
print(center3 - offset2, center3, center3 + offset2)
print(center3 - offset3, center3, center3 + offset3)
print(center3 - offset4, center3, center3 + offset4)


# 95%: todo...
# 90%: center + 382 (1279 + 382 = 1661)
# 80%: center + 340 (1279 + 340 = 1619)
# 70%: center + 297 (1279 + 297 = 1576)



# from time import sleep

# list = [855, 960, 1066, 1491, 1598, 1702]
# list = [i - 479 for i in list]
# print(list)
# exit()

# while True:
#     sleep(1)
#     pos = position()
#     print(pos)
#     print(pixel(pos.x, pos.y))

sleep(2)
# pos = locate('../static/en/comfort.png', 'test1.png', confidence=0.9)
# WindowController().activate_game_window()
# pos = locateOnScreen('../static/en/comfort.png', confidence=0.9)
pos = locateOnScreen("../static/en/food.png", confidence=0.9)
moveTo(pos)
exit()
pos = center(pos)
x, y = int(pos.x), int(pos.y)
print(x, y)
# exit()

# magic = (40, 44, 52)
magic = (47, 47, 47)

# (855(start), 960, 1066, 1491, 1598, 1702(end))
# 16:9: 200, 1000, leftup: 479, 273
# 1080: 300, 1300, left up 319, 183
# 2k: 600, 1600, leftup: 0, 0
# y: 1146, 1236, 1372 (true: 1412)

# press('esc')
# moveTo(1702, 1146)
# moveTo(x + 1053, y)
# exit()


moveTo(855, 1412)
sleep(2)
moveTo(960, 1412)
sleep(2)
moveTo(1066, 1412)
sleep(2)
moveTo(1491, 1412)
sleep(2)
moveTo(1598, 1412)
sleep(2)
moveTo(1702, 1412)
sleep(2)
exit()


start, end = 600, 1600
table = {}
first_x, first_y = 0, 0
last_x, last_y = 0, 0
first = True
for i in range(start, end):
    value = pixel(x + i, y)
    print(value)
    if value in table:
        table[value] += 1
    else:
        table[value] = 1

    if value == magic and first:
        first = False
        first_x, first_y = x + i, y
    elif value == magic:
        last_x, last_y = x + i, y

    # moveTo(x + i, y)

# press('esc')
moveTo(first_x, first_y)
sleep(4)
moveTo(last_x, last_y)


transformed_table = [(v, k) for (k, v) in table.items()]
transformed_table.sort()
pprint.pp(transformed_table)
print(first_x, first_y)
print(last_x, last_y)
