import numpy as np
import matplotlib.pyplot as plt
import time
from itertools import *
import random

num_ingress = 3
ISP_Cap = [2000,2000,2000]
Process_Cap = 1000
Server_Cap = 256
Link_Cap = 1000
amp_factor = 5
num_rounds = 50

RTT_QLearn = []
RTT_randMix = []
RTT_randIngressAttack = []
    
def get_tuple(length, total):
    return filter(lambda x:sum(x)==total,product(range(total+1),repeat=length))

def attack(at_type,ing,pc,sc,lc,isp_cap):
    if(at_type is 'TCP'):
        time.sleep(0.1)
        sc-= 1
        time.sleep(0.001)
        isp_cap[ing]-= 1
    elif(at_type is 'UDP'):
        time.sleep(0.01)
        lc-= 1
        time.sleep(0.001)
        isp_cap[ing]-= 1
        pc-= 1
    else:
        for i in range(amp_factor):
            time.sleep(0.05)
            lc-= 1
            time.sleep(0.001)
            isp_cap[ing]-= 1
            pc-= 1
    return pc,sc,lc,isp_cap


def randMixAttack(Process_Cap,Server_cap,Link_Cap,iSP_Cap):
    pc,sc,lc,isp_cap = Process_Cap,Server_cap,Link_Cap,iSP_Cap
    pkts = 0
    attack_vol = {'TCP':0,'UDP':0,'DNS':0}
    while((attack_vol['TCP'] + attack_vol['UDP'] + attack_vol['DNS'])!=100):
        type=np.random.randint(0,3)
        if(type==0):
            pc,sc,lc,isp_cap=attack('TCP',1,pc,sc,lc,isp_cap)
            attack_vol['TCP']+=1
        elif(type==1):
            pc,sc,lc,isp_cap=attack('UDP',1,pc,sc,lc,isp_cap)
            attack_vol['UDP']+=1
        else:
            pc,sc,lc,isp_cap=attack('DNS',1,pc,sc,lc,isp_cap)
            attack_vol['DNS']+=1
        #if ((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,pkts
        else:
            pkts+= 1
        #    return 0,0,0,[0,0,0]
        time.sleep(0.001)           #Congestion Delay
    return pc,sc,lc,isp_cap,pkts

def SmartAttack(vol,ing,pc,sc,lc,isp_cap):
    pkts = 0
    done = False
    while(not done):
        type=np.random.randint(0,3)
        if(vol[type]==0):
            pc,sc,lc,isp_cap=attack('TCP',ing,pc,sc,lc,isp_cap)
        elif(vol[type]==1):
            pc,sc,lc,isp_cap=attack('UDP',ing,pc,sc,lc,isp_cap)
        else:
            pc,sc,lc,isp_cap=attack('DNS',ing,pc,sc,lc,isp_cap)    
        vol[type]-= 1
        if(vol[type]<0):
            vol[type] = 1
        if(vol[0]+vol[1]+vol[2]==0):
            done = True
        #if ((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,pkts
        else:
            pkts+=1
    return pc,sc,lc,isp_cap,100
                
def randIngressAttack(Process_Cap,Server_cap,Link_Cap,iSP_Cap):
    pkts = 0
    pc,sc,lc,isp_cap = Process_Cap,Server_cap,Link_Cap,iSP_Cap
    attack_vol = {'TCP':0,'UDP':0,'DNS':0}
    while((attack_vol['TCP'] + attack_vol['UDP'] + attack_vol['DNS'])!=100):
        type=np.random.randint(0,3)
        randing=np.random.randint(0,num_ingress)
        if(type==0):
            pc,sc,lc,isp_cap=attack('TCP',randing,pc,sc,lc,isp_cap)
            attack_vol['TCP']+=1
        elif(type==1):
            pc,sc,lc,isp_cap=attack('UDP',randing,pc,sc,lc,isp_cap)
            attack_vol['UDP']+=1
        else:
            pc,sc,lc,isp_cap=attack('DNS',randing,pc,sc,lc,isp_cap)
            attack_vol['DNS']+=1
        time.sleep(0.001)           #Congestion Delay
        #if ((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            return pc,sc,lc,isp_cap,pkts
        else:
            pkts+= 1
#        print("Attack {}, PC {}, SC {}, LC {}, IC {}".format(i,pc,sc,lc,isp_cap))
    return pc,sc,lc,isp_cap,pkts

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
    
    pc,sc,lc,isp_cap = Process_Cap,Server_Cap,Link_Cap,ISP_Cap
    packets_Mix, packets_Ing, packets_Q = 0,0,0
    start = time.time()
    for i in range(num_rounds):
        pc,sc,lc,isp_cap,pkts=randMixAttack(pc,sc,lc,isp_cap)
        packets_Mix+= pkts
        end = time.time()
        #if((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            RTT_randMix+= [10000]
            break
        else:
            RTT_randMix+= [end - start]
            
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}, IC {}".format(i+1,isp_cap))
    print("Successful DDoS in Randmix in {} attacks by sending {} packets".format(i+1,packets_Mix))
        
    ISP_Cap = [2000,2000,2000]
    pc,sc,lc,isp_cap = Process_Cap,Server_Cap,Link_Cap,ISP_Cap 
    start = time.time()
    for i in range(num_rounds):
        pc,sc,lc,isp_cap,pkts=randIngressAttack(pc,sc,lc,isp_cap)
        packets_Ing+= pkts
        end = time.time()
        #if((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            RTT_randIngressAttack+= [10000]
            break
        else:
            RTT_randIngressAttack+= [end - start]
            
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}, IC {}".format(i+1,isp_cap)) 
    print("Successful DDoS in RandIngress in {} attacks by sending {} packets".format(i+1,packets_Ing))
    
    ISP_Cap = [2000,2000,2000]
    pc,sc,lc,isp_cap = Process_Cap,Server_Cap,Link_Cap,ISP_Cap  
    start = time.time()
    RTT = [-10,-10,-10,10,10,20]
    
    for i in range(num_rounds):
        attacker,ingress = q_learn(RTT)
        attack_list =[attacker[0],attacker[1],attacker[2]]
        
        pc,sc,lc,isp_cap,pkts=SmartAttack(attack_list,ingress,pc,sc,lc,isp_cap)
        packets_Q+= pkts
        end = time.time()
        for l in range(0,3):
            RTT[l]-=(end-start)
        for l in range(3,6):
            RTT[l]+=(end-start)
            
        #if((pc <= 0) or (sc <= 0) or (lc <= 0) or (isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
        if((isp_cap[0] <= 0) or (isp_cap[1] <= 0) or (isp_cap[2] <= 0)):
            RTT_QLearn+= [10000]
            break
        else:
            RTT_QLearn+= [end - start]
            
        new_isp_cap = random.choice(isp_cap)
        isp_cap[0], isp_cap[1], isp_cap[2] = int(new_isp_cap), int(new_isp_cap), int(new_isp_cap)
        
        print("Attack {}, IC {}".format(i+1,isp_cap)) 
    print("Successful DDoS in Q-Learning in {} attacks by sending {} packets".format(i+1,packets_Q))
    

    
    
        
        
    
