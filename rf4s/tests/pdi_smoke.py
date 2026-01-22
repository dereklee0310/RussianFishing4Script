"""Quick pydirectinput smoke test.

This script prints the mouse position, moves the cursor in a few directions,
and prints the positions after each move. Run from repo root:

    python -u .\rf4s\tests\pdi_smoke.py

If nothing moves, try running PowerShell as Administrator.
"""
import time
import sys

try:
    import pydirectinput as pdi
except Exception as e:
    print("pydirectinput import failed:", e)
    sys.exit(1)

# disable failsafe (moveTo corner won't raise)
pdi.FAILSAFE = False

print("Initial position:", pdi.position())
print("Moving to (100,100) absolute")
pdi.moveTo(100, 100)
print("After moveTo(100,100):", pdi.position())

time.sleep(0.5)
print("Moving relative (+100,+0)")
pdi.moveRel(100, 0)
print("After moveRel(+100,0):", pdi.position())

time.sleep(0.5)
print("Moving relative (0,+100)")
pdi.moveRel(0, 100)
print("After moveRel(0,+100):", pdi.position())

time.sleep(0.5)
print("Done")
