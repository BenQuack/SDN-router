import requests
import sys
import json

def format_topology(topo_string:str) -> dict:
    """
    formats a JSON object into a dictionary where the key
    is the switch id and each entry contains a dictionary
    where the keys are the switch ids and the values are the 
    ports to reach the switch
    """
    topo_list = json.loads(topo_string)['connected']

    switches = dict()
    for switch in topo_list:
        if switch[0] in switches.keys():
            switches[switch[0]][switch[1]] = switch[2]
        else:
            switches[switch[0]] = {switch[1]:switch[2]}
        

    return switches

def sort_assist(e):
    try:
        return int(e[0])
    except:
        s = e[0].replace('.','')
        return int(s)

def bsf(graph:dict, s:str):
    seen = []
    queue = []
    send_back_port = {}
    queue.append(s)
    while queue:
        node = queue.pop(0)
        seen.append(node)

        for connection in graph[node].keys():
            neighbor = connection

            if (neighbor not in seen and 
                neighbor not in queue and 
                not isinstance(neighbor,str)):

                send_back_port[neighbor] = graph[neighbor][node]
                queue.append(neighbor)
    
    return send_back_port

def scan(switches:dict) -> str:
    """
    scans the list of lists <topo_list> and returns 
    a string containing the fowarding tables for each switch 
    """
    hosts = [item for item in switches.keys() if isinstance(item,str)]
    switches_no_hosts = [item for item in switches.keys() if item not in hosts]
    paths = {}
    tables_entries = []
    for host in hosts:                         
        path = bsf(switches, host)
        for switch_id in switches_no_hosts:
            if switch_id in path:              
                table_entry = {
                    "switch_id": int(switch_id),    
                    "dst_ip": host,
                    "out_port": int(path[switch_id]) 
                }
                tables_entries.append(table_entry)

    return {"table_entries":tables_entries}


def main():
    
    if len(sys.argv) != 2:
        if len(sys.argv) == 1:
            print("agrument expected after sdn-routing-app.py <network to scan>")
            return ValueError
        else:
            print("no agrument(s) expected after sdn-routing-app.py other than <network to scan>")
    
    
    # get_request = requests.get(f'http://sdn.cs3650.org/get_topology/topology1')
    
    try:
        get_request = requests.get(f'http://sdn.cs3650.org/get_topology/{sys.argv[1]}')
        print(get_request.status_code)
    except requests.exceptions.Timeout:
        print("The request timed out")

    topology_text = get_request.text
    topology_dict = format_topology(topology_text)
    switch_tables_dict = scan(topology_dict)
    response = requests.post("http://sdn.cs3650.org/set_tables/topology1",json=switch_tables_dict)
    if response.status_code // 100 == 2: # check for a successfull response 
        print("data sent successfully")
    else:
        print("There was an error with the server")
    return 0


if __name__ == '__main__':
    main()



