import globals 
# import queue


class VM ():
	def __init__(self,cap,vm_queue, dp,space):
		self.cap = cap
		self.vmQueue = vm_queue
		self.numOfDequeuePkts = dp
		self.availableBuffSpace = space
		# self.vm_ports = globals.NUM_PORTS_VM

