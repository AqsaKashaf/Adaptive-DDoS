package main

import (
	"os"

	"../helper/fifo"
	"../helper/go-cache"

	// "fmt"
	"encoding/json"
	"log"
	"runtime"
	"time"
)

const TOTAL_BACKLOG_SIZE int = 256 // syn queue acceoting 256 connnections

var (
	CONFIGURATION      Config
	CURR_TRAFFIC_STATS []map[string]float64
	// PREV_TRAFFIC_STATS []map[string]int
	PEAK_TRAFFIC []float64
	MIN_TRAFFIC  []float64
	AVG_TRAFFIC  []float64
	// RECEIVE_COUNTER []int
	legitimateDropCounter []int
	TargetDropCounter     int
	// processCounter []int
	// BUFFER []*fifo.Queue
	RTT            time.Duration
	pktQueue       []*fifo.Queue
	tPktQueue      *fifo.Queue
	tOutgoingQueue *fifo.Queue
	BACKLOG_TARGET *cache.Cache
	ATTACK_TYPES   [3]string
	BACKLOG        [TOTAL_BACKLOG_SIZE]string // array to store pkts

	NUM_VMs                  []map[string]int
	INGRESS_CAP              []map[string]*VM
	PKT_LEN                  float64 = 100.0 * 8 / 1000000
	UDP_DETECT_ACCURACY      float64 = 0.9
	TCP_SYN_DETECT_ACCURACY  float64 = 0.9
	DNS_AMP_DETECT_ACCURACY  float64 = 0.9
	EPOCH_TIME                       = 5.0
	WINDOW_COUNTER           int
	CONN_IN_BACKLOG          int = 0 //num of connection in backlog
	CONN_CUST                int = 0 //num of connection in customer
	times                    string
	TARGET_NETWORK_RESOURCES *VM
	TARGET_LINK_RESOURCES    *VM
)

func main() {

	runtime.GOMAXPROCS(4)
	if len(os.Args) < 2 {
		log.Fatal("PLEASE ENTER FILENAME FOR CONFIG")
	}
	ATTACK_TYPES[0] = "UDP_FLOOD"
	ATTACK_TYPES[1] = "TCP_SYN"
	ATTACK_TYPES[2] = "DNS_AMP"
	var configurationFile string = os.Args[1]
	_DEBUG.Println("Hello from main")

	_DEBUG.Println("Reading configuration file")

	CONFIGURATION = LoadConfiguration(configurationFile)
	s, _ := json.MarshalIndent(CONFIGURATION, "", "\t")
	_DEBUG.Printf("%s", s)

	_DEBUG.Printf("Initialize traffic stats data structures in ISP")
	// initialize traffic stats data structures
	initializeISP()

	_DEBUG.Printf("Initialize capacity of ingress locations depending on the defense type")
	initializeDefense()

	initializeLocks()

	// start legitimate traffic thread
	_DEBUG.Printf("Start legitimate traffic thread")
	// for j := 0; j < CONFIGURATION.INGRESS_LOC; j++ {
	// 	flowGenBenign("simple", j)
	// }
	// start attack traffic thread
	_DEBUG.Printf("Start attack traffic thread")
	go attack()

	// start dequeuing pkts after delay equivalent to processing delay
	_DEBUG.Printf("Start packet processing thread - processing delay = %f s", CONFIGURATION.PROCESSING_DELAY)
	_DEBUG.Printf("Start stats collection thread - epoch = %f s", EPOCH_TIME)
	// stopProcess = Event()
	// processingThread = RepeatingThread(stopProcess,PROCESSING_DELAY,"packet processingThread",buffer.processPacket)
	// processingThread.start()
	statsTicker := time.NewTicker(time.Duration(EPOCH_TIME) * time.Second)
	processTicker := time.NewTicker(time.Duration(CONFIGURATION.PROCESSING_DELAY) * time.Millisecond)

	// go processing()
	// go flowGenBenign("simple", 0)
	for {
		select {
		case <-processTicker.C:
			go processPacket("UDP_FLOOD")
			go processPacket("TCP_SYN")
			go processPacket("DNS_AMP")
			go processIncomingTarget()
			go processOutgoingTarget()
		case <-statsTicker.C:
			go collectStats()
		}
	}

}
