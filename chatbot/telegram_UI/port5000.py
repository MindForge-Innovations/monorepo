import socket

def main():
    # Host and port to listen on
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 5000

    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Bind the socket to the address and port
        server_socket.bind((SERVER_HOST, SERVER_PORT))

        # Start listening for incoming connections
        server_socket.listen(5)
        print("Server listening on port", SERVER_PORT)

        while True:
            # Accept incoming connections
            client_socket, client_address = server_socket.accept()
            print("Connected to client:", client_address)

            # Receive data from the client
            data = client_socket.recv(1024)
            print("Received from client:", data.decode())

            # Process the data
            response = data.decode() #"system answer"

            # Send the response back to the client
            client_socket.sendall(response.encode())

            # Close the client socket
            client_socket.close()

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the server socket
        server_socket.close()

if __name__ == "__main__":
    main()
