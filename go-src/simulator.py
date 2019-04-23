import gym
import numpy as np
import random
from IPython.display import clear_output
import time
from itertools import *

no_ingress = 5
states = 8
actions = 5151*no_ingress
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
rewards = [-10.0,-10.0,-10.0,-10.0,-10.0,10.0,10.0,20.0]
max_reward = np.max(np.asarray(rewards))

start=time.time()
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
        clear_output(wait=True)
        print("Episodes: ",i)

print("Training finished.\n")
#print(q_table)
end=time.time()

#type1 = np.max(q_table[:,0])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#type2 = np.max(q_table[:,1])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#type3 = np.max(q_table[:,2])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#print("Attack Type 1:",type1*100,"Attack Type 2:",type2*100,"Attack Type 3:",type3*100)
print("Q Learning:", end-start)
ind = np.unravel_index(np.argmax(q_table, axis=None), q_table.shape)
print(ind)

def get_tuple(length, total):
    return filter(lambda x:sum(x)==total,product(range(total+1),repeat=length))

x=list(get_tuple(3,100))
k= ind[1] % 5151

print("Attack Type:",x[k])
print("Ingress:", int(ind[1] / 5151))
        


#print(len(list(get_tuple(3,100))))