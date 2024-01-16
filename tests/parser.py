import argparse

parser = argparse.ArgumentParser(
                    prog='parser.py',
                    description='Start the script for Russian Fishing 4',
                    epilog='')
parser.add_argument('-p', '--profile', help='profile id to use', type=int)
parser.add_argument('-n', '--number', help='current number of fishes in keepnet', default=1, type=int)
args = parser.parse_args()
print(args.profile, args.number)