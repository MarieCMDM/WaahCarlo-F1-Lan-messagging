import asyncio
import httpx
import socket
import ipaddress

class DeviceDiscoverer:
    def __init__(self, port: int, connection_timeout: int, endpoint: str, subnet: str  = None) -> None:
        if subnet == None:
            #TODO autodiscover
            raise Exception("For now subnet must be specified")

        self.subnet = subnet
        self.timeout = connection_timeout
        self.running_port = port
        self.check_endpint = endpoint
        self.ip = self.__find_local_ip()
        
    def __find_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
        
    def __generate_ip_list(self) -> list[str]:
        network = ipaddress.IPv4Network(self.subnet, strict=False)
        return [str(ip) for ip in network.hosts()]

    async def __check_device(self, client: httpx.AsyncClient, ip: str,) -> tuple[str, str]:
        if ip == self.ip:
            return None
        url = f"http://{ip}:{self.running_port}/{self.check_endpint}"
        try:
            response = await client.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "name" in data:
                    print(f"Found device: {ip}:{self.running_port}")
                    return ip, data["name"]
        except (httpx.HTTPError, ValueError):
            print(f"No response from: {ip}:{self.running_port}")
            return None

    async def scan_network(self) -> list[tuple]:
        ip_list = self.__generate_ip_list()
        results = []

        async with httpx.AsyncClient() as client:
            tasks = [self.__check_device(client, ip) for ip in ip_list]
            responses = await asyncio.gather(*tasks)
            results = [res for res in responses if res]
        return results
