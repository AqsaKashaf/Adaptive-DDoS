import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random
import threading

num_ingress = 3
ISP_Cap = 10000000
VM_Cap = 200000
Number_of_VMs = 2
ISP_Queues = [80,80,80]

Process_Cap = 2000000
Process_Queue = 100

Server_Cap = 1000000
Backlog = 256

Link_Cap = 5000000
Link_Queue = 100

amp_factor = np.random.randint(8,13)

num_rounds = 500

Max_attack_budget = 500000

tcp_size = 0.000006  #TCP Packet Sizes
udp_size = 0.0625   #UDP Packet Sizes
dns_size = amp_factor * udp_size  #DNS Amp Size

rewards = [-10,-10,-10,10,10,20]

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
def getAttackStrategy(ISPIngress, Budget, Attack = "Smart", RTT):
    attack_volume = list(get_tuple(3,100))

    ingress = 1  
    if(Attack is "RandMix"):
        x = np.random.randint(0,5151)
        attack_vol = attack_volume[x]
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
        attack = {ingress:[attack[0],attack[1],attack[2]]}
    
    for i in range(0,3):
        attack[ingress][i] = attack[ingress][i]/100*attack_budget

    
    return attack

#Firewall Implementation
def Firewall(attack, percent_ack):
    for i in range(0,3):
        attack[ingress][i] = attack[ingress][i]*(1-percent_ack)

    return attack

#Benign Traffic Implementation
def BenignTraffic():
    background = random.uniform(1000,10000)
    benign_traffic = {'SYN':0,'DATA':0}
    benign_traffic['SYN'] = random.uniform(70,100)
    benign_traffic['DATA'] = random.uniform(1,40)
    return background, benign_traffic

#Merging Attack and Benign Traffic
def mergeTraffic(attack):
    background, benign_traffic = BenignTraffic()
    #Get keys
    ingress = list(attack.keys())[0]
    
    #Merge everything together
    Traffic = {ingress:{(attack[ingress][0]+benign_traffic['SYN']) * tcp_size, attack[ingress][1]*udp_size, attack[ingress][2]*dns_size, benign_traffic['DATA'] *udp_size,background*udp_size}}
    return Traffic  

if __name__ =="__main__":
    
    print("Simulator Start!")
    total_budget = Max_attack_budget
    attack_types = ['RandMix', 'RandIngress', 'Smart']
    for i in range(0,num_rounds):
        
        RTT = 0
        attack_budget = random.uniform(1, total_budget)
        total_budget-= attack_budget
        
        for j in attack_types:
            attack_vol = getAttackStrategy(num_ingress, attack_budget, j, RTT)
            attack_vol = FireWall(attack_vol, 0.6)
            Traffic = mergeTraffic(attack_vol)
            
            #Create your own functions

        
#threading.Thread(target=lambda: every(5, mergeTraffic)).start()
