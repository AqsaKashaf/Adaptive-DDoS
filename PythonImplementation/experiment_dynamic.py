import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random

RTT_list = []

num_ingress = 3
ISP_Cap = [10000000/num_ingress, 10000000/num_ingress, 10000000/num_ingress]    #Static
VM_Cap = 2000
Number_of_VMs = ISP_Cap[0]/VM_Cap
#print(Number_of_VMs)
ISP_Queues = [80*Number_of_VMs, 80*Number_of_VMs, 80*Number_of_VMs]  #Mbits

#print(ISP_Queues)

Traffic_sum = [0,0,0]
packet_drops = [0,0,0]
pkts_to_be_queued = [0,0,0]
pkts_to_be_queued_link = 0
pkts_to_be_queued_process = 0

avail_queue_size = ISP_Queues

occupied_queue_size = [0, 0, 0]
occupied_link_queue_size = 0
occupied_process_queue_size = 0
packet_drops_process = 0
# link_traffic = {'SYN':0,'UDP':0,'DNS':0,'Data':0}

Process_Cap = 200000 #Mbits
Process_Queue = 100 * (Process_Cap/VM_Cap) #Mbits
process_traffic = {'SYN':0,'UDP':0,'DNS':0,'Data':0}

Server_Cap = 180000
Backlog_per_VM = 1024     #Per VM

Link_Cap = 220000
Link_Queue = 100 * (Link_Cap/VM_Cap)
avail_link_queue_size = Link_Queue

amp_factor = np.random.randint(8,13)

num_rounds = 10

Max_attack_budget = 200000 #100Gbits

tcp_size = 0.000048  #TCP Packet Sizes = 60bytes
udp_size = 0.062428   #UDP Packet Sizes = 65,535 bytes
dns_size = amp_factor * udp_size  #DNS Amp Size

#rewards = [5,5,5,10,10,20]
rewards = [-1,-1,-1,10,10,20]

RTT_QLearn = []
RTT_randMix = []
RTT_randIngress = []

time_syn = []
pkts_queued_syn = []

pkts_queued_backlog = []
t_syn = []
o_q = 0

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
# def Firewall(attack, false_negative_rate):                           
#     ingress = list(attack.keys())[0]
#     for i in range(0,3):
#         attack[ingress][i] = attack[ingress][i]*(1-false_negative_rate)      #PErcentage of attack traffic that goes through

#     return attack

#Benign Traffic Implementation
def BenignTraffic():
    background = 3000000
    benign_traffic = {'SYN':0,'DATA':0}
    #Total Connections = Page views per user * Number of users of the website (5.54 * 1821.6*10^3)
    #Number of users of the website = (Reach per million * total internet users)/10^6 = (414*4.4*10^9)/10^6
    benign_traffic['SYN'] = 1530
    #Assuming the data traffic is 5 times the SYN connections received
    benign_traffic['DATA'] = 180000
    return background, benign_traffic

#Merging Attack and Benign Traffic
def mergeTraffic(attack):
    background, benign_traffic = BenignTraffic()
    back = [75000,75000,75000]
    # back[0] = np.random.randint(100000,300000)/3
    # back[1] = np.random.randint(100000,300000)/3
    # back[2] = np.random.randint(100000,300000)/3
    # back[0] = np.random.randint(1000000,3000000)/3
    # back[1] = np.random.randint(1000000,3000000)/3
    # back[2] = np.random.randint(1000000,3000000)/3
    #Get keys
    ingress = list(attack.keys())[0]
    attack_syn_vol = attack[ingress][0]/(attack[ingress][0]+benign_traffic['SYN'])
    benign_syn_vol = benign_traffic['SYN']/(attack[ingress][0]+benign_traffic['SYN'])
    Traffic = {0:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},1:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},2:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0}}
    for j in range(0,3):
        if(j is ingress):
            Traffic[j]={'SYN':attack[ingress][0]+benign_traffic['SYN'],'UDP':attack[ingress][1],'DNS':attack[ingress][2], 'Data':benign_traffic['DATA']/3,'Background':back[j]}
        else:
            Traffic[j]={'SYN':0,'UDP':0,'DNS':0,'Data':benign_traffic['DATA']/3,'Background':back[j]}
    return Traffic, attack_syn_vol, benign_syn_vol      #Return benign and attack syn volume for SYN

def TrafficVolume(rate,ingress):
    Traffic = {0:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},1:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0},2:{'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0}}
    for j in range(0,3):
        if(j is ingress):
            Traffic[j] = {'SYN':rate,'UDP':0,'DNS':0,'Data':0,'Background':0}
        else:
            Traffic[j] = {'SYN':0,'UDP':0,'DNS':0,'Data':0,'Background':0}
    return Traffic
    
# Calculates the congestion in the ISP queue
def calculateCongestionISP(traffic):
    rem_traffic = traffic
    # Traffic[j] = {'SYN':0,'UDP':0,'DNS':0,'Data':benign_traffic['DATA'],'Background':background}
    for i in range(0,num_ingress):  
    #i = 1   
        Traffic_sum[i] = sum(traffic[i].values())
        print("Sum of traffic at ingress {}: {}".format(i, Traffic_sum[i]))
        print("background traffic at {}: {}".format(i, traffic[i]['Background']))
        print("data traffic at {}: {}".format(i,traffic[i]["Data"]))
        pkts_to_be_queued[i] = Traffic_sum[i] + occupied_queue_size[i] - ISP_Cap[i]
        print ("packets to be queued at isp ingress {}: {}".format(i,pkts_to_be_queued[i]))
        P_syn = traffic[i]['SYN']/(Traffic_sum[i]+1)
        P_udp = traffic[i]['UDP']/(Traffic_sum[i]+1)
        P_dns = traffic[i]['DNS']/(Traffic_sum[i]+1)
        P_data = traffic[i]['Data']/(Traffic_sum[i]+1)
        P_bg = traffic[i]['Background']/(Traffic_sum[i]+1)
        
        if(pkts_to_be_queued[i] < 0):
            pkts_to_be_queued[i] = 0
            packet_drops[i] = 0
            occupied_queue_size[i] = 0
            rem_traffic[i]['SYN'] = traffic[i]['SYN'] + P_syn*occupied_queue_size[i]
            rem_traffic[i]['UDP'] = traffic[i]['UDP'] + P_udp*occupied_queue_size[i]
            rem_traffic[i]['DNS'] = traffic[i]['DNS'] + P_dns*occupied_queue_size[i]
            rem_traffic[i]['Data'] = traffic[i]['Data'] + P_data*occupied_queue_size[i]
            rem_traffic[i]['Background'] = traffic[i]['Background'] + P_bg*occupied_queue_size[i]
        #print(pkts_to_be_queued[i])
        #time.sleep(1)
 
        else:
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
                #time.sleep(1)

        avail_queue_size[i] = ISP_Queues[i] - occupied_queue_size[i]
        #print("Packet Drop at Ingress {} is {}".format(i,packet_drops[i]))
        # print("remaining traffic at ingress {} is {}".format(i,rem_traffic))
        print("Occupied Queue Size {} at ingress {}".format(occupied_queue_size[i],i))
    return occupied_queue_size, rem_traffic
	
# Calculates the congestion in the Link queue
def calculateCongestionLink(traffic, occupied_link_queued_size):
    
    queue_occ = occupied_link_queued_size
    link_traffic = {'SYN':0,'UDP':0,'DNS':0,'Data':0}
    rem_link_traffic = link_traffic
    print("Traffic Coming into Link", traffic)

    for i in range(0,num_ingress):
        link_traffic['SYN'] += traffic[i]['SYN']
        link_traffic['UDP'] += traffic[i]['UDP']
        link_traffic['DNS'] += traffic[i]['DNS']
        link_traffic['Data'] += traffic[i]['Data']

    total_link_traffic = sum(link_traffic.values())
    print("total_link_traffic",total_link_traffic)

    pkts_to_be_queued_link = total_link_traffic + queue_occ - Link_Cap
    print ("packets to be queued at link {}".format(pkts_to_be_queued_link))
    P_syn = link_traffic['SYN']/total_link_traffic
    P_udp = link_traffic['UDP']/total_link_traffic
    P_dns = link_traffic['DNS']/total_link_traffic
    P_data = link_traffic['Data']/total_link_traffic 
    
    if(pkts_to_be_queued_link < 0):
        pkts_to_be_queued_link = 0
        queue_occ = 0
        rem_link_traffic['SYN'] = link_traffic['SYN'] + P_syn*queue_occ
        rem_link_traffic['UDP'] = link_traffic['UDP'] + P_udp*queue_occ
        rem_link_traffic['DNS'] = link_traffic['DNS'] + P_dns*queue_occ
        rem_link_traffic['Data'] = link_traffic['Data'] + P_data*queue_occ
    
        

    else:
        if pkts_to_be_queued_link <= Link_Queue:
            packet_drops_link = 0
            queue_occ = pkts_to_be_queued_link
            #queue_occ = occupied_link_queued_size
            rem_link_traffic['SYN'] = link_traffic['SYN'] - P_syn*queue_occ
            rem_link_traffic['UDP'] = link_traffic['UDP'] - P_udp*queue_occ
            rem_link_traffic['DNS'] = link_traffic['DNS'] - P_dns*queue_occ
            rem_link_traffic['Data'] = link_traffic['Data'] - P_data*queue_occ
        
        if pkts_to_be_queued_link > Link_Queue:
            packet_drops_link = pkts_to_be_queued_link - Link_Queue
            #queue_occ = Link_Queue
            queue_occ = Link_Queue
            rem_link_traffic['SYN'] = link_traffic['SYN'] - P_syn*(queue_occ+packet_drops_link)
            rem_link_traffic['UDP'] = link_traffic['UDP'] - P_udp*(queue_occ+packet_drops_link)
            rem_link_traffic['DNS'] = link_traffic['DNS'] - P_dns*(queue_occ+packet_drops_link)
            rem_link_traffic['Data'] = link_traffic['Data'] - P_data*(queue_occ+packet_drops_link)

    avail_link_queue_size = Link_Queue - queue_occ
#    print("Packet Drops {}".format(packet_drops_link))
    print ("rem_link_traffic", rem_link_traffic)
    return avail_link_queue_size, rem_link_traffic, queue_occ
		
# Calculates the congestion in the target process queue
def calculateCongestionProcess(traffic, occupied_process_queue_size):
    global packet_drops_process
    proc_occ = occupied_process_queue_size
    print ("incoming process traffic", traffic)
    rem_process_traffic = process_traffic
    #for i in range(0,num_ingress):  
    process_traffic['SYN'] = traffic['SYN']
    process_traffic['UDP'] = traffic['UDP']
    process_traffic['DNS'] = traffic['DNS']
    process_traffic['Data'] = traffic['Data']

    total_process_traffic = sum(process_traffic.values())
    print("total_process_traffic",total_process_traffic)
    
    P_syn = process_traffic['SYN']/total_process_traffic
    P_udp = process_traffic['UDP']/total_process_traffic
    P_dns = process_traffic['DNS']/total_process_traffic
    P_data = process_traffic['Data']/total_process_traffic

    pkts_to_be_queued_process = total_process_traffic + proc_occ - Process_Cap
    print("Packets to be queued {}".format(pkts_to_be_queued_process))
    if(pkts_to_be_queued_process < 0):
        #print("Less than zero")
        pkts_to_be_queued_process = 0
        proc_occ = 0
        packet_drops_process = 0
        #proc_occ = proc_occ + pkts_to_be_queued_process
        rem_process_traffic['SYN'] = process_traffic['SYN'] + P_syn*proc_occ
        rem_process_traffic['UDP'] = process_traffic['UDP'] + P_udp*proc_occ
        rem_process_traffic['DNS'] = process_traffic['DNS'] + P_dns*proc_occ
        rem_process_traffic['Data'] = process_traffic['Data'] + P_data*proc_occ
        
     
    else:
        #print("Else")
        if pkts_to_be_queued_process <= Process_Queue:
            #print("greater than zero_1")
            packet_drops_process = 0
            proc_occ = pkts_to_be_queued_process
            rem_process_traffic['SYN'] = process_traffic['SYN'] - P_syn*proc_occ
            rem_process_traffic['UDP'] = process_traffic['UDP'] - P_udp*proc_occ
            rem_process_traffic['DNS'] = process_traffic['DNS'] - P_dns*proc_occ
            rem_process_traffic['Data'] = process_traffic['Data'] - P_data*proc_occ
            
        if pkts_to_be_queued_process > Process_Queue:
            #print("greater than zero_2")
            packet_drops_process = pkts_to_be_queued_process - Process_Queue
            proc_occ = Process_Queue
            rem_process_traffic['SYN'] = process_traffic['SYN'] - P_syn*(proc_occ+packet_drops_process)
            rem_process_traffic['UDP'] = process_traffic['UDP'] - P_udp*(proc_occ+packet_drops_process)
            rem_process_traffic['DNS'] = process_traffic['DNS'] - P_dns*(proc_occ+packet_drops_process)
            rem_process_traffic['Data'] = process_traffic['Data'] - P_data*(proc_occ+packet_drops_process)

    avail_process_queue_size = Process_Queue - proc_occ
    #print("Packet Drops {}".format(packet_drops_process))
    
    return avail_process_queue_size, rem_process_traffic, proc_occ


def backlogCongestion(V_syn, o_q, pkts_queued_backlog, t_syn, total_connections):
    pkts_queued_syn = pkts_queued_backlog
    occ_syn_q = o_q
    time_syn = t_syn
    incoming_connections = V_syn/tcp_size
    if incoming_connections + occ_syn_q <= total_connections:
        packets_dropped_syn = 0
        occ_syn_q += incoming_connections
        time_syn+=[time.time()]
        pkts_queued_syn+=[incoming_connections]
    if incoming_connections + occ_syn_q > total_connections: 
        packets_dropped_syn = incoming_connections + occ_syn_q - total_connections
        occ_syn_q = total_connections
    
    print("V_syn", V_syn)
    return occ_syn_q, pkts_queued_syn, time_syn

def rttEstimate(ISP_Queues, attack_ingress, Link_Queue, Process_Queue, Backlog_Queue, ISP_Cap, total_connections):
    if (Backlog_Queue >= total_connections):
        rtt = 10000
    rtt = ISP_Queues[attack_ingress]/ISP_Cap[attack_ingress] + Link_Queue/Link_Cap + Process_Queue/Process_Cap
    print("Occ ISP queues",ISP_Queues)
    print("Occ Link queues",Link_Queue)
    print("Occ Process queues",Process_Queue)
    return rtt

if __name__ =="__main__":
    
    ISP_Cap = [1000000/num_ingress, 1000000/num_ingress, 1000000/num_ingress] #Static
    VM_Cap = 2000
    Number_of_VMs = ISP_Cap[0]/VM_Cap
    #print(Number_of_VMs)
    ISP_Queues = [80*Number_of_VMs, 80*Number_of_VMs, 80*Number_of_VMs] #Mbits
    
    expire_time = 45
    totalMachines = Server_Cap/VM_Cap
    total_connections = Backlog_per_VM * totalMachines
    available_syn_q = int(total_connections)
    
    print("Simulator Start!")
    #print("Backlog Size {}".format(available_syn_q))
    #time.sleep(1)
    total_budget = Max_attack_budget
    attack_types = ['RandMix', 'RandIngress', 'Smart']
    RTT = 0
    #attack_budget = 0
    attack_budget_1 = 0.1*(total_budget)
    for i in range(0,num_rounds):
        #if (total_budget > 0):
        print("Entering attack round {}".format(i))
        attack_budget_2 = attack_budget_1+(0.1*total_budget)
        attack_budget = random.uniform(attack_budget_1,attack_budget_2)
        attack_budget_1 = attack_budget_2
        print("Attack Budget", attack_budget)
            #total_budget -= attack_budget
        #else:
            # print("Budget Reached in epoch {}".format(i))
            # break
    
        # attack_budget = 100000
        # total_budget-= attack_budget
        # if(total_budget=0):
        #    print("Budget Reached in epoch {}".format(i))
        #    break
        # attack_budget = total_budget
        
        #for j in attack_types:
        #attack_budget = total_budget
        #attack_budget = Firewall(attack_budget, 0.6)
        attack_budget = attack_budget*(1-0.6)
        attack_vol = getAttackStrategy(num_ingress, attack_budget,'Smart', RTT)
        #attack_vol = Firewall(attack_vol, 0.6)
        attack_ingress = 1
        print("attack_ingress", attack_ingress)
        
        Traffic, attack_syn_vol, benign_syn_vol = mergeTraffic(attack_vol)
        print(Traffic)
        time.sleep(1)
        
#            for l in range(0,3):
#                if(l is attack_ingress):
#                    Traffic[l]={'SYN':Traffic[l]['SYN'],'UDP':Traffic[l]['UDP'],'DNS':Traffic[l]['DNS']}
#                else:
#                    Traffic[l]={'SYN':0,'UDP':0,'DNS':0}
                
        #print(Traffic)
        #print("Attack Type {} Round {} \n".format(j,i)) 
        # Traffic = TrafficVolume(92160+10,1)   
        #print(Traffic)
        occupied_ISP_queue, ISP_Traffic = calculateCongestionISP(Traffic)
        #print("Remaining ISP Queue Lengths {}".format(rem_ISP_queue))
        #print("Traffic processed by ISP to link", ISP_Traffic)

        rem_link_queue, Link_Traffic, occupied_link_queue_size = calculateCongestionLink(ISP_Traffic, occupied_link_queue_size)
        #print("Remaining Link Queue Lengths {}, Occupied {}".format(rem_link_queue, occupied_link_queue_size))
        #print("Traffic Volume {}\n".format(sum(Traffic.values())))
        #print("Traffic processed by link to Process", Link_Traffic)

        rem_process_queue, Process_Traffic, occupied_process_queue_size = calculateCongestionProcess(Link_Traffic, occupied_process_queue_size)
        #print("Remaining Process Queue Lengths {}, Occupied {}".format(rem_process_queue, occupied_process_queue_size))
        #summer = sum(Process_Traffic.values())
        #print("Traffic Volume {} \n".format(sum))
        print("Traffic processed by Process to Server", Process_Traffic)
        print("rem process queue", rem_process_queue)
        
        SYN_VOL = int(Process_Traffic['SYN'])
        #print("SYN Volumes {}".format(SYN_VOL))
        
        attack_syn_percent = attack_syn_vol/(attack_syn_vol + benign_syn_vol)
        benign_syn_percent = benign_syn_vol/(attack_syn_vol + benign_syn_vol)
        
        
        o_q, pkts_queued_backlog, t_syn = backlogCongestion(SYN_VOL, o_q, pkts_queued_backlog, t_syn, total_connections)
        


        t = time.time() 
        for k in range(0,len(t_syn)):
            if t - t_syn[k] >= 1:
                o_q += int((benign_syn_percent)*pkts_queued_backlog[k])
            if t - t_syn[k] >= 45:
                o_q += int((attack_syn_percent)*pkts_queued_backlog[k])

        
        #available_syn_q = back_queue
        #if(available_syn_q < 0):
            #print("DDoSed at RTT 10000 at epoch {}".format(i+1))
            #break
        #print("Backlog Size {}".format(available_syn_q))
        
        ##RTT = rttEstimate(rem_ISP_queue[0]+rem_ISP_queue[1]+rem_ISP_queue[2], rem_link_queue, rem_process_queue, available_syn_q, ISP_Cap[0])
        RTT = rttEstimate(occupied_ISP_queue, attack_ingress, occupied_link_queue_size, occupied_process_queue_size, o_q, ISP_Cap, total_connections)
        RTT_list.append(RTT)
        print("RTT {}\n".format(RTT))
        # if(j is 'RandMix'):
        #     RTT_randMix+=[RTT]
        # elif(j is 'RandIngress'):
        #     RTT_randIngress+=[RTT]
        # else:
        #     RTT_QLearn+=[RTT]
            
print("RTT LIST", RTT_list)