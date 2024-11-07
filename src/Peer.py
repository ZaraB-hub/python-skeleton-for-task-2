import ipaddress 
import re
# import module tha twill help us work with ipadresses and check to see if valid
# bootstrap nodes staring piint - hardocded 
"""
host
host_formated == host for hostname and ipv4,
              == bracket wrapped ipv6 addres
"""
# each peer object represents a node/another device in the network
class Peer:
    # host_str is the adress( ip or hostname)
    def __init__(self, host_str, port:int):
        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        self.port = port
        self.isBootstrap = False # indicates if this is one of your hardcoded bootstrap nodes
        try:
            ip = None
            # empty var caledd ip
            ip = ipaddress.ip_address(host_str)
            # tries to create an IP address object from ho

            self.host = ip.compressed
            # compacted form
            # ipv4
            self.host_formated = self.host


        # not an ipv, dns name
        except:
            if self.validate_hostname(host_str):
                self.host = host_str
                self.host_formated = host_str
            else: 
                raise ValueError("Not a valid hostname")
        
    
    def validate_hostname(self,hostname):
        pattern = r"^[a-zA-Z\d\.\-\_]{3,50}$"
        return (
            re.match(pattern, hostname)
            and "." in hostname
            and not (hostname.startswith('.') or hostname.endswith('.'))
            and any(c.isalpha() for c in hostname)
        )

    def tagBootstrap(self):
        self.isBootstrap = True

    def __str__(self) -> str:
        return f"{self.host_formated}:{self.port}"

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Peer) and self.host == o.host \
            and self.port == o.port

    def __hash__(self) -> int:
        return (self.port, self.host).__hash__()

    def __repr__(self) -> str:
        return f"Peer: {self}"
