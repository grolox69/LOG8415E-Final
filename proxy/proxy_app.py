import socket
import random
import re
import mysql.connector
from ping3 import ping

import json

def load_config(file_path):
    """ Load configuration from a JSON file. """
    with open(file_path, 'r') as file:
        return json.load(file)

# Load configuration from the JSON file
CONFIG = load_config('proxy_config.json')

def prepare_ips():
    # TODO: Prepare config file before scp script
    pass

def mysql_connect(node_ip):
    """ Connect to MySQL node. """
    try:
        cnx = mysql.connector.connect(
            host=node_ip,
            user=CONFIG["mysql_user"],
            password=CONFIG["mysql_password"],
            database=CONFIG["database_name"]
        )
        return cnx
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def execute_query(node_ip, query):
    """ Execute a query on a specified MySQL node. """
    cnx = mysql_connect(node_ip)
    if cnx:
        try:
            cursor = cnx.cursor()
            cursor.execute(query)
            if cursor.with_rows:
                return cursor.fetchall()
            print(f"Query executed successfully on {node_ip}")
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cnx.close()
    else:
        print(f"Unable to connect to {node_ip}")

def measure_ping(ip):
    """ Measure ping time to a given IP. """
    try:
        return ping(ip)
    except Exception as e:
        print(f"Error measuring ping to {ip}: {e}")
        return float('inf')

def is_write_query(query):
    """ Determine if a query is a write operation. """
    return re.match(r'\b(INSERT|UPDATE|DELETE)\b', query, re.IGNORECASE) is not None

def select_node(query, use_customized_logic=False):
    """ Select the appropriate node for a given query. """
    if is_write_query(query): # Direct hit
        return CONFIG["mysql_master_ip"]
    else:
        if use_customized_logic: # Customized logic
            # Choose node based on lowest ping time
            ping_times = {ip: measure_ping(ip) for ip in CONFIG["mysql_slave_ips"]}
            return min(ping_times, key=ping_times.get)
        else: # Randomized logic
            # Randomly select a slave node
            return random.choice(CONFIG["mysql_slave_ips"])

def handle_client_query(client_socket):
    """ Receive and process query from the client. """
    data = client_socket.recv(1024).decode("utf-8")
    if not data:
        print("No query received.")
        return

    # Decide whether to use customized logic or not
    use_customized_logic = True  # Set to False to use random selection

    node_ip = select_node(data, use_customized_logic)
    results = execute_query(node_ip, data)
    client_socket.sendall(str(results).encode("utf-8"))

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((CONFIG["proxy_ip"], CONFIG["proxy_port"]))
        server_socket.listen()
        print("Proxy listening for connections...")

        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                print(f"Connected to: {addr}")
                handle_client_query(client_socket)

if __name__ == "__main__":
    main()