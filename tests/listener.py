"""
    Functionality: test pynput keyboard listener
"""

from pynput import keyboard
from time import sleep

def on_press(key):
    print(type(key))
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    print('{0} released'.format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released (blocking)
# with keyboard.Listener(
#         on_press=on_press,
#         on_release=on_release) as listener:
#     listener.join()


while True:
    with keyboard.Events() as events:
        # Block at most one second
        event = events.get(1.0)
        if event is None:
            print('You did not press a key within one second')
            # exit()
        else:
            print('Received event {}'.format(event))
            key = str(event.key)
            print(key)
            print(type(event))
            if key == "'w'": # compare with 'w'
                print('w detected')
            elif key == 'Key.space':
                print('Space detected')
            elif key == '1':
                print('1 detected')
                exit()
exit()

# ...or, in a non-blocking fashion: (non-blocking)
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

listener.start() # start the thread

# loop until the thread is no longer running
while listener.is_alive():
    sleep(1)
    print('The thread is alive!!!!')

# not neccessary, this will block the current process until the thread is stopped
listener.join()

# reference: https://pynput.readthedocs.io/en/latest/keyboard.html