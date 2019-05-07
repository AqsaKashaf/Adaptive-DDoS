import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random
import threading

num_ingress = 3
ISP_Cap = 10000000
ISP_Queues = [80,80,80]

Process_Cap = 200000
Process_Queue = 100

Server_Cap = 100000
Backlog = 256

Link_Cap = 500000
Link_Queue = 100

amp_factor = np.random.randint(8,13)

num_rounds = 500

Max_attack_budget = 500000

tcp_size = 0.00004
udp_size = 0.0625
dns_size = amp_factor * udp_size

rewards = [-10,-10,-10,10,10,20]

RTT_QLearn = []
RTT_randMix = []
RTT_randIngressAttack = []

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

def getAttackStrategy(ISPIngress, Budget, Attack = "Smart", RTT):
    attack_volume = list(get_tuple(3,100))
    #total_budget = Budget
    attack = {'TCP':0,'UDP':0,'DNS':0, 'Ingress':0}
    #while(total_budget>=0):
    
    #    attack_budget = random.uniform(1, total_budget)     Do all this in Main
    #    total_budget-= attack_budget
        
    if(Attack is "RandMix"):
        x = np.random.randint(0,5151)
        attack = attack_volume[x]
        ingress = 1
        
    elif(Attack is "RandIngress"):
        #x = np.random.randint(0,5151)
        attack['TCP'] = 100/3
        attack['UDP'] = 100/3 
        attack['DNS'] = 100/3 
        ingress = np.random.randint(1,ISPIngress)
        
    else:
        rewards+= RTT
        attack, ingress = q_learn(rewards)
    
    attack['TCP'] = attack['TCP']/100*attack_budget
    attack['UDP'] = attack['UDP']/100*attack_budget 
    attack['DNS'] = attack['DNS']/100*attack_budget 
    attack['Ingress'] = ingress 
    
    return attack

def Firewall(attack, percent_ack):
    attack['TCP']*= (1-percent_ack)
    attack['DNS']*= (1-percent_ack)
    attack['UDP']*= (1-percent_ack)
    return attack

def BenignTraffic():
    background = random.uniform(1000,10000)
    benign_traffic = {'SYN':0,'DATA':0}
    benign_traffic['SYN'] = random.uniform(70,100)
    benign_traffic['DATA'] = random.uniform(1,40)
    return background, benign_traffic

def mergeTraffic():
    background, benign_traffic = BenignTraffic()
    attack = getAttackStrategy(3, Max_attack_budget, Attack = "Smart", [0,0,0,0,0,0])
    Traffic = {'TCP':0,'UDP':0,'DNS':0, 'Data':0, 'Ingress':0, 'Benign':0}
    Traffic['TCP'] = attack['TCP'] + benign_traffic['SYN'] * tcp_size
    Traffic['UDP'] = attack['UDP']
    Traffic['DNS'] = attack['DNS']
    Traffic['Ingress'] = attack['Ingress']
    Traffic['Data'] = benign_traffic['Data'] * udp_size
    Traffic['Benign'] = background * udp_size
    return Traffic    
        
#threading.Thread(target=lambda: every(5, mergeTraffic)).start()
