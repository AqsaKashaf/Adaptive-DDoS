package main

import (
	"log"
	"math"
	"math/rand"
	"time"
)

var dest int
var lastPingSent time.Time

func ping(ingress int) {
	var pingPkt = NewPacket(64*8, "ping", ingress, false)
	pingPkt.dest = "target"
	lastPingSent = time.Now()
	enqueuePacket(pingPkt)

}
func calculateRTT(pkt packet) {
	t := time.Now()
	RTT = t.Sub(lastPingSent)
}
func enqueueAttacker(pkt packet) {
	if pkt.protocol == "ping" {
		calculateRTT(pkt)
	}
}

func attack() {
	if CONFIGURATION.ATTACK_TYPE == "randIngress" {
		randIngress()
	} else if CONFIGURATION.ATTACK_TYPE == "randMix" {
		randAttackMix()
	} else {
		log.Fatal("ATTACK TYPE UNKNOWN")
	}
}
func amplify(pkt packet) packet {
	//ampFactor := 10.0
	max := 10.0
	min := 5.0
	ampFactor := min + (rand.Float64() * (max - min))
	pkt.packet_len = ampFactor * pkt.packet_len
	return pkt
}

// func sendToRandIngress(n int) {
// 	// dst :=
// 	// pkt := NewPacket(PKT_LEN, "udp", rand.Intn(CONFIGURATION.INGRESS_LOC), true)
// 	for i := 0; i < n; i++ {

// 		// # network.sendtoNetwork(pkt)
// 		// }
// 		//
// 		// for i := 0; i < n; i++ {
// 		// 	// sendtoNetwork(NewPacket(PKT_LEN,"udp",0,0))

// 		enqueuePacket(NewPacket(PKT_LEN, "udp", dest, true))
// 	}
// }
func randIngress() {
	fixedCap := CONFIGURATION.ATTACKER_CAP //Mb per epoch
	numPkts := int(math.Ceil(fixedCap / (PKT_LEN)))
	dest = rand.Intn(CONFIGURATION.INGRESS_LOC)
	_DEBUG.Printf("Function: randIngress - Number of packets to send in 1 second %d with packet length %f and send rate %f", numPkts, PKT_LEN, fixedCap)
	for {
		// go sendToRandIngress(numPkts)
		go sendPktsProtocol(numPkts, dest, "dns")

		time.Sleep(1 * time.Second)
		dest = rand.Intn(CONFIGURATION.INGRESS_LOC)
		// time.Sleep(time.Duration(CONFIGURATION.EPOCH_TIME) * time.Second)
		// # network.sendtoNetwork(pkt)
	}
}

func sendPktsProtocol(n int, ingress int, protocol string) {
	_DEBUG.Printf("Function: sendPktsProtocol - protocol is %s, total pkts to send is %v and ingress is %v", protocol, n, ingress)
	for i := 0; i < n; i++ {
		// sendtoNetwork(NewPacket(PKT_LEN,"udp",0,0))
		if protocol == "udp" {
			enqueuePacket(NewPacket(PKT_LEN, protocol, ingress, true))
		} else if protocol == "dns" {
			pkt := amplify(NewPacket(PKT_LEN, protocol, ingress, true))
			_DEBUG.Printf("Function: sendPktsProtocol - protocol is %s, total pkts to send is %v and ingress is %v and PKT lenght is %v", protocol, n, ingress, pkt.packet_len)
			enqueuePacket(pkt)

		}
	}
}
func randAttackMix() {
	// _DEBUG.Printf("Function: flowGenSimple - Number of packets to send in 1 second %d with packet length %f and send rate %f",numPkts, PKT_LEN, fixedCap)
	for {
		u := rand.Float64()
		// t := rand.Float64()
		d := rand.Float64()
		sum := u + d //+ t
		u = (u / sum) * CONFIGURATION.ATTACKER_CAP
		// t = (t / sum) * CONFIGURATION.ATTACKER_CAP
		d = (d / sum) * CONFIGURATION.ATTACKER_CAP
		u_numPkts := int(math.Ceil(u/(PKT_LEN*1000))) * 100
		// t_numPkts := int(t / PKT_LEN)
		d_numPkts := int(math.Ceil(d/(PKT_LEN*1000))) * 100
		ingress := 0

		go sendPktsProtocol(u_numPkts, ingress, "udp")
		// go sendPktsProtocol(t_numPkts, ingress, "tcp")
		go sendPktsProtocol(d_numPkts, ingress, "dns")
		time.Sleep(100 * time.Millisecond)
		// # network.sendtoNetwork(pkt)
	}
}
