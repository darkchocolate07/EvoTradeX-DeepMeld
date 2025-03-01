import gym
import numpy as np

class CustomEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(4,))
        self.action_space = gym.spaces.Discrete(2)
        self.state = None
    def reset(self):
        self.state = np.zeros(4)
        return self.state
    def step(self, action):
        reward = np.random.randn()
        done = bool(np.random.rand() < 0.05)
        self.state = np.random.randn(4)
        return self.state, reward, done, {}
