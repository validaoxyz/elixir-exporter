# Elixir Prom Exporter

This script parses Docker logs from an elixir validator, extracts relevant metrics, and exposes them for Prometheus on port 8086.

## Features

- **Metrics Collection**: Counts and gauges various metrics like data frames processed, proposal requests, connect requests, order adjustments, and more.
- **Validator Information**: Captures validator-specific details such as software version, beneficiary address, validator address, and uptime percentage.
- **Error Tracking**: Logs and counts errors encountered during parsing.

## Prometheus Metrics

- **Counters**
  - `data_frames_processed`: Tracks data frames processed, labeled by `exchange` and `symbol`.
  - `proposal_requests_sent` and `proposal_responses_received`: Counts for proposal requests and responses.
  - `connect_requests_sent` and `authorization_requests_sent`: Counts connect and authorization requests.
  - `strategy_executions`, `order_level_adjustments`, and `transaction_cost_adjustments`: Tracks various trading actions.
  - `error_count`: Counts the number of errors encountered.

- **Gauges**
  - `spread`: Spread between bid and ask prices.
  - `position`, `volatility`, `bid_price`, `ask_price`: Market data values for each symbol.
  - `uptime_percentage`: Validator uptime percentage.

- **Rate Metrics**
  - `Rate of Data Frames Processed`: Calculates the rate of data frames processed per 5 minutes, indicating market activity and throughput.
  - `Rate of Proposal Requests and Responses:`: 
    - `Request Rate`: Measures the rate of proposal requests sent, highlighting consensus participation.
    - `Response Rate`: Measures the rate of proposal responses received, indicating network health and response handling.
  - `Rate of Strategy Executions:`: Tracks how often the validator executes strategies, providing insights into operational efficiency and strategy   effectiveness.
  - `Rate of Authorization Requests Sent:`: Monitors the frequency of authorization requests, useful for tracking communication and security interactions over time.

- **Info**
  - `validator_info`, `software_version`, `beneficiary_address`, `validator_address`: Stores basic information about the validator.

## Usage

1. **Install Dependencies**: Ensure you have `prometheus_client`, `logging`, and `re` installed.
   ```bash
   pip install prometheus_client
   ```

2. **Run the Script**
    ```bash
    python elixir-exporter.py
    ```
    This starts the Prometheus server on port 8086 and begins tailing Docker logs for metrics.
3. **Access Prom metrics**
   ```bash
   curl http://localhost:8086/metrics to view the metrics.
   ```

## Example dashboard
![grafana-dashboard](https://github.com/user-attachments/assets/606ae1f4-c71b-4bce-80bb-33aea28244b4)


## Logging
Logs are set to WARNING level by default but can be adjusted within the `logging.basicConfig` setup.
