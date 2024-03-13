import argparse
from pypilot.__main__ import main

parser = argparse.ArgumentParser(description="Python Pilot - A python terminal assistant")
parser.add_argument("--api-key", help="API key for OPENAI (optional)")
parser.add_argument("--provider", help="API key for OPENAI (optional)", default="openai")


if __name__ == '__main__':
    args = parser.parse_args()
    main(provider=args.provider, api_key=args.api_key)