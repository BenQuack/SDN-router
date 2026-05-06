import requests
import sys
import json

def format_topology(topo_string:str) -> dict:
    """
    formats a JSON object into a dictionary where the key
    is the switch id and each item in the list is a tuple where
    the first item is the switch it is connected to and 
    the second is the port to reach the destination switch
    """
    topo_list = json.loads(topo_string)['connected']

    switches = dict()
    for switch in topo_list:
        if switch[0] in switches.keys():
            switches[switch[0]].append(switch[-2:])
        else:
            switches[switch[0]] = [switch[-2:]]

    return switches

def bsf(graph:dict, s:str):
    seen = []
    queue = []
    queue.append(s)
    while queue:
        node = queue.pop(0)
        seen.append(node)
        for connection in graph[node]:
            if connection[0] not in seen and connection[0] not in queue:
                queue.append(connection[0])
                print(queue)

def scan(switches:dict) -> str:
    """
    scans the list of lists <topo_list> and returns 
    a string containing the fowarding tables for each switch 
    """
    hosts = [item for item in switches.keys() if isinstance(item,str)]
    bsf(switches,hosts[0])
    return

def app():
    return 0

def main():
    """
    if len(sys.argv) != 2:
        if len(sys.argv) == 1:
            print("agrument expected after sdn-routing-app.py <network to scan>")
            return ValueError
        else:
            print("no agrument(s) expected after sdn-routing-app.py other than <network to scan>")
    """
    
    dit = format_topology(requests.get(f'http://sdn.cs3650.org/get_topology/topology1').text)
    scan(dit)
    return 0


if __name__ == '__main__':
    main()



