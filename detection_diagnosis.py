


from globals import *

# let's fix 90% accuracy for each attack for now



def detect_UDP_Flood(udp_pkt):
	rnd = random.random(0.0,1)
	if(rnd < globals.UDP_DETECT_ACCURACY):
		# attack packet received
		return True

	return False




def detect_TCP_SYN_Flood(tcp_pkt):
	rnd = random.random(0.0,1)
	if(rnd < globals.TCP_SYN_DETECT_ACCURACY):
		# attack packet received
		return True

	return False




def diagnose_UDP_Flood(pkt):


	if(detect_UDP_Flood(pkt)):
		CURR_TRAFFIC_STATS[pkt.dst]["udp_flood"] += 1



def diagnose_TCP_SYN_Flood(pkt):


	if(detect_TCP_SYN_Flood(pkt)):
		CURR_TRAFFIC_STATS[pkt.dst]["tcp_syn"] += 1




def isUDP(pkt):
	if(pkt.protocol == "UDP"):
		return True
	return False

def isTCP(pkt):
	if(pkt.protocol == "TCP"):
		return True
	return False


def diagnoseTraffic(pkt):

	
	if(pkt.attack_flag == 1):
		if(isUDP(pkt)):
			diagnose_UDP_Flood(pkt)
		
		if(isTCP(pkt)):
			diagnose_TCP_SYN_Flood(pkt)








