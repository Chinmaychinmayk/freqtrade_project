Freqtrade Project


Installation
Prerequisites

Docker: Install Docker Desktop from docker.com.
Git: Install Git from git-scm.com.
Python 3.12+: Optional for local Freqtrade setup (if not using Docker).
Homebrew (macOS): For installing dependencies./bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"



Setup with Docker

Clone the Repository:
git clone <your-repository-url>
cd freqtrade_project


Create Directory Structure:Ensure the ft_userdata directory exists:
mkdir -p ft_userdata/strategies ft_userdata/data/binance ft_userdata/logs


Pull Freqtrade Docker Image:
docker compose pull


Download Historical Data:Download Binance data for BTC/USDT and ETH/USDT (1h, 30m) for 2023-01-01 to 2024-01-01:
docker compose run --rm freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 1h 30m --timerange 20230101-20240101 --erase --data-dir user_data/data/binance


Verify Data:
docker compose run --rm freqtrade list-data --config user_data/config_pair.json --show-timerange



Configure:Copy config_pair.json to ft_userdata/ and adjust settings as needed.


Executing Strategies
BreakoutStrategy
Description: A momentum-based strategy that enters long positions when the price breaks above a 20-period high, using a 3-period low for a trailing stoploss. Designed for spot markets, it relies on price momentum for entries and custom stoploss for exits.
Execution:

Ensure Configuration:Verify config_pair.json includes strategy: "BreakoutStrategy".
nano ft_userdata/config_pair.json


Backtest (1h Timeframe):
docker compose run --rm freqtrade backtesting --strategy BreakoutStrategy --config user_data/config_pair.json --timeframe 1h --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades


Backtest (30m Timeframe):
docker compose run --rm freqtrade backtesting --strategy BreakoutStrategy --config user_data/config_pair.json --timeframe 30m --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades


Dry-Run:
docker compose up -d



PairBreakoutStrategy
Description: A correlation-based strategy that enters long positions in ETH/USDT when BTC/USDT’s price breaks above a 20-period high. It uses a 3-period low for stoploss and is designed for spot markets, leveraging BTC/ETH price correlation.
Execution:

Ensure Configuration:Verify config_pair.json includes strategy: "PairBreakoutStrategy".
nano ft_userdata/config_pair.json


Backtest (1h Timeframe):
docker compose run --rm freqtrade backtesting --strategy PairBreakoutStrategy --config user_data/config_pair.json --timeframe 1h --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades


Backtest (30m Timeframe):
docker compose run --rm freqtrade backtesting --strategy PairBreakoutStrategy --config user_data/config_pair.json --timeframe 30m --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades


Dry-Run:
docker compose up -d



