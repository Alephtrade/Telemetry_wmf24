import nmap

def test():
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='10.8.0.0/24', arguments='-sn')

    for host in hosts["scan"]:
        return host