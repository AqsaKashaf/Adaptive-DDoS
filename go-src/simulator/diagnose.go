package main

import (
	"math/rand"
)

func detect_UDP_Flood(udp_pkt packet) bool {
	rnd := rand.Float64()
	if rnd < UDP_DETECT_ACCURACY {
		// _DEBUG.Printf("Function: detect_UDP_Flood - attack pkt detected")
		// # attack packet received
		return true
	}

	return false
}

func detect_TCP_SYN_Flood(tcp_pkt packet) bool {
	rnd := rand.Float64()
	if rnd < TCP_SYN_DETECT_ACCURACY {
		// # attack packet received
		return true
	}
	return false
}

func detect_DNS_Amp(dns_pkt packet) bool {
	rnd := rand.Float64()
	if rnd < DNS_AMP_DETECT_ACCURACY {
		// # attack packet received
		return true
	}

	return false
}

func diagnose_UDP_Flood(pkt packet) packet {

	if detect_UDP_Flood(pkt) {
		pkt.detection = "attack"
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["UDP_FLOOD"] += pkt.packet_len
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	} else {
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	}
	return pkt
}

func diagnose_TCP_SYN_Flood(pkt packet) packet {

	if detect_TCP_SYN_Flood(pkt) {
		pkt.detection = "attack"
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["TCP_SYN"] += pkt.packet_len
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()

	} else {
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	}
	return pkt
}

func diagnose_DNS_Amp(pkt packet) packet {

	if detect_DNS_Amp(pkt) {
		pkt.detection = "attack"
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["DNS_AMP"] += pkt.packet_len
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	} else {
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	}
	return pkt
}

func isUDP(pkt packet) bool {
	if pkt.protocol == "udp" {
		return true
	}
	return false
}

func isTCP(pkt packet) bool {
	if pkt.protocol == "tcp" {
		return true
	}
	return false
}

func isDNS(pkt packet) bool {
	if pkt.protocol == "dns" {
		return true
	}
	return false
}

func diagnoseTraffic(pkt packet) packet {

	if pkt.attack_flag == true {
		if isUDP(pkt) {
			pkt = diagnose_UDP_Flood(pkt)
		}

		if isTCP(pkt) {
			pkt = diagnose_TCP_SYN_Flood(pkt)
		}

		if isDNS(pkt) {
			pkt = diagnose_DNS_Amp(pkt)
		}

	} else {
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Lock()
		CURR_TRAFFIC_STATS[pkt.ingress]["total"] += pkt.packet_len
		LOCK_CURR_TRAFFIC_STATS[pkt.ingress].Unlock()
	}
	return pkt
}
