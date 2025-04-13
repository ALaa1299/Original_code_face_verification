import socket

def check_host_connection(host='host.docker.internal', port=8080):
    """Check if the host is reachable."""
    try:
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        return True
    except OSError:
        return False

if __name__ == "__main__":
    if check_host_connection():
        print("Host is reachable.")
    else:
        print("Host is not reachable.")
