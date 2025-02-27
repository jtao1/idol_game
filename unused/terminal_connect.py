import socket
import threading

def receive_messages(conn):
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Received: {data}")
        except ConnectionResetError:
            print("Connection lost.")
            break

def send_messages(conn):
    while True:
        message = input("Your message: ")
        conn.sendall(message.encode())
        if message.lower() == 'quit':
            break

def start_p2p(host, port, peer_host, peer_port):
    # Set up the socket to listen for incoming connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening for connections on {host}:{port}")

        # Connect to the peer
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        print(f"Connected to peer at {peer_host}:{peer_port}")

        # Accept an incoming connection
        conn, addr = s.accept()
        print(f"Connected by {addr}")

        # Start threads for sending and receiving messages
        receive_thread = threading.Thread(target=receive_messages, args=(conn,))
        send_thread = threading.Thread(target=send_messages, args=(peer_socket,))

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

if __name__ == "__main__":
    # Replace these with the actual IP addresses and ports for both machines
    YOUR_IP = socket.gethostbyname(socket.gethostname())  # Replace with this machine's IP
    YOUR_PORT = 65432          # Replace with this machine's port
    PEER_IP = '100.69.9.232'  # Replace with the other machine's IP
    PEER_PORT = 65432          # Replace with the other machine's port

    start_p2p(YOUR_IP, YOUR_PORT, PEER_IP, PEER_PORT)