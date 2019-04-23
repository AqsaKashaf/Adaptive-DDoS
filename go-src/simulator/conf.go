package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type Config struct {
	ATTACK_TYPE           string  `json:"attackerType"`
	DEFENSE_TYPE          string  `json:"defenseType"`
	INGRESS_LOC           int     `json:"ingreeLoc"`
	VM_COMPUTE_CAP        float64 `json:"VMCapacity"`
	ISP_CAP               float64 `json:"ISPCapacity"`
	NUM_NIC_VM            int     `json:"numNICsVM"`
	ATTACKER_CAP          float64 `json:"attackerCapacity"`
	LEG_TRAFFIC_MODEL     string  `json:"legitimateTraffic"`
	EPOCH_TIME            float64 `json:"epochTime"`
	PROCESSING_DELAY      float64 `json:"processingDelay"`
	BUFF_SIZE             float64 `json:"buffSize"`
	TARGET_BUFF_SIZE      float64 `json:"targetBuffSize"`
	BACKLOG_SIZE          int     `json:"backlogSize"`
	SERVER_CAP            int     `json:"ServerCapacity"`
	TARGET_PROCESS_CAP    float64 `json:"TargetProcessCapacity"`
	TARGET_SERVER_CAP     float64 `json:"TargetServerCapacity"`
	TARGET_LINK_CAP       float64 `json:"TargetLinkCapacity"`
	TARGET_LINK_BUFF_SIZE float64 `json:"targetLinkBuffSize"`
}

func LoadConfiguration(file string) Config {
	var config Config
	configFile, err := os.Open(file)
	defer configFile.Close()
	if err != nil {
		fmt.Println(err.Error())
	}
	jsonParser := json.NewDecoder(configFile)
	jsonParser.Decode(&config)
	// config.VM_COMPUTE_CAP *= 1000 // conversion from Gbps to Mbps
	// config.ISP_CAP *= 1000 // conversion from Gbps to Mbps
	// config.ATTACKER_CAP *= 1000
	// config.BUFF_SIZE *= 8 // conversion to bits from bytes

	return config
}
