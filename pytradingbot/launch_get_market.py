"""A script to launch a get_market mode of pytradingbot"""
#!/bin/python3.6

import argparse
import os.path
import sys

from pytradingbot.iolib.crypto_api import KrakenApiDev

# ============================
# arguments
# ============================
parser = argparse.ArgumentParser(
    prog="launch_get_market.py", description="\n" "Written by E. CHESNEAU"
)
parser.add_argument("--ifile", "-i", help="input xml file")

args = parser.parse_args()

if args.ifile is None or not os.path.isfile(args.ifile):
    print(f"STOP: {args.ifile} is not a file")
    sys.exit()

api = KrakenApiDev(input_path=args.ifile)
api.connect()
api.run()
