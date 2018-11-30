


# this file will be used to have a notion of legitimate traffic
# how much legtimate traffic is received at any given time
# what is the latency observed and all those things will be modeled here
import packet
import globals
import time
import network
import logging

def flowGen():
	globals.DEBUG_LOGGER.debug("Function: flowGen")
	if(globals.LEG_TRAFFIC_MODEL == "simple"):
		flowGenSimple()

def sendPkts(n):
	for i in range(0,n):
		network.sendtoNetwork(packet.Packet(globals.PKT_LEN,"udp",0,0))

def flowGenSimple():
	globals.DEBUG_LOGGER.debug("Function: flowGenSimple")
	fixedRate = 1000000 # 1 Mbps
	numPkts = int(fixedRate / globals.PKT_LEN)
	while True:
		sendPkts(numPkts)
		time.sleep(1)
		# network.sendtoNetwork(pkt)





# def randFlowGen():
  
