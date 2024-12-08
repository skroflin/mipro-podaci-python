import os
import json
from datetime import datetime
from collections import Counter
import pymysql

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'website_analysis_mipro',
    'port': 3306
}

# Safe float conversion
def safe_float(value, default=0.0):
    try:
        value = str(value).replace(" ms", "").replace(" ms", "").replace("s", "").strip()
        return float(value)
    except (ValueError, AttributeError):
        return default

# Check if a table exists in the database
def check_table_exists(cursor, table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    return result is not None

# Connect to database
db = pymysql.connect(**db_config)
cursor = db.cursor()

# Function to drop and recreate tables
def recreate_tables():
    print("Dropping and recreating tables...")

    # Drop dependent tables first (those with foreign keys)
    if check_table_exists(cursor, 'metrics'):
        cursor.execute("DROP TABLE IF EXISTS metrics;")
    if check_table_exists(cursor, 'https_protocols'):
        cursor.execute("DROP TABLE IF EXISTS https_protocols;")
    if check_table_exists(cursor, 'console_errors'):
        cursor.execute("DROP TABLE IF EXISTS console_errors;")
    if check_table_exists(cursor, 'critical_request_chains'):
        cursor.execute("DROP TABLE IF EXISTS critical_request_chains;")
    
    # Now drop parent table (websites)
    if check_table_exists(cursor, 'websites'):
        cursor.execute("DROP TABLE IF EXISTS websites;")
    print("Tables dropped successfully.")

    # Recreate websites table (parent table)
    cursor.execute("""
    CREATE TABLE websites (
        website_id INT PRIMARY KEY,
        timestamp DATETIME,
        fcp FLOAT,
        lcp FLOAT,
        speed_index FLOAT,
        total_blocking_time FLOAT,
        cls FLOAT,
        server_response_time FLOAT
    );
    """)
    print("\nwebsites table created.")

    # Recreate dependent tables (child tables)
    cursor.execute("""
    CREATE TABLE metrics (
        metric_id INT AUTO_INCREMENT PRIMARY KEY,
        website_id INT,
        metric_name VARCHAR(255),
        metric_value FLOAT,
        FOREIGN KEY (website_id) REFERENCES websites(website_id)
    );
    """)
    print("\nmetrics table created.")

    cursor.execute("""
    CREATE TABLE https_protocols (
        protocol_id INT AUTO_INCREMENT PRIMARY KEY,
        website_id INT,
        protocol_version VARCHAR(50),
        count INT,
        FOREIGN KEY (website_id) REFERENCES websites(website_id)
    );
    """)
    print("\nhttps_protocols table created.")

    cursor.execute("""
    CREATE TABLE console_errors (
        error_id INT AUTO_INCREMENT PRIMARY KEY,
        website_id INT,
        source VARCHAR(255),
        description TEXT,
        timestamp DATETIME,
        FOREIGN KEY (website_id) REFERENCES websites(website_id)
    );
    """)
    print("\nconsole_errors table created.")

    cursor.execute("""
    CREATE TABLE critical_request_chains (
        chain_id INT AUTO_INCREMENT PRIMARY KEY,
        website_id INT,
        total_chains INT,
        total_requests INT,
        max_chain_depth INT,
        total_transfer_size INT,
        longest_chain_duration FLOAT,
        longest_chain_length INT,
        FOREIGN KEY (website_id) REFERENCES websites(website_id)
    );
    """)
    print("\ncritical_request_chains table created.")

# Ensure the tables are recreated
recreate_tables()

def count_chain_depth(chain):
    if not chain.get('children'):
        return 1
    return 1 + max(count_chain_depth(child) for child in chain['children'].values())

def count_total_requests(chain):
    count = 1
    if chain.get('children'):
        for child in chain['children'].values():
            count += count_total_requests(child)
    return count

def calculate_total_transfer_size(chain):
    size = chain.get('request', {}).get('transferSize', 0)
    if chain.get('children'):
        for child in chain['children'].values():
            size += calculate_total_transfer_size(child)
    return size

# Directory and JSON files
current_directory = os.getcwd()
json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]

# Batch insertion for performance
def batch_insert(table, data, cursor):
    """Inserts data into the given table."""
    if table == 'websites':
        query = """
        INSERT INTO websites (
            website_id, timestamp, fcp, lcp, speed_index, total_blocking_time, cls, server_response_time
        ) VALUES (%(website_id)s, %(timestamp)s, %(fcp)s, %(lcp)s, %(speed_index)s, %(total_blocking_time)s, %(cls)s, %(server_response_time)s)
        ON DUPLICATE KEY UPDATE
            timestamp = VALUES(timestamp),
            fcp = VALUES(fcp),
            lcp = VALUES(lcp),
            speed_index = VALUES(speed_index),
            total_blocking_time = VALUES(total_blocking_time),
            cls = VALUES(cls),
            server_response_time = VALUES(server_response_time)
        """
    elif table == 'https_protocols':
        query = """
        INSERT INTO https_protocols (
            website_id, protocol_version, count
        ) VALUES (%(website_id)s, %(protocol_version)s, %(count)s)
        """
    elif table == 'critical_request_chains':
        query = """
        INSERT INTO critical_request_chains (
            website_id, total_chains, total_requests, max_chain_depth, 
            total_transfer_size, longest_chain_duration, longest_chain_length
        ) VALUES (
            %(website_id)s, %(total_chains)s, %(total_requests)s, %(max_chain_depth)s,
            %(total_transfer_size)s, %(longest_chain_duration)s, %(longest_chain_length)s
        )
        """
    elif table == 'console_errors':
        query = """
        INSERT INTO console_errors (
            website_id, source, description, timestamp
        ) VALUES (%(website_id)s, %(source)s, %(description)s, %(timestamp)s)
        """
    else:
        raise ValueError("Unsupported table")

    cursor.executemany(query, data)

# Process each JSON file
def process_json_file(json_file):
    website_id = int(os.path.splitext(os.path.basename(json_file))[0])

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading file {json_file}: {str(e)}")
        return

    # Data for `websites`
    website_data = {
        'website_id': website_id,
        'timestamp': datetime.now(),
        'fcp': safe_float(data.get("FCP (First Contentful Paint)", "0")),
        'lcp': safe_float(data.get("LCP (Largest Contentful Paint)", "0")),
        'speed_index': safe_float(data.get("Speed Index", "0")),
        'total_blocking_time': safe_float(data.get("Total Blocking Time (TBT)", "0")),
        'cls': safe_float(data.get("CLS (Cumulative Layout Shift)", "0")),
        'server_response_time': safe_float(data.get("Server Response Time", "0"))
    }
    batch_insert('websites', [website_data], cursor)

    # Data for `https_protocols`
    protocol_counts = Counter(data.get("HTTPS Protocols", []))
    protocols_data = [
        {'website_id': website_id, 'protocol_version': protocol, 'count': count}
        for protocol, count in protocol_counts.items()
        if protocol
    ]
    batch_insert('https_protocols', protocols_data, cursor)

    # Data for `critical_request_chains`
    critical_chains = data.get("Critical Request Chains")
    
    if isinstance(critical_chains, str):
        chains_data = {
            'website_id': website_id,
            'total_chains': 0,
            'total_requests': 0,
            'max_chain_depth': 0,
            'total_transfer_size': 0,
            'longest_chain_duration': 0,
            'longest_chain_length': 0
        }
        print(f"Storing zero metrics for {json_file} due to error: {critical_chains}")
        batch_insert('critical_request_chains', [chains_data], cursor)
        return
    
    if isinstance(critical_chains, dict) and "chains" in critical_chains:
        chains = critical_chains.get("chains", {})
        try:
            chains_data = {
                'website_id': website_id,
                'total_chains': len(chains),
                'total_requests': sum(count_total_requests(chain) for chain in chains.values()),
                'max_chain_depth': max(count_chain_depth(chain) for chain in chains.values()) if chains else 0,
                'total_transfer_size': sum(calculate_total_transfer_size(chain) for chain in chains.values()),
                'longest_chain_duration': float(critical_chains.get('longestChain', {}).get('duration', 0)),
                'longest_chain_length': int(critical_chains.get('longestChain', {}).get('length', 0))
            }
            print(f"Successfully processed chains data for {json_file}")
            batch_insert('critical_request_chains', [chains_data], cursor)
        except Exception as e:
            print(f"Error processing chains for {json_file}: {str(e)}")
            
    else:
        chains_data = {
            'website_id': website_id,
            'total_chains': 0,
            'total_requests': 0,
            'max_chain_depth': 0,
            'total_transfer_size': 0,
            'longest_chain_duration': 0,
            'longest_chain_length': 0
        }
        print(f"Storing zero metrics for {json_file} - Invalid or missing data")
        batch_insert('critical_request_chains', [chains_data], cursor)

    # Data for `console_errors`
    errors = data.get("Console Errors", [])
    errors_data = [
        {
            'website_id': website_id,
            'source': error.get("source", ""),
            'description': error.get("description", ""),
            'timestamp': datetime.now()
        }
        for error in errors
    ]
    batch_insert('console_errors', errors_data, cursor)

# Limit file processing for testing
for json_file in json_files:  # Process only 50 files for testing
    process_json_file(json_file)

# Commit changes and close connection
db.commit()
cursor.close()
db.close()
