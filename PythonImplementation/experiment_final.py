import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random

num_ingress = 3
ISP_Cap = [10000000/num_ingress, 10000000/num_ingress, 10000000/num_ingress]    #Static
VM_Cap = 200000
Number_of_VMs = ISP_Cap[0]/VM_Cap
#print(Number_of_VMs)
ISP_Queues = [80*Number_of_VMs, 80*Number_of_VMs, 80*Number_of_VMs]  #Mbits

print(ISP_Queues)

Traffic_sum = [0,0,0]
packet_drops = [0,0,0]
pkts_to_be_queued = [0,0,0]
pkts_to_be_queued_link = 0
pkts_to_be_queued_process = 0

avail_queue_size = ISP_Queues

occupied_queue_size = [0, 0, 0]
occupied_link_queue_size = 0
occupied_process_queue_size = 0
link_traffic = {'SYN':0,'UDP':0,'DNS':0,'Data':0}

Process_Cap = 200000 #Mbits
Process_Queue = 100 #Mbits
process_traffic = {'SYN':0,'UDP':0,'DNS':0,'Data':0}

Server_Cap = 100000
Backlog_per_VM = 256      #Per VM

Link_Cap = 500000
Link_Queue = 100
avail_link_queue_size = Link_Queue

amp_factor = np.random.randint(8,13)

num_rounds = 500

Max_attack_budget = 100000

tcp_size = 0.000048  #TCP Packet Sizes = 60bytes
udp_size = 0.062428   #UDP Packet Sizes = 65,535 bytes
dns_size = amp_factor * udp_size  #DNS Amp Size

rewards = [5,5,5,10,10,20]

RTT_QLearn = []
RTT_randMix = []
RTT_randIngress = []

time_syn = []
pkts_queued_syn = []

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
        for l in range(0,6):
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
    background = random.uniform(20000000,25000000)/(24*60*60)
    benign_traffic = {'SYN':0,'DATA':0}
    #Total Connections = Page views per user * Number of users of the website (5.54 * 1821.6*10^3)
    #Number of users of the website = (Reach per million * total internet users)/10^6 = (414*4.4*10^9)/10^6
    benign_traffic['SYN'] = np.random.normal(10092000,3129000)/(24*60*60)
    #Assuming the data traffic is 5 times the SYN connections received
    benign_traffic['DATA'] = np.random.normal(10092000,3129000)/(24*60*60)
    return background, benign_traffic

#Merging Attack and Benign Traffic
def mergeTraffic(attack):
    background, benign_traffic = BenignTraffic()
    #Get keys
    ingress = list(attack.keys())[0]
    attack_syn_vol = attack[ingress][0]/(attack[ingress][0]+benign_traffic['SYN'])
    benign_syn_vol = benign_traffic['SYN']/(attack[ingress][0]+benign_traffic['SYN'])
    Traffic = {0:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},1:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},2:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0}}
    for j in range(0,3):
        if(j is ingress):
            Traffic[j]={'SYN':attack[ingress][0]+benign_traffic['SYN']*tcp_size,'UDP':attack[ingress][1],'DNS':attack[ingress][2], 'Data':benign_traffic['DATA']/3,'Background':background/3}
        else:
            Traffic[j]={'SYN':0,'UDP':0,'DNS':0,'Data':benign_traffic['DATA']/3,'Background':background/3}
    return Traffic, attack_syn_vol, benign_syn_vol      #Return benign and attack syn volume for SYN

# Calculates the congestion in the ISP queue
def calculateCongestionISP(traffic):
    rem_traffic = traffic
    # Traffic[j] = {'SYN':0,'UDP':0,'DNS':0,'Data':benign_traffic['DATA'],'Background':background}
    for i in range(0,num_ingress):  
        
        Traffic_sum[i] = sum(traffic[i].values())
        print(Traffic_sum[i])
        pkts_to_be_queued[i] = Traffic_sum[i] + occupied_queue_size[i] - ISP_Cap[i]
        if(pkts_to_be_queued[i] < 0):
            pkts_to_be_queued[i] = 0
        #print(pkts_to_be_queued[i])
        #time.sleep(1)
        P_syn = traffic[i]['SYN']/Traffic_sum[i]
        P_udp = traffic[i]['UDP']/Traffic_sum[i]
        P_dns = traffic[i]['DNS']/Traffic_sum[i]
        P_data = traffic[i]['Data']/Traffic_sum[i]
        P_bg = traffic[i]['Background']/Traffic_sum[i] 

        if pkts_to_be_queued[i] <= ISP_Queues[i]:
            #print('I am here')
            #time.sleep(1)
            packet_drops[i] = 0
            occupied_queue_size[i] = pkts_to_be_queued[i]
            rem_traffic[i]['SYN'] = traffic[i]['SYN'] - P_syn*occupied_queue_size[i]
            rem_traffic[i]['UDP'] = traffic[i]['UDP'] - P_udp*occupied_queue_size[i]
            rem_traffic[i]['DNS'] = traffic[i]['DNS'] - P_dns*occupied_queue_size[i]
            rem_traffic[i]['Data'] = traffic[i]['Data'] - P_data*occupied_queue_size[i]
            rem_traffic[i]['Background'] = traffic[i]['Background'] - P_bg*occupied_queue_size[i]
            #print("Occupied Queue Size {}".format(occupied_queue_size[i]))
            #time.sleep(1)

        if pkts_to_be_queued[i] > ISP_Queues[i]:
            #print('I am here too')
            #time.sleep(1)
            packet_drops[i] = pkts_to_be_queued[i] - ISP_Queues[i]
            occupied_queue_size[i] = ISP_Queues[i]
            rem_traffic[i]['SYN'] = traffic[i]['SYN'] - P_syn*(occupied_queue_size[i] + packet_drops[i])
            rem_traffic[i]['UDP'] = traffic[i]['UDP'] - P_udp*(occupied_queue_size[i] + packet_drops[i])
            rem_traffic[i]['DNS'] = traffic[i]['DNS'] - P_dns*(occupied_queue_size[i] + packet_drops[i])
            rem_traffic[i]['Data'] = traffic[i]['Data'] - P_data*(occupied_queue_size[i] + packet_drops[i])
            rem_traffic[i]['Background'] = traffic[i]['Background'] - P_bg*(occupied_queue_size[i] + packet_drops[i])
            #print("Occupied Queue Size {}".format(occupied_queue_size[i]))
            time.sleep(1)

        avail_queue_size[i] = ISP_Queues[i] - occupied_queue_size[i]
        
    return avail_queue_size, rem_traffic
	
# Calculates the congestion in the Link queue
def calculateCongestionLink(traffic, occupied_link_queued_size):
    
    queue_occ = occupied_link_queued_size
    rem_link_traffic = link_traffic
    for i in range(0,num_ingress):
        link_traffic['SYN'] += traffic[i]['SYN']
        link_traffic['UDP'] += traffic[i]['UDP']
        link_traffic['DNS'] += traffic[i]['DNS']
        link_traffic['Data'] += traffic[i]['Data']

    total_link_traffic = sum(link_traffic.values())
    print(total_link_traffic)

    pkts_to_be_queued_link = total_link_traffic + queue_occ - Link_Cap
    if(pkts_to_be_queued_link < 0):
        pkts_to_be_queued_link = 0
    
    P_syn = link_traffic['SYN']/total_link_traffic
    P_udp = link_traffic['UDP']/total_link_traffic
    P_dns = link_traffic['DNS']/total_link_traffic
    P_data = link_traffic['Data']/total_link_traffic     

    if pkts_to_be_queued_link <= Link_Queue:
        packet_drops_link = 0
        queue_occ = pkts_to_be_queued_link
        rem_link_traffic['SYN'] = link_traffic['SYN'] - P_syn*queue_occ
        rem_link_traffic['UDP'] = link_traffic['UDP'] - P_udp*queue_occ
        rem_link_traffic['DNS'] = link_traffic['DNS'] - P_dns*queue_occ
        rem_link_traffic['Data'] = link_traffic['Data'] - P_data*queue_occ
        
    if pkts_to_be_queued_link > Link_Queue:
        packet_drops_link = pkts_to_be_queued_link - Link_Queue
        queue_occ = Link_Queue
        rem_link_traffic['SYN'] = link_traffic['SYN'] - P_syn*(queue_occ+packet_drops_link)
        rem_link_traffic['UDP'] = link_traffic['UDP'] - P_udp*(queue_occ+packet_drops_link)
        rem_link_traffic['DNS'] = link_traffic['DNS'] - P_dns*(queue_occ+packet_drops_link)
        rem_link_traffic['Data'] = link_traffic['Data'] - P_data*(queue_occ+packet_drops_link)

    avail_link_queue_size = Link_Queue - queue_occ

    return avail_link_queue_size, rem_link_traffic, queue_occ
		
# Calculates the congestion in the target process queue
def calculateCongestionProcess(traffic, occupied_process_queue_size):
    
    proc_occ = occupied_process_queue_size
    rem_process_traffic = process_traffic
    #for i in range(0,num_ingress):  
    process_traffic['SYN'] += traffic['SYN']
    process_traffic['UDP'] += traffic['UDP']
    process_traffic['DNS'] += traffic['DNS']
    process_traffic['Data'] += traffic['Data']

    total_process_traffic = sum(process_traffic.values())
    print(total_process_traffic)

    pkts_to_be_queued_process = total_process_traffic + proc_occ - Process_Cap
    if(pkts_to_be_queued_process < 0):
        pkts_to_be_queued_process = 0
        
    P_syn = process_traffic['SYN']/total_process_traffic
    P_udp = process_traffic['UDP']/total_process_traffic
    P_dns = process_traffic['DNS']/total_process_traffic
    P_data = process_traffic['Data']/total_process_traffic     

    if pkts_to_be_queued_process <= Process_Queue:
        packet_drops_process = 0
        proc_occ = pkts_to_be_queued_process
        rem_process_traffic['SYN'] = process_traffic['SYN'] - P_syn*proc_occ
        rem_process_traffic['UDP'] = process_traffic['UDP'] - P_udp*proc_occ
        rem_process_traffic['DNS'] = process_traffic['DNS'] - P_dns*proc_occ
        rem_process_traffic['Data'] = process_traffic['Data'] - P_data*proc_occ
        
    if pkts_to_be_queued_link > Process_Queue:
        packet_drops_process = pkts_to_be_queued_process - Process_Queue
        proc_occ = Process_Queue
        rem_process_traffic['SYN'] = process_traffic['SYN'] - P_syn*(proc_occ+packet_drops_process)
        rem_process_traffic['UDP'] = process_traffic['UDP'] - P_udp*(proc_occ+packet_drops_process)
        rem_process_traffic['DNS'] = process_traffic['DNS'] - P_dns*(proc_occ+packet_drops_process)
        rem_process_traffic['Data'] = process_traffic['Data'] - P_data*(proc_occ+packet_drops_process)

    avail_process_queue_size = Process_Queue - proc_occ

    return avail_process_queue_size, rem_process_traffic, proc_occ

def backlogCongestion(V_syn, available_syn_q, pkts_queued_syn, time_syn):
    #backlogtime = datetime.datetime.now().timestamp()
    av_q = available_syn_q
    pkts_syn = pkts_queued_syn
    t_syn = time_syn
    # Remains a constant throught
    total_server_processing = Server_Cap
    #Checking is the processing capacity of the server is greater than the volume of the SYN traffic
    
    #if total_server_processing - V_syn < 0:
        #Volume of the traffic to be queued
    #V_syn_q = V_syn - total_server_processing
        #connections_syn_q = int(V_syn_q/tcp_size)
    connections_syn_q = int(V_syn/tcp_size)
        #Checking if all the incoming SYN connections can be queued
 #   if total_connections - connections_syn_q < 0:
 #       connections_dropped = connections_syn_q - total_connections
            #List containing the timestamp in which the connections were added to the queue 
            #time_syn.add(datetime.datetime.now().timestamp())
        t_syn+=[time.time()]
            #List containing the number of connections added to the queue
        pkts_syn+=[av_q - connections_dropped]
            #Recalculating the available space in the backlog queue
        av_q = av_q - pkts_queued_syn[-1]
    return av_q, pkts_syn, t_syn

def rttEstimate(ISP_Queues, Link_Queue, Process_Queue, Backlog_Queue, ISP_Cap):
    if (Backlog_Queue >= 256):
        rtt = 10000
    else:
        rtt = ISP_Queues/ISP_Cap + Link_Queue/Link_Cap + Process_Queue/Process_Cap
    return rtt

if __name__ =="__main__":
    
    ISP_Cap = [10000000/num_ingress, 10000000/num_ingress, 10000000/num_ingress]    #Static
    VM_Cap = 2000
    Number_of_VMs = [ISP_Cap[0]/VM_Cap, ISP_Cap[1]/VM_Cap, ISP_Cap[2]/VM_Cap]       #print(Number_of_VMs)
    ISP_Queues = [80*Number_of_VMs[0], 80*Number_of_VMs[1], 80*Number_of_VMs[2]]    #Mbits
    
    expire_time = 45
    totalMachines = Server_Cap/VM_Cap
    total_connections = Backlog_per_VM * totalMachines
    available_syn_q = int(total_connections)
    
    print("Simulator Start!")
    print("Backlog Size {}".format(available_syn_q))
    time.sleep(1)
    total_budget = Max_attack_budget
    attack_types = ['RandMix', 'RandIngress', 'Smart']
    for i in range(0,num_rounds):
        
        RTT = 0
        attack_budget = random.uniform(1000, total_budget)
        total_budget-= attack_budget
        
        for j in attack_types:
            attack_vol = getAttackStrategy(num_ingress, attack_budget, j, RTT)
            attack_vol = Firewall(attack_vol, 0.6)
            attack_ingress = list(attack_vol.keys())[0]
            
            Traffic, attack_syn_vol, benign_syn_vol = mergeTraffic(attack_vol)
            print(Traffic)
            time.sleep(1)
            
#            for l in range(0,3):
#                if(l is attack_ingress):
#                    Traffic[l]={'SYN':Traffic[l]['SYN'],'UDP':Traffic[l]['UDP'],'DNS':Traffic[l]['DNS']}
#                else:
#                    Traffic[l]={'SYN':0,'UDP':0,'DNS':0}
                    
            #print(Traffic)
            print("Attack Type {} Round {} \n".format(j,i))            
            rem_ISP_queue, ISP_Traffic = calculateCongestionISP(Traffic)
            print("Remaining ISP Queue Lengths {} \n".format(rem_ISP_queue))
            print(ISP_Traffic)

            rem_link_queue, Link_Traffic, occupied_link_queue_size = calculateCongestionLink(ISP_Traffic, occupied_link_queue_size)
            print("Remaining Link Queue Lengths {}, Occupied {} \n".format(rem_link_queue, occupied_link_queue_size))
            #print("Traffic Volume {}\n".format(sum(Traffic.values())))
            print(Link_Traffic)

            rem_process_queue, Process_Traffic, occupied_process_queue_size = calculateCongestionProcess(Link_Traffic, occupied_process_queue_size)
            print("Remaining Process Queue Lengths {}, Occupied {} \n".format(rem_process_queue, occupied_process_queue_size))
            #summer = sum(Process_Traffic.values())
            #print("Traffic Volume {} \n".format(sum))
            print(Process_Traffic)
            
            SYN_VOL = int(Process_Traffic['SYN'])
            print("SYN Volumes {}".format(SYN_VOL))
            attack_syn_percent = attack_syn_vol/(attack_syn_vol + benign_syn_vol)
            benign_syn_percent = benign_syn_vol/(attack_syn_vol + benign_syn_vol)
            
            back_queue, pkts_queued_syn, time_syn = backlogCongestion(SYN_VOL, available_syn_q, pkts_queued_syn, time_syn)
            
            if(back_queue > int(total_connections)):
                back_queue = int(total_connections)
            if(back_queue < 0):
                back_queue = 0
            print("Backlog Size {} \n".format(back_queue))

            t = time.time() 
            for k in range(0,len(time_syn)):
                if t - time_syn[k] >= 3:
                    back_queue += int((benign_syn_percent)*pkts_queued_syn[k])
                if t - time_syn[k] >= 45:
                    back_queue += int((attack_syn_percent)*pkts_queued_syn[k])

            
            available_syn_q = back_queue
            if(back_queue < 0):
                print("DDoSed at RTT 10000 at epoch {}".format(i))
            print("Backlog Size {} \n".format(available_syn_q))
            
            ##RTT = rttEstimate(rem_ISP_queue[0]+rem_ISP_queue[1]+rem_ISP_queue[2], rem_link_queue, rem_process_queue, available_syn_q, ISP_Cap[0])
            RTT = rttEstimate(rem_ISP_queue[attack_ingress], rem_link_queue, rem_process_queue, available_syn_q, ISP_Cap[0])
            if(j is 'RandMix'):
                RTT_randMix+=[RTT]
            elif(j is 'RandIngress'):
                RTT_randIngress+=[RTT]
            else:
                RTT_QLearn+=[RTT]
            

                
                
      
            
