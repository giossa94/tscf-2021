from sys import path
import pyshark
# https://www.youtube.com/watch?v=1COC92XJluA

class sliding_window:
    def __init__(self,window_size,threshold):
        self.window_size = window_size
        self.threshold = threshold
        self.last_id_pcap = {}
    
    def sliding_window_check(self, paths_to_pcaps: list) -> bool:
        """
            Runs the sliding window check for node convergence.
            Codes:
                0 - The node has not yet converged.
                1 - The node has converged.
                2 - The node has not received enough packets to consider a window.
                3 - The node has not received enough *new* packets to consider a not overlaping window.
        """
        
        number_of_packets_pcaps = {} # key: pcap, value: number of packets

        packets_to_analyze = []
        for path in paths_to_pcaps:
            try:
                cap = pyshark.FileCapture(path)
                cap.close()
            except Exception as e:
                raise Exception("Pyshark error: " + str(e)) 


            number_of_packets_pcaps[path] = len([p for p in cap])

            if number_of_packets_pcaps[path]-self.window_size < 0:
                return {'average': -1, 'status': "Not enough packets to consider the first window.", 'code': 2}


            packets_to_analyze += [cap[i] for i in range(number_of_packets_pcaps[path]-self.window_size, number_of_packets_pcaps[path])]
            
            # Initialize last id for this pcap
            if path not in self.last_id_pcap:
                self.last_id_pcap[path] = 0

        # If some of the pcaps does not have enough packets to build a new window then skip
        for path in paths_to_pcaps:
            if self.last_id_pcap[path]+self.window_size > number_of_packets_pcaps[path]:
                return {'average': -1, 'status':'Not enough new packets to consider a new window.', 'code': 3}

        # Count the number of UPDATE messages among the considered packets
        number_of_UPDATES_msgs = 0
        for packet in packets_to_analyze:
            if 'BGP' in packet and packet.bgp.type=='2': 
                number_of_UPDATES_msgs+=1

        # Update last id for each pcap analyzed
        for path in paths_to_pcaps:
            self.last_id_pcap[path] = number_of_packets_pcaps[path]

        average = number_of_UPDATES_msgs/(self.window_size*len(paths_to_pcaps))
        
        if average<self.threshold:
            result = {'average': average, 'status':'Converged.', 'code': 1}
        else:
            result = {'average': average, 'status':'Still converging.', 'code': 0}

        return result