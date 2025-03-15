import asyncio
import httpx
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
        
        
    def __generate_ip_list(self) -> list[str]:
        network = ipaddress.IPv4Network(self.subnet, strict=False)
        return [str(ip) for ip in network.hosts()]

    async def __check_device(self, client: httpx.AsyncClient, ip: str,) -> tuple[str, str]:
        url = f"http://{ip}:{self.running_port}/{self.check_endpint}"
        try:
            print(f"checking device: {ip}:{self.running_port}")
            response = await client.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if "name" in data:
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
            print(results)
        return results

if __name__ == "__main__":
    discoverer = DeviceDiscoverer(9000, 2, 'waahCavlo', '10.10.0.0/24')
    devices = asyncio.run(discoverer.scan_network())
    for ip, name in devices:
        print(f"Dispositivo trovato: {ip} -> Nome: {name}")
