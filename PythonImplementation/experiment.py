import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random
import threading

num_ingress = 3
ISP_Cap = 10000000
VM_Cap = 200000
Number_of_VMs = ISP_Cap / VM_Cap 
ISP_Queues = [80*Number_of_VMs,80*Number_of_VMs,80*Number_of_VMs]  #Mbits

Process_Cap = 200000 #Mbits
Process_Queue = 100 #Mbits

Server_Cap = 100000
Backlog_per_VM = 256      #Per VM

Link_Cap = 500000
Link_Queue = 100

amp_factor = np.random.randint(8,13)

num_rounds = 500

Max_attack_budget = 100000

tcp_size = 0.00048  #TCP Packet Sizes = 60bytes
udp_size = 0.524280   #UDP Packet Sizes = 65,535 bytes
dns_size = amp_factor * udp_size  #DNS Amp Size

rewards = [5,5,5,10,10,20]

RTT_QLearn = []
RTT_randMix = []
RTT_randIngressAttack = []

#Q-Learning Algorithm
def q_learn(RTT):
    states = 3 + num_ingress
    actions = 5151*num_ingress
    q_table = np.zeros([states,actions])
    q=q_table
# Hyperparameters
    alpha = 0.1
    gamma = 0.6
    epsilon = 0.1
    max_epsilon = 1.0
    min_epsilon = 0.01
    decay_rate = 0.01
    all_penalties = []

    rewards = RTT
    max_reward = np.max(np.asarray(rewards))

    for i in range(1, 20000):
        state = np.random.randint(0,states)

    # Init Vars
        epochs, penalties, reward, = 0, 0, 0
        done = False

        while not done:
            if random.uniform(0, 1) < epsilon:
            # Check the action space
                action = np.random.randint(0,actions)
            else:
            # Check the learned values
                action = np.argmax(q_table[state])

            next_state = np.random.randint(0,states)
            reward = rewards[next_state]
            if(reward == max_reward):
                done = True
                
            old_value = q_table[state, action]
            next_max = np.max(q_table[next_state])

        # Update the new value
            new_value = (1 - alpha) * old_value + alpha * \
            (reward + gamma * next_max)
            q_table[state, action] = new_value

            if reward == -10:
                penalties += 1

            state = next_state
            epochs += 1

        epsilon = min_epsilon + (max_epsilon-min_epsilon)*np.exp(-0.1*epsilon)
    
        if i % 100 == 0:
            all_penalties += [penalties]
    ind = np.unravel_index(np.argmax(q_table, axis=None), q_table.shape)

    x=list(get_tuple(3,100))
    k= ind[1] % 5151
    
    return x[k], int(ind[1]/5151)

def get_tuple(length, total):
    return filter(lambda x:sum(x)==total,product(range(total+1),repeat=length))

#Return Attack Strategy
def getAttackStrategy(ISPIngress, Budget, Attack, RTT):
    attack_volume = list(get_tuple(3,100))

    ingress = 1  
    if(Attack is "RandMix"):
        x = np.random.randint(0,5151)
        attack_vol = list(attack_volume[x])
        ingress = 1
        attack = {ingress:attack_vol}
        
    elif(Attack is "RandIngress"):
        #x = np.random.randint(0,5151)
        attack_tcp, attack_dns, attack_udp = 100/3,100/3,100/3
        ingress = np.random.randint(1,ISPIngress)
        attack = {ingress:[attack_tcp,attack_udp,attack_dns]}
        
    else:
        for l in range(0,3):
            rewards[l]-=RTT
        for l in range(3,6):
            rewards[l]+=RTT
        attack, ingress = q_learn(rewards)
        attack = {ingress:[attack[0],attack[1],attack[2]]}       #Attack[0] is TCP, Attack[1] is UDP, Attack[2] is DNS
    
    for i in range(0,3):
        attack[ingress][i] = attack[ingress][i]/100*attack_budget

    
    return attack

#Firewall Implementation
def Firewall(attack, false_negative_rate):                           
    ingress = list(attack.keys())[0]
    for i in range(0,3):
        attack[ingress][i] = attack[ingress][i]*(1-false_negative_rate)      #PErcentage of attack traffic that goes through

    return attack

#Benign Traffic Implementation
def BenignTraffic():
    background = random.uniform(1000,10000)
    benign_traffic = {'SYN':0,'DATA':0}
    #Total Connections = Page views per user * Number of users of the website (5.54 * 1821.6*10^3)
    #Number of users of the website = (Reach per million * total internet users)/10^6 = (414*4.4*10^9)/10^6
    benign_traffic['SYN'] = random.normal(10092000,3129000)
    #Assuming the data traffic is 5 times the SYN connections received
    benign_traffic['DATA'] = random.normal(10092000,3129000)*5
    return background, benign_traffic

#Merging Attack and Benign Traffic
def mergeTraffic(attack):
    background, benign_traffic = BenignTraffic()
    #Get keys
    ingress = list(attack.keys())[0]
    
    #Merge everything together
    Traffic = {ingress:{attack[ingress][0]+benign_traffic['SYN'], attack[ingress][1], attack[ingress][2], benign_traffic['DATA'],background}}
    return Traffic  

# Calculates the congestion in the ISP queue
def calculateCongestionISP(round_num, attack, traffic):
	# round 0
    # isp traffic per ingress all values
    # ISP_raffic = mergeTraffic()
    Traffic_sum = []
    #ISP_traffic = {}
    for i in range(num_ingress):  
        #ISP_traffic[i] = {'TCP':0,'UDP':0,'DNS':0, 'Data':0, 'Background':0}
        Traffic_sum[i] = sum(traffic[i].values())
    
    # target traffic sum of all ingress isp traffics
	Rem_traffic = traffic
    pkts_queued = traffic
    pkts_in_queue = traffic

    if round_num == 0:
        for i in range(num_ingress):      
            avail_queue_size[i] = ISP_Queues[i]
            last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0

                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

	# rounds 1 to n	
	else:
		for i in range(num_ingress):
            #avail_queue_size[i] = ISP_Queues[i]
            #last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0
                
                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

    return avail_queue_size, Rem_traffic
	
# Calculates the congestion in the Link queue
def calculateCongestionLink(round_num, attack, traffic):
	# round 0
    # isp traffic per ingress all values
    # ISP_raffic = mergeTraffic()
    Traffic_sum = []
    #ISP_traffic = {}
    for i in range(num_ingress):  
        #ISP_traffic[i] = {'TCP':0,'UDP':0,'DNS':0, 'Data':0, 'Background':0}
        Traffic_sum[i] = sum(traffic[i].values())
    
    # target traffic sum of all ingress isp traffics
	Rem_traffic = traffic
    pkts_queued = traffic
    pkts_in_queue = traffic

    if round_num == 0:
        for i in range(num_ingress):      
            avail_queue_size[i] = ISP_Queues[i]
            last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0

                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

	# rounds 1 to n	
	else:
		for i in range(num_ingress):
            #avail_queue_size[i] = ISP_Queues[i]
            #last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0
                
                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

    return avail_queue_size, Rem_traffic
		
# Calculates the congestion in the target queue
def calculateCongestionProcess(round_num, attack, traffic):
	# round 0
    # isp traffic per ingress all values
    # ISP_raffic = mergeTraffic()
    Traffic_sum = []
    #ISP_traffic = {}
    for i in range(num_ingress):  
        #ISP_traffic[i] = {'TCP':0,'UDP':0,'DNS':0, 'Data':0, 'Background':0}
        Traffic_sum[i] = sum(traffic[i].values())
    
    # target traffic sum of all ingress isp traffics
	Rem_traffic = traffic
    pkts_queued = traffic
    pkts_in_queue = traffic

    if round_num == 0:
        for i in range(num_ingress):      
            avail_queue_size[i] = ISP_Queues[i]
            last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0

                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

	# rounds 1 to n	
	else:
		for i in range(num_ingress):
            #avail_queue_size[i] = ISP_Queues[i]
            #last_queue_size[i] = avail_queue_size[i]
            for key in traffic[i]:
            if attack[key] > ISP_Queues[i]:
                pkts_queued[i][key] = attack[key] - ISP_Queues[i]
                if pkts_queued[i][key] > avail_queue_size[i]:
                    pkts_dropped[i][key] = pkts_queued[i][key] - avail_queue_size[i]
                    pkts_in_queue[i][key] = pkts_queued[i][key] - pkts_dropped[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]
        
                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    # avail_queue_size[i] -= 
                    Rem_traffic[i][key] = traffic[i][key] - pkts_dropped[i][key]*a
                else:
                    pkts_dropped[i][key] = 0
                    pkts_in_queue[i][key] = pkts_queued[i][key]
                    avail_queue_size[i] = last_queue_size[i] - pkts_in_queue[i][key]

                    a = traffic[i][key]/Traffic_sum[i]
                    last_queue_size[i] = avail_queue_size[i]
                    Rem_traffic[i][key] = traffic[i][key]
            else:
                pkts_queued[i][key] = 0
                pkts_dropped[i][key] = 0
                pkts_in_queue[i][key] = 0
                
                a = traffic[i][key]/Traffic_sum[i]
                last_queue_size[i] = avail_queue_size[i]
                Rem_traffic[i][key] = traffic[i][key]

    return avail_queue_size, Rem_traffic

if __name__ =="__main__":
    
    print("Simulator Start!")
    total_budget = Max_attack_budget
    attack_types = ['RandMix', 'RandIngress', 'Smart']
    for i in range(0,num_rounds):
        
        RTT = 0
        attack_budget = random.uniform(1000, total_budget)
        total_budget-= attack_budget
        
        for j in attack_types:
            attack_vol = getAttackStrategy(num_ingress, attack_budget, j, RTT)
            attack_vol = Firewall(attack_vol, 0.6)
            Traffic = mergeTraffic(attack_vol)
            print(Traffic)
            
            rem_ISP_queue, Traffic = calculateCongestionISP(i, attack, Traffic)

            rem_link_queue, Traffic = calculateCongestionLink(i, attack, Traffic)

            rem_process_queue, Traffic = calculateCongestionProcess(i, attack, Traffic)
            #Create your own functions

        
#threading.Thread(target=lambda: every(5, mergeTraffic)).start()
