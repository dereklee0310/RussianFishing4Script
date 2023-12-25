import sys

# args
print(len(sys.argv))

# filename
print(sys.argv[0])

for arg in sys.argv[1:]:
    print(arg)