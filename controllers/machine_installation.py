import nmap

def test():
    nm = nmap.PortScanner()
    hosts = nm.scan(hosts='192.168.1.0/24', arguments='-n -sP -PE -PA21,23,80,3389')
    return hosts
    for host in nm.all_hosts():
        print('Host : %s (%s)' % (host, nm[host].hostname()))
        print('State : %s' % nm[host].state())
        for proto in nm[host].all_protocols():
            print('----------')
            print('Protocol : %s' % proto)

            lport = nm[host][proto].keys()
            lport.sort()
            for port in lport:
                print('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))
