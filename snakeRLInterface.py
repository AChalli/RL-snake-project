class Snake:
    def __init__(self): #attributes: snake head, block list / snake body, direction, length
        print(1)

    def move(self, S_dir):
        print(S_dir)

    def grow(self):
        print(2)

    def checkSelfEat(self):
        print(3)

    def death(self):
        print(4)


class Reward:
    def __init__(self): #attributes: position, size
        print(1)

    def spawn_reward(self, blocks):
        print(2)


class Environment:
    def __init__(self): #attributes: snake obj, reward obj, window_size, tic_delay, score, done
        print (1)

    def step(self, action):
        print(2)

    def reset(self):
        print(3)

    def render(self, screen):
        print(4)