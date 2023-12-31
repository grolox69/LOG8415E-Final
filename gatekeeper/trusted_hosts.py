import socket
import re

# Configuration data 
trusted_host_ip = "<trusted_host_private_ip>"
trusted_host_port = 50000 # This is the port that the Trusted Host is listening on
proxy_ip = "<proxy_private_ip>"
proxy_port = 60001 # This is the port that the Proxy is listening on

def validate_query(query):
    # Regular expressions for validation of specific SQL operations
    select_pattern = re.compile(r'\bSELECT\s.*\bFROM\s[A-Za-z_][A-Za-z0-9_]*\b', re.IGNORECASE | re.DOTALL)
    insert_pattern = re.compile(r'\bINSERT\sINTO\s[A-Za-z_][A-Za-z0-9_]*\s\(.*\)\sVALUES\s\(.*\);', re.IGNORECASE | re.DOTALL)
    update_pattern = re.compile(r'\bUPDATE\s[A-Za-z_][A-Za-z0-9_]*\sSET\s.*\sWHERE\s.*', re.IGNORECASE | re.DOTALL)
    delete_pattern = re.compile(r'\bDELETE\sFROM\s[A-Za-z_][A-Za-z0-9_]*\sWHERE\s.*', re.IGNORECASE | re.DOTALL)

    # Validate based on the type of operation
    if not (re.search(select_pattern, query) or re.search(insert_pattern, query) or 
            re.search(update_pattern, query) or re.search(delete_pattern, query)):
        print("Invalid query. Operation type not recognized.")
        return False

    print("Query passed basic validation.")
    return True

def forward_query_to_proxy(query):
    """ Forward the validated query to the Proxy. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.connect((proxy_ip, proxy_port))
        proxy_socket.sendall(query.encode("utf-8"))

        # Receive response from Proxy
        response = proxy_socket.recv(1024).decode("utf-8")
        return response

def receive_query():
    """ Listen for incoming connections and receive the query. """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((trusted_host_ip, trusted_host_port))
        server_socket.listen()
        print("Trusted Host listening for connections...")

        while True:
            connection, address = server_socket.accept()
            with connection:
                print(f"Connected to: {address}")
                query = connection.recv(1024).decode("utf-8")
                if not query:
                    continue

                if not validate_query(query):
                    print("Invalid query. Exiting process.")
                    continue

                response = forward_query_to_proxy(query)
                connection.sendall(response.encode("utf-8"))

def main():
    receive_query()

if __name__ == "__main__":
    main()