# Adaptive - DDOS 

A Distributed Denial of Service (DDoS) defense system simulation which is capable of handling smart attackers. The DDoS defense system is adaptive and can allocate resources to ingress locations based on it's ability to predict the incoming attack traffic at each ingress by looking at the past traffic at each ingress location.


## Simulator Design 

The DDoS defense system has been designed to be configured in three states: Static, Dynamic and Adaptive. The static defense system is the basic defense system where there is there is no change in the number of VM's alloted to all the ingress locations. The dynamic defense system will allocate the the VM's for the ingress location without any prediction. The Adaptive defense system will decide the number of VM's to be allocated for each ingress location per epoch based on the past traffic at each ingress location. The assumptions made are, each virtual machine has one NIC and each NIC has one queue. We prove the efficiency of our defense model by computing the number of legitimate packets dropped and the proper utilization of allocated VM's to each ingress location. 


## This Repository Contains..

1. attack.go -  The two attack types, randIngress and randAttackMix have been defined here. The former type of attack will send an attack of fixed type, to a different ingress location at every epoch and the latter attack type to send an attack to an ingress location at all epochs but will vary the type of attack.  
2. benignTraffic.go -  The functions for sending non-attack traffic have been defined in this file. 
3. buffer.go -  Handles the enqueing and dequeing and dropping of packets. There is one queue per NIC of the VM.
4. defense.go - The initialization of defenses has been defined.
5. diagnose.go - This file contains functions to detect and diagnose the TCP-SYN flood, UDP flood and the normal traffic. 
6. isp.go - Functions to initialze capacity to the ingress locations and to calculate teh dropped packets and wasted resources has been defined here. 
7. locking.go - Initialization of locks has been done.
5. logging.go - File that handles the logging. 
6. mitigate.go - The three types of defense models : static, dynamic and adaptive have been defined here.
7. simulator.go - The main function is contained in this file.


## Requirement

Go 1.11.2

