from sys import path
import pyshark,time
# https://www.youtube.com/watch?v=1COC92XJluA

def sliding_window_check(window_size: int, threshold:float, paths_to_pcaps: list) -> bool:
    
    packets_to_analyze = []
    try:
        for path in paths_to_pcaps:
            cap = pyshark.FileCapture(path)
            cap.close()
            number_of_packets = len([p for p in cap])
            packets_to_analyze += [cap[i] for i in range(number_of_packets-window_size, number_of_packets)]
    except Exception as e: 
        print('Pyshark error: ', e)
        return False, -1

    number_of_UPDATES_msgs = 0

    for packet in packets_to_analyze:
        if 'BGP' in packet and packet.bgp.type=='2': 
            number_of_UPDATES_msgs+=1
        
    average = number_of_UPDATES_msgs/(window_size*len(paths_to_pcaps))
    return average<threshold, average