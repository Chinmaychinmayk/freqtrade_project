# Freqtrade Project

This repository provides a Freqtrade setup for backtesting and running trading strategies (`BreakoutStrategy` and `PairBreakoutStrategy`) on Binance spot markets. It includes configuration files, strategy scripts, and instructions for Docker-based installation.

## Installation

### Prerequisites
- **Docker**: Install Docker Desktop from [docker.com](https://www.docker.com/get-started).
- **Git**: Install Git from [git-scm.com](https://git-scm.com/downloads).
- **Homebrew** (macOS, optional for dependencies):
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- **Python 3.12+**: Optional for local Freqtrade setup (not required for Docker).

### Setup with Docker

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Chinmaychinmayk/freqtrade_project.git
   cd freqtrade_project
   ```

2. **Create Directory Structure**:
   Ensure the `ft_userdata` directories exist:
   ```bash
   mkdir -p ft_userdata/strategies ft_userdata/data/binance ft_userdata/logs
   ```

3. **Pull Freqtrade Docker Image**:
   ```bash
   docker compose pull
   ```

4. **Download Historical Data**:
   Download Binance spot data for BTC/USDT and ETH/USDT (1h, 30m) for 2023-01-01 to 2024-01-01:
   ```bash
   docker compose run --rm freqtrade download-data --exchange binance --pairs BTC/USDT ETH/USDT --timeframes 1h 30m --timerange 20230101-20240101 --erase --data-dir user_data/data/binance
   ```

5. **Verify Data**:
   Check downloaded data:
   ```bash
   docker compose run --rm freqtrade list-data --config user_data/config_pair.json --show-timerange
   ```

6. **Configure**:
   - Copy `config_pair.json` to `ft_userdata/` if not present.
   - Verify settings in `ft_userdata/config_pair.json`:
     ```bash
     nano ft_userdata/config_pair.json
     ```
   - Ensure `exchange.name` is `"binance"`, `pairlists` includes `"BTC/USDT"` and `"ETH/USDT"`, and `strategy` is set to `"BreakoutStrategy"` or `"PairBreakoutStrategy"`.

### Executing Strategies

#### BreakoutStrategy
- **Description**: Enters long positions when the price breaks above a 20-period high, using a 3-period low for a trailing stoploss. Suited for spot markets, it captures price momentum.
- **Execution**:
  1. Set `strategy: "BreakoutStrategy"` in `ft_userdata/config_pair.json`.
     ```bash
     nano ft_userdata/config_pair.json
     ```
  2. Backtest (1h):
     ```bash
     docker compose run --rm freqtrade backtesting --strategy BreakoutStrategy --config user_data/config_pair.json --timeframe 1h --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades
     ```
  3. Backtest (30m):
     ```bash
     docker compose run --rm freqtrade backtesting --strategy BreakoutStrategy --config user_data/config_pair.json --timeframe 30m --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades
     ```
  4. Dry-Run:
     ```bash
     docker compose up -d
     ```

#### PairBreakoutStrategy
- **Description**: Enters long positions in ETH/USDT when BTC/USDT breaks above a 20-period high, using a 3-period low stoploss. Designed for spot markets, it leverages BTC/ETH correlation.
- **Execution**:
  1. Set `strategy: "PairBreakoutStrategy"` in `ft_userdata/config_pair.json`.
     ```bash
     nano ft_userdata/config_pair.json
     ```
  2. Backtest (1h):
     ```bash
     docker compose run --rm freqtrade backtesting --strategy PairBreakoutStrategy --config user_data/config_pair.json --timeframe 1h --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades
     ```
  3. Backtest (30m):
     ```bash
     docker compose run --rm freqtrade backtesting --strategy PairBreakoutStrategy --config user_data/config_pair.json --timeframe 30m --timerange 20230101-20240101 --dry-run-wallet 1000 --export trades
     ```
  4. Dry-Run:
     ```bash
     docker compose up -d
     ```

## Notes
- **Data**: Historical data is stored in `ft_userdata/data/binance/`. Ensure data is downloaded before backtesting.
- **Backtest Results**: Saved in `ft_userdata/backtest_results/`.
- **Logs**: Check `ft_userdata/logs/` or `ft_userdata/freqtrade.log` for debugging.
- **docker-compose.yml**: Ensure no `version` attribute to avoid warnings:
  ```bash
  nano docker-compose.yml
  ```
