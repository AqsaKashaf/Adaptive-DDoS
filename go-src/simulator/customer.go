package main

import (
	"fmt"
	"math"
	"time"

	"../helper/fifo"
	"../helper/go-cache"
)

func initializeTarget() {

	_DEBUG.Printf("Function: initializeTarget")

	tPktQueue = fifo.NewQueue()
	BACKLOG_TARGET = cache.New(5*time.Second, 5*time.Second)
	queueSize := float64(CONFIGURATION.TARGET_PROCESS_CAP) * CONFIGURATION.TARGET_BUFF_SIZE

	dequeueBits := int(math.Ceil(CONFIGURATION.TARGET_PROCESS_CAP / (CONFIGURATION.PROCESSING_DELAY)))

	_DEBUG.Printf("Function: initialize taregt- total processing capacity %d", CONFIGURATION.TARGET_PROCESS_CAP)

	_DEBUG.Printf("Function: initialize taregt - Bits to dequeue = %d", dequeueBits)

	_DEBUG.Printf("Function: initialize TARGET  - Initial queue size = %f", queueSize)
	// _INFO.Printf("BufferSize %f ingress %d", virtual, i)

	// # CONFIGURATION.INGRESS_CAP[i] = math.floor(total_num_vms/CONFIGURATION.INGRESS_LOC)
	TARGET_NETWORK_RESOURCES = new(VM)
	TARGET_NETWORK_RESOURCES.cap = CONFIGURATION.TARGET_PROCESS_CAP
	TARGET_NETWORK_RESOURCES.vmQueue = queueSize
	TARGET_NETWORK_RESOURCES.numOfDequeueBits = dequeueBits
	TARGET_NETWORK_RESOURCES.availableBuffSpace = queueSize

	// change it to calculate link resources
	// ARGET_NETWORK_RESOURCES = new(VM)
	// TARGET_NETWORK_RESOURCES.cap = CONFIGURATION.TARGET_LINK_CAP
	// queueLinkSize := float64(CONFIGURATION.TARGET_LINK_CAP) * CONFIGURATION.TARGET__LINK_BUFF_SIZE
	// TARGET_NETWORK_RESOURCES.vmQueue = queueLinkSize
	// dequeueBits := int(math.Ceil(CONFIGURATION.TARGET_LINK_CAP / (CONFIGURATION.PROCESSING_DELAY)))

	// TARGET_NETWORK_RESOURCES.numOfDequeueBits = dequeueBits
	// TARGET_NETWORK_RESOURCES.availableBuffSpace = queueLinkSize

}

func addToBacklog(pkt packet) {

	if CONN_CUST == 256*int(CONFIGURATION.TARGET_SERVER_CAP) {
		fmt.Println("Backlog Full")
		dropPacketTarget(pkt)
	} else {
		BACKLOG_TARGET.Add(pkt.src, 1, cache.DefaultExpiration)
		CONN_CUST += 1
		fmt.Println(BACKLOG_TARGET.ItemCount())
	}
}

func RemoveFromBacklog(pkt packet) {
	if CONN_CUST > 0 {
		BACKLOG_TARGET.Delete(pkt.src)
		CONN_CUST -= 1
		fmt.Println(BACKLOG_TARGET.ItemCount())
	}
}

func enqueueIncomingTarget(pkt packet) {
	if TARGET_NETWORK_RESOURCES.availableBuffSpace-pkt.packet_len > 0 {
		tPktQueue.Add(pkt)
	} else {
		dropPacketTarget(pkt)
	}

}
func enqueueOutgoingTarget(pkt packet) {
	if TARGET_LINK_RESOURCES.availableBuffSpace-pkt.packet_len > 0 {
		tOutgoingPktQueue.Add(pkt)
	} else {
		dropPacketTarget(pkt)
	}

}

func dequeueTarget() packet {
	return tPktQueue.Next().(packet)
}

func processOutgoingTarget() {
	bitsToDequeue := int(math.Ceil((TARGET_LINK_RESOURCES.vmQueue - TARGET_LINK_RESOURCES.availableBuffSpace)))

	for bitsToDequeue >= 0 {
		var pkt = tOutgoingPktQueue.Next().(packet)

		bitsToDequeue -= int(pkt.packet_len)
		enqueueIncomingTarget(pkt)
	}

	TARGET_LINK_RESOURCES.availableBuffSpace += (float64(bitsToDequeue))
}

func processIncomingTarget() {
	bitsToDequeue := int(math.Ceil((TARGET_NETWORK_RESOURCES.vmQueue - TARGET_NETWORK_RESOURCES.availableBuffSpace)))

	for bitsToDequeue >= 0 {
		var pkt packet = dequeueTarget()

		if pkt.protocol == "ping" {
			var pingPkt packet = NewPacket(64*8, "ping", -1, false)
			pingPkt.dest = pkt.src
			enqueuePacket(pingPkt)
		}
		if pkt.synFlag == 1 {
			addToBacklog(pkt)
		} else if pkt.ackFlag == 1 {
			RemoveFromBacklog(pkt)
		}
		bitsToDequeue -= int(pkt.packet_len)
	}

	TARGET_NETWORK_RESOURCES.availableBuffSpace += (float64(bitsToDequeue))
}

func dropPacketTarget(pkt packet) {

	TargetDropCounter += 1
	_DEBUG.Printf("Function: dropPacket - target packet dropped = %d", TargetDropCounter)

}
