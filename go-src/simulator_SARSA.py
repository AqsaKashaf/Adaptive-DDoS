import gym
import numpy as np
import time


def init_q(s, a, type="ones"):
    """
    @param s the number of states
    @param a the number of actions
    @param type random, ones or zeros for the initialization
    """
    if type == "ones":
        return np.ones((s, a))
    elif type == "random":
        return np.random.random((s, a))
    elif type == "zeros":
        return np.zeros((s, a))


def epsilon_greedy(Q, epsilon, n_actions, s, train=False):
    """
    @param Q Q values state x action -> value
    @param epsilon for exploration
    @param s number of states
    @param train if true then no random actions selected
    """
    if train or np.random.rand() < epsilon:
        action = np.argmax(Q[s, :])
    else:
        action = np.random.randint(0, n_actions)
    return action

def expected_sarsa(alpha, gamma, epsilon, episodes, max_steps, n_tests, render = False, test=False):
    #env = gym.make('Taxi-v2')
    tot_time = 0.0
    n_states, n_actions = 8, 5151 * 5
    Q = init_q(n_states, n_actions, type="zeros")
    timestep_reward = []
    for episode in range(episodes):
        print("Episode:", episode)
        total_reward = 0
        s = np.random.randint(0,n_states)
        t = 0
        done = False
        if(tot_time>=10000):
            break
        while t < max_steps:
            #if render:
            #    env.render()
            t += 1
            a = epsilon_greedy(Q, epsilon, n_actions, s)
            #s_, reward, done, info = env.step(a)
            s_ = np.random.randint(0,n_states)
            reward = rewards[s_]
            total_reward += reward
            if(total_reward >= max_reward):
                done = True
            if done:
                Q[s, a] += alpha * ( reward  - Q[s, a] )
            else:
                expected_value = np.mean(Q[s_,:])
                # print(Q[s,:], sum(Q[s,:]), len(Q[s,:]), expected_value)
                Q[s, a] += alpha * (reward + (gamma * expected_value) - Q[s, a])
            s = s_
            if done:
                if True:
                    print(f"This episode took",t," timesteps and reward",total_reward)
                    tot_time+=t

                timestep_reward.append(total_reward)
                break
    #if render:
    #    print(f"Here are the Q values:\n{Q}\nTesting now:")
    print(Q)
    if test:
        test_agent(Q, n_tests, n_actions, n_states)
    return timestep_reward,Q

def test_agent(Q, n_tests, n_actions, n_states, delay=0.1):
    for test in range(n_tests):
        print("Test #{",test," }")
        s = np.random.randint(0,n_states)
        done = False
        epsilon = 0
        total_reward = 0
        while True:
            time.sleep(delay)
            #env.render()
            a = epsilon_greedy(Q, epsilon, n_actions, s, train=True)
            print("Choose Action",a,"for State",s)
            #s, reward, done, info = env.step(a)
            s_ = np.random.randint(0,n_states)
            reward = rewards[s_]
            if(total_reward >= max_reward):
                done = True
            total_reward += reward
            if done:
                print("Episode Reward:",total_reward)
                time.sleep(0.5)
                break


if __name__ =="__main__":
    alpha = 0.1
    gamma = 0.9
    epsilon = 0.9
    episodes = 10000
    max_steps = 2500
    n_tests = 20
    rewards = [-10.0,-10.0,-10.0,-10.0,-10.0,10.0,10.0,20.0]
    start = time.time()
    max_reward = np.max(np.asarray(rewards))
    timestep_reward,q_table = expected_sarsa(alpha, gamma, epsilon,episodes, max_steps, n_tests,render=False, test=False)
    #timestep_reward = expected_sarsa(alpha, gamma, epsilon,episodes, max_steps, n_tests,render=False, test=True)
    #print(timestep_reward)
    end = time.time()
#    type1 = np.max(q_table[:,0])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#    type2 = np.max(q_table[:,1])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#    type3 = np.max(q_table[:,2])/(np.max(q_table[:,0])+(np.max(q_table[:,1]))+np.max(q_table[:,2]))
#    print("Attack Type 1:",type1*100,"Attack Type 2:",type2*100,"Attack Type 3:",type3*100)
    print("SARSA Time", end-start)