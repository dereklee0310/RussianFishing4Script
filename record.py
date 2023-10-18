import keyboard
import time

# q = []
# time = []
# rec = keyboard.record(until='space')
# for key in rec:
#     if key.event_type == 'down':
#         q.append(key.name)
# print(q)

import keyboard, time
while True:
    a = keyboard.read_event()     #Reading the key
    if a.name == "esc":break      #Loop will break on pressing esc, you can remove that
    elif a.event_type == "down":  #If any button is pressed (Not talking about released) then wait for it to be released
        t = time.time()           #Getting time in sec
        b = keyboard.read_event() 
        while not b.event_type == "up" and b.name == a.name:  #Loop till the key event doesn't matches the old one
            b = keyboard.read_event()
        print('Pressed Key "'+ b.name + '" for ' + str(time.time()-t))