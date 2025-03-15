import socket
import json
import threading
import time

class DeviceDiscover:
    def __init__(self, name: str):
        self.__should_run: bool = True
        self.__ip = self.__findLocalIp()
        ip_parts = self.__ip.split('.')
        ip_parts[3] = '255'
        self.__broadcast_address = '.'.join(ip_parts)
        self.__name = name
        self.__listen_port = 9001
        self.__talking_port = 9002

        self.__listen_thread: threading.Thread = threading.Thread(target=self.__listenForHello)
        self.__listen_thread.start()

    def discoverLanDevices(self) -> dict:
        devices_ip = {} 
        message = "Waah Cavlo"
        server_address = (self.__broadcast_address, self.__listen_port) 

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.bind(('0.0.0.0', self.__talking_port))
        client_socket.settimeout(2)

        client_socket.sendto(message.encode('utf-8'), server_address)

        while True:
            try:
                response, server = client_socket.recvfrom(1024)
                ip, port = server
                if ip == self._ip:
                    continue
                data_loaded = json.loads(response)

                if ip not in devices_ip:
                    devices_ip[ip] = data_loaded['name']

            except socket.timeout:
                print("Nessuna risposta dal server entro 5 secondi.")
                break

        client_socket.close()
        return devices_ip
   
    def __findLocalIp(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    
    def __listenForHello(self):
        while self.__should_run:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
            try:
                server_socket.bind(('0.0.0.0', self.__listen_port))
                print("Socket bound, listening for 'Waah Cavlo'...\n\n")

                while self.__should_run:
                    try:
                        message, client_address = server_socket.recvfrom(1024)
                        decoded_message = message.decode('utf-8')

                        if decoded_message == "Waah Cavlo":
                            message = {
                                'name': self.__name,
                            }

                            response = json.dumps(message)
                            server_socket.sendto(response.encode('utf-8'), client_address)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        break 

            except Exception as e:
                print(f"Critical error in listenForHello: {e}")
            finally:
                print("Closing and cleaning up the socket")
                server_socket.close()

            # Add a delay before restarting to avoid rapid restarts
            time.sleep(5)
            print("Restarting the __listenForHello function...")