import re
import subprocess
import logging
from prometheus_client import start_http_server, Counter, Gauge, Histogram, Info

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Prometheus metrics
data_frame_counter = Counter('data_frames_processed', 'Number of data frames processed', ['exchange', 'symbol'])
proposal_request_counter = Counter('proposal_requests_sent', 'Number of proposal requests sent')
proposal_response_counter = Counter('proposal_responses_received', 'Number of proposal responses received')
connect_request_counter = Counter('connect_requests_sent', 'Number of connect requests sent')
authorization_request_counter = Counter('authorization_requests_sent', 'Number of authorization requests sent')
strategy_execution_counter = Counter('strategy_executions', 'Number of strategy executions')
order_level_adjustment_counter = Counter('order_level_adjustments', 'Number of order level adjustments')
transaction_cost_adjustment_counter = Counter('transaction_cost_adjustments', 'Number of transaction cost adjustments')

spread_gauge = Gauge('spread', 'Spread between bid and ask prices', ['symbol'])
position_gauge = Gauge('position', 'Current position', ['symbol'])
volatility_gauge = Gauge('volatility', 'Current volatility', ['symbol'])
bid_gauge = Gauge('bid_price', 'Current bid price', ['symbol'])
ask_gauge = Gauge('ask_price', 'Current ask price', ['symbol'])

error_counter = Counter('error_count', 'Number of errors encountered')

validator_info = Info('validator_info', 'Information about the validator')
software_version = Info('software_version', 'Software version of the validator')
beneficiary_address = Info('beneficiary_address', 'Beneficiary address of the validator')
validator_address = Info('validator_address', 'Address of the validator')
uptime_percentage = Gauge('uptime_percentage', 'Uptime percentage of the validator')

def parse_log_line(line):
    try:
        # Count data frames
        if 'processing incoming data frame' in line:
            exchange_symbol_match = re.search(r'data_frame_id=([\w\.]+)-([\w-]+)-', line)
            if exchange_symbol_match:
                exchange, symbol = exchange_symbol_match.groups()
                data_frame_counter.labels(exchange=exchange, symbol=symbol).inc()

        # Count proposal requests and responses
        if 'sending proposal request' in line:
            proposal_request_counter.inc()
        elif 'received proposal response' in line:
            proposal_response_counter.inc()

        # Count connect and authorization requests
        if 'sending connect request' in line:
            connect_request_counter.inc()
        elif 'sending authorization request' in line:
            authorization_request_counter.inc()

        # Count strategy executions
        if '[strategy_executor]' in line:
            strategy_execution_counter.inc()

        # Count order level adjustments and transaction cost adjustments
        if 'order levels' in line:
            order_level_adjustment_counter.inc()
        elif 'transaction cost adjustment' in line:
            transaction_cost_adjustment_counter.inc()

        # Extract and update market data metrics
        metrics_match = re.search(r'bb=([\d\.]+)\|ba=([\d\.]+)\|ob=([\d\.]+)\|oa=([\d\.]+)\|q=([\d\.-]+)\|pos=([\d\.-]+)\|vol=([\d\.]+)', line)
        if metrics_match:
            bb, ba, ob, oa, q, pos, vol = map(float, metrics_match.groups())
            symbol_match = re.search(r'data_frame_id=[\w\.]+-([\w-]+)-', line)
            if symbol_match:
                symbol = symbol_match.group(1)
                spread_gauge.labels(symbol=symbol).set(ba - bb)
                position_gauge.labels(symbol=symbol).set(float(pos))
                volatility_gauge.labels(symbol=symbol).set(float(vol))
                bid_gauge.labels(symbol=symbol).set(bb)
                ask_gauge.labels(symbol=symbol).set(ba)

        # Extract validator info
        if 'SOFTWARE VERSION:' in line:
            version = line.split(':')[1].strip()
            software_version.info({'version': version})
        elif 'DISPLAY NAME:' in line:
            display_name = line.split(':')[1].strip()
            validator_info.info({'display_name': display_name})
        elif 'BENEFICIARY:' in line:
            beneficiary = line.split(':')[1].strip()
            beneficiary_address.info({'address': beneficiary})
        elif 'VALIDATOR ADDRESS:' in line:
            address = line.split(':')[1].strip()
            validator_address.info({'address': address})
        elif 'uptime for today as' in line:
            uptime_match = re.search(r'uptime for today as (\d+\.\d+)%', line)
            if uptime_match:
                uptime_percentage.set(float(uptime_match.group(1)))

        # Count errors
        if '[error]' in line.lower():
            error_counter.inc()

    except Exception as e:
        logger.error(f"Error parsing log line: {e}")
        error_counter.inc()

def tail_docker_logs():
    cmd = "docker logs -f elixir"
    logger.info(f"Starting to tail Docker logs with command: {cmd}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            parse_log_line(output.strip())

if __name__ == '__main__':
    # Start up the server to expose the metrics on port 8086
    start_http_server(8086)
    logger.info("Started Prometheus metrics server on port 8086")

    # Start tailing Docker logs
    logger.info("Starting to tail Docker logs")
    tail_docker_logs()