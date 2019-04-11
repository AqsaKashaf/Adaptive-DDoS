package main

import (
	"math"
	// "time"
)

func enqueuePacket(pkt packet) {

	LOCK_INGRESS_CAP[pkt.ingress].Lock()
	var attackType string
	if pkt.protocol == "udp" {
		attackType = "UDP_FLOOD"
	} else if pkt.protocol == "tcp" {
		attackType = "TCP_SYN"
	} else {
		attackType = "DNS_AMP"
	}
	if (INGRESS_CAP[pkt.ingress][attackType].availableBuffSpace - pkt.packet_len) > 0 {

		INGRESS_CAP[pkt.ingress][attackType].availableBuffSpace -= pkt.packet_len
		// _DEBUG.Printf("Function: enqueuePacket - Packet Added to Queue, Available Buffer space at %d = %f", pkt.ingress, INGRESS_CAP[pkt.ingress].availableBuffSpace)
		enqueue(pkt, pkt.ingress)
		LOCK_INGRESS_CAP[pkt.ingress].Unlock()

	} else {
		LOCK_INGRESS_CAP[pkt.ingress].Unlock()
		dropPacket(pkt)
	}

}

func dropPacket(pkt packet) {

	if pkt.attack_flag == false {

		LOCK_legitimateDropCounter[pkt.ingress].Lock()
		legitimateDropCounter[pkt.ingress] += 1
		_DEBUG.Printf("Function: dropPacket - Legitimate packet dropped, legitimateDropCounter = %d", legitimateDropCounter[pkt.ingress])
		LOCK_legitimateDropCounter[pkt.ingress].Unlock()

		//  	} else {
		// 	attackDropCounter[pkt.ingress] +=1
		//      // # _DEBUG.Printf(f"Function: dropPacket - Attack packet dropped, attackDropCounter = {attackDropCounter[pkt.ingress]}")
	}
}

// func addToBacklog(pkt packet) {

// 	if CONN_IN_BACKLOG == 256 {
// 		fmt.Println("Backlog Full")
// 		dropPacket(pkt)
// 	} else {

// 	Backlog_Queue[pkt.ingress].Add(pkt.src,1,cache.DefaultExpiration)
// 	CONN_IN_BACKLOG+=1
//     }
//  }

// func RemoveFromBacklog(pkt packet) {
//     Backlog_Queue[pkt.ingress].Delete(pkt.src)
//     CONN_IN_BACKLOG-=1
// }

func processPacket(attackType string) {

	for i := 0; i < CONFIGURATION.INGRESS_LOC; i++ {

		LOCK_INGRESS_CAP[i].Lock()

		//pktsToDequeue := int(math.Ceil((INGRESS_CAP[i].vmQueue - INGRESS_CAP[i].availableBuffSpace) / PKT_LEN))
		bitsToDequeue := int(math.Ceil((INGRESS_CAP[i][attackType].vmQueue - INGRESS_CAP[i][attackType].availableBuffSpace)))

		for bitsToDequeue > 0 {
			var pkt packet = dequeue(i)
			// if pkt.synFlag == 1 {
			// 	addToBacklog(pkt)
			// } else if pkt.ackFlag == 1 {
			// 	RemoveFromBacklog(pkt)
			// }
			pkt = diagnose(pkt)
			if pkt.detection == "benign" && pkt.dest == "target" {
				// enqueueTarget(pkt)
				// enqueueOutgoingTarget(pkt)
			}
			if pkt.dest == "attacker" {
				enqueueAttacker(pkt)
			}
			bitsToDequeue -= int(pkt.packet_len)
		}

		INGRESS_CAP[i][attackType].availableBuffSpace += (float64(bitsToDequeue))

		LOCK_INGRESS_CAP[i].Unlock()

	}
}
