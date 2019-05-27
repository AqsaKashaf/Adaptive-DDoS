package main

import (
	"math"
	"time"
)

type packet struct {
	packet_len  float64
	protocol    string // tcp, udp, dns
	ingress     int
	attack_flag bool
	dest        string
	src         string
	synFlag     int
	ackFlag     int
	detection   string
	timestamp   time.Time
}

func NewPacket(l float64, protocol string, ingress int, af bool) packet {
	var p packet
	p.packet_len = l
	p.protocol = protocol
	p.ingress = ingress
	p.attack_flag = af
	p.dest = "dummy"
	p.detection = "benign"
	return p
}
func flowGenBenign(model string, ingress int) {
	// # _DEBUG.Printf("Function: flowGen")
	if model == "simple" {
		flowGenSimple(ingress)
	}
}

func sendPkts(n int, ingress int) {
	for i := 0; i < n; i++ {
		// sendtoNetwork(NewPacket(PKT_LEN,"udp",0,0))
		enqueuePacket(NewPacket(PKT_LEN, "udp", ingress, false))
		// time.Sleep(1 * time.Microsecond)
	}
}

func flowGenSimple(ingress int) {
	fixedRate := 100.0 // Mbps
	numPkts := int(math.Ceil(fixedRate / (PKT_LEN)))
	_DEBUG.Printf("Function: flowGenSimple - Number of packets to send in 100 ms %d with packet length %f and send rate %f", numPkts, PKT_LEN, fixedRate)
	for {
		go sendPkts(numPkts, ingress)
		time.Sleep(1 * time.Second)
		// # network.sendtoNetwork(pkt)
	}
}

func flowGenSimple2(ingress int) {
	fixedRate := 1000.0 // Mbps
	numPkts := int(fixedRate / PKT_LEN)
	_DEBUG.Printf("Function: flowGenSimple2 - Number of packets to send in 1 second %d with packet length %f and send rate %f", numPkts, PKT_LEN, fixedRate)
	// for {
	sendTicker := time.NewTicker(time.Duration(1 * time.Second))

	for {
		select {
		case <-sendTicker.C:
			go sendPkts(numPkts, ingress)
		}
	}

}
