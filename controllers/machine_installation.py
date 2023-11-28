import nmap


def test():
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='10.8.0.0/24', arguments='-sn')
    ips = []
    for host in hosts["scan"]:
        ips.append(host)

    return ips
