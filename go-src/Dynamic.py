import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random

num_ingress = 3
ISP_Cap = 2024
ISP_Queues = [100,100,100]

Process_Cap = 1024
Process_Queue = 100

Server_Cap = 1024
Backlog = 256

Link_Cap = 1024
Link_Queue = 100

amp_factor = np.random.randint(8,13)
print(amp_factor)

num_rounds = 500

Max_attack_budget = 700

tcp_size = 0.00004
udp_size = 0.0625
dns_size = amp_factor * udp_size

RTT_QLearn = []
RTT_randMix = []
RTT_randIngressAttack = []


def get_tuple(length, total):
    return filter(lambda x:sum(x)==total,product(range(total+1),repeat=length))

def attack(at_type,ing,pc,sc,lc,isp_cap):
    if(at_type is 'TCP'):
        #time.sleep(0.1)
        sc-= tcp_size
        #time.sleep(0.001)
        isp_cap[ing]-= tcp_size
    elif(at_type is 'UDP'):
        #time.sleep(0.01)
        lc-= udp_size
        #time.sleep(0.001)
        isp_cap[ing]-= udp_size
        pc-= udp_size
    else:
        for i in range(amp_factor):
            #time.sleep(0.01)
            lc-= udp_size
            #time.sleep(0.001)
            isp_cap[ing]-= udp_size
            pc-= udp_size
    return pc,sc,lc,isp_cap


def randMixAttack(pc,sc,lc,ic,budget):
    pc,sc,lc,isp_cap = pc,sc,lc,ic
    bits_to_attack = 0
    
    attack_vol = {'TCP':0,'UDP':0,'DNS':0}
    while((attack_vol['TCP'] + attack_vol['UDP'] + attack_vol['DNS'])<=budget):
        type=np.random.randint(0,3)
        
        if(type==0):
            pc,sc,lc,isp_cap=attack('TCP',1,pc,sc,lc,isp_cap)
            attack_vol['TCP']+=tcp_size
            bits_to_attack+=tcp_size
            
        elif(type==1):
            pc,sc,lc,isp_cap=attack('UDP',1,pc,sc,lc,isp_cap)
            attack_vol['UDP']+=udp_size
            bits_to_attack+=udp_size
            
        else:
            pc,sc,lc,isp_cap=attack('DNS',1,pc,sc,lc,isp_cap)
            attack_vol['DNS']+=dns_size
            bits_to_attack+=dns_size
            
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,bits_to_attack
        #    return 0,0,0,[0,0,0]
        time.sleep(0.001)      
        #Congestion Delay
    return pc,sc,lc,isp_cap,budget

def SmartAttack(vol,ing,pc,sc,lc,isp_cap):
    done = False
    bits_to_attack = 0
    
    while(not done):
        type=np.random.randint(0,3)
        
        if(vol[type]==0):
            pc,sc,lc,isp_cap=attack('TCP',ing,pc,sc,lc,isp_cap)
            vol[type]-=tcp_size
            
        elif(vol[type]==1):
            pc,sc,lc,isp_cap=attack('UDP',ing,pc,sc,lc,isp_cap)
            vol[type]-=udp_size
            
        else:
            pc,sc,lc,isp_cap=attack('DNS',ing,pc,sc,lc,isp_cap)
            vol[type]-=dns_size
            
        bits_to_attack+= vol[type]
        
        if(vol[type]<0):
            vol[type] = 0
        if(vol[0]+vol[1]+vol[2]==0):
            done = True
            
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,bits_to_attack

    return pc,sc,lc,isp_cap,budget
                
def randIngressAttack(pc,sc,lc,ic,budget):
    bits_to_attack = 0
    pc,sc,lc,isp_cap = pc,sc,lc,ic
    
    attack_vol = {'TCP':0,'UDP':0,'DNS':0}
    while((attack_vol['TCP'] + attack_vol['UDP'] + attack_vol['DNS'])<=budget):
        type=np.random.randint(0,3)
        randing=np.random.randint(0,num_ingress)
        
        if(type==0):
            pc,sc,lc,isp_cap=attack('TCP',randing,pc,sc,lc,isp_cap)
            attack_vol['TCP']+=tcp_size
            bits_to_attack+=tcp_size
            
        elif(type==1):
            pc,sc,lc,isp_cap=attack('UDP',randing,pc,sc,lc,isp_cap)
            attack_vol['UDP']+=udp_size
            bits_to_attack+=udp_size
            
        else:
            pc,sc,lc,isp_cap=attack('DNS',randing,pc,sc,lc,isp_cap)
            attack_vol['DNS']+=dns_size
            bits_to_attack+=dns_size
            
        time.sleep(0.001)           #Congestion Delay
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,bits_to_attack
#        print("Attack {}, PC {}, SC {}, LC {}, IC {}".format(i,pc,sc,lc,isp_cap))
    return pc,sc,lc,isp_cap,budget

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
    #print("Attack Type:",x[k])
    #print("Ingress:", int(ind[1] / 5151))
            
if __name__ =="__main__":
    
    print("Simulator Start!")
    
    attack_budget = Max_attack_budget
    
    pc,sc,lc,isp_cap = Process_Queue,Backlog,Link_Queue,ISP_Queues
    bits_Mix, bits_Ing, bits_Q = 0,0,0
    
    #start = time.time()
    for i in range(num_rounds):
        
        budget = random.uniform(1, attack_budget)
        attack_budget-= budget
        
        print("Budget in RandMix:",budget)
        
        pc,sc,lc,isp_cap,bits=randMixAttack(pc,sc,lc,isp_cap,budget)
        bits_Mix+= bits
        #end = time.time()
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            RTT_randMix+= [10000]
            break
        else:
            congestion = (isp_cap[0]+isp_cap[1]+isp_cap[2])/ISP_Cap + pc/Process_Cap + sc/Server_Cap + lc/Link_Cap
            RTT_randMix+= [congestion]
            
        if(attack_budget<=0):
            break
        
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}".format(i))
    print("Successful DDoS in Randmix in {} attacks by sending {} bits".format(i+1,bits_Mix))
        
    attack_budget = Max_attack_budget   
    pc,sc,lc,isp_cap = Process_Queue,Backlog,Link_Queue,ISP_Queues   
    #start = time.time()
    for i in range(num_rounds):
        
        budget = random.uniform(1, attack_budget)
        print("Budget in Rand Ingress:",budget)
        attack_budget-= budget
        
        pc,sc,lc,isp_cap,bits=randIngressAttack(pc,sc,lc,isp_cap,budget)
        bits_Ing+= bits
        #end = time.time()
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            RTT_randIngressAttack+= [10000]
            break
        else:
            congestion = (isp_cap[0]+isp_cap[1]+isp_cap[2])/ISP_Cap + pc/Process_Cap + sc/Server_Cap + lc/Link_Cap
            RTT_randIngressAttack+= [congestion]
        
        if(attack_budget<=0):
            break
        
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}".format(i))
    print("Successful DDoS in RandIngress in {} attacks by sending {} packets".format(i+1,bits_Ing))
    
    attack_budget = Max_attack_budget 
    pc,sc,lc,isp_cap = Process_Queue,Backlog,Link_Queue,ISP_Queues   
    #start = time.time()
    RTT = [-10,-10,-10,10,10,20]
    
    for i in range(num_rounds):
        
        attacker,ingress = q_learn(RTT)
                
        budget = random.uniform(1,attack_budget)
        attack_budget-= budget
        
        print("Budget in QLearn:",budget)
        
        attack_list =[attacker[0]/100*budget,attacker[1]/100*budget,attacker[2]/100*budget]
        
        pc,sc,lc,isp_cap,bits=SmartAttack(attack_list,ingress,pc,sc,lc,isp_cap)
        bits_Q+= bits
        congestion = (isp_cap[0]+isp_cap[1]+isp_cap[2])/ISP_Cap + pc/Process_Cap + sc/Server_Cap + lc/Link_Cap
        #end = time.time()
        for l in range(0,3):
            RTT[l]-=(congestion)
        for l in range(3,6):
            RTT[l]+=(congestion)
            
        if ((pc <= 0) and (sc <= 0) and (lc <= 0) and (isp_cap[0] <= 0) and (isp_cap[1] <= 0) and (isp_cap[2] <= 0)):
            RTT_QLearn+= [10000]
            break
        else:
            
            RTT_QLearn+= [congestion]
        if(attack_budget<=0):
            break
        
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}".format(i))
    print("Successful DDoS in Q-Learning in {} attacks by sending {} bits".format(i+1,bits_Q))
    
#print("Successful DDoS in {} attacks".format(i))
    
    
        
        
    
