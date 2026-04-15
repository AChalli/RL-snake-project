import pygame
from random import randrange
import numpy as np

class Snake:
    def __init__(self, tileSize, pos):
        self.tileSize= tileSize
        self.head = pygame.rect.Rect([0, 0, tileSize-2, tileSize-2]) # snake sprite = basic rectangle
        self.head.center = pos
        self.body = [self.head.copy()] #snake body
        starts = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        start = starts[np.random.randint(4)]
        self.direction = pygame.Vector2(start[0] * tileSize, start[1] * tileSize)
        self.length = 1

    def move(self, direction):
        self.head.move_ip(direction)
        self.body.append(self.head.copy())
        self.body = self.body[-self.length:]

    def grow(self):
        self.length+=1

    def selfEat(self):
        return pygame.Rect.collidelist(self.head, self.body[:-1]) != -1

    def death(self):
        self.body[:] = [self.head.copy()]
        self.direction.update(0, 0)
        self.length = 1

class Reward:
    def __init__(self, tileSize, position):
        self.core = pygame.rect.Rect([0,0, tileSize-2, tileSize-2])
        self.core.center = position
        self.tileSize = tileSize
        self.pos = position

    def spawn(self, snakeBody, randPos):
        while True:
            self.pos = randPos()
            if self.pos not in [body.center for body in snakeBody]:
                self.core.center = self.pos
                return self.pos

class Environment:
    def __init__(self, windowSize, ticDelay, tileSize):
        self.range = (tileSize // 2, windowSize - tileSize // 2, tileSize)  # range for reward coordinate generating
        self.tileSize = tileSize
        self.snake = Snake(tileSize, self.getRandomPos())
        self.reward = Reward(tileSize, self.getRandomPos())
        self.windowSize = windowSize
        self.ticDelay = ticDelay
        self.score = 0
        self.numTiles = windowSize // tileSize
        self.screen = pygame.display.set_mode([windowSize] * 2)

    def step(self, action):
        snake = self.snake
        reward = self.reward
        stepReward = 0 #reward for next step
        done = False

        #opposite direction restriction:
        heading_up = self.snake.direction.y < 0
        heading_down = self.snake.direction.y > 0
        heading_left = self.snake.direction.x < 0
        heading_right = self.snake.direction.x > 0

        #convert action into snake movement
        if action == 0 and not heading_down:
            snake.direction.y = -self.tileSize
            snake.direction.x = 0
        elif action == 1 and not heading_up:
            snake.direction.y = self.tileSize
            snake.direction.x = 0
        elif action == 2 and not heading_right:
            snake.direction.x = -self.tileSize
            snake.direction.y = 0
        elif action == 3 and not heading_left:
            snake.direction.x = self.tileSize
            snake.direction.y = 0

        #get s1 distance to food
        s1_dist = abs(snake.head.center[0] - reward.core.center[0]) + abs(snake.head.center[1] - reward.core.center[1])

        #call movement in pygame
        snake.move(snake.direction)

        #get s2 distance to food (post movement)
        s2_dist = abs(snake.head.center[0] - reward.core.center[0]) + abs(snake.head.center[1] - reward.core.center[1])

        #check for death and rerun if dead
        if snake.head.left < 0 or snake.head.right > self.windowSize or snake.head.top < 0 or snake.head.bottom > self.windowSize or snake.selfEat():
            done = True
            stepReward = -10
            #self.rerun()
            return self.getState(), stepReward, done

        # consume reward logic
        if snake.head.center == reward.core.center:
            stepReward = 10
            snake.length += 1
            reward.core.center = reward.spawn(snake.body, self.getRandomPos)
        else:
           #old: stepReward = -0.08 # small step penalty
           #new: distance based shaping instead of constant step penalty
           if s2_dist < s1_dist:
               stepReward = 0.1  # Got closer
           elif s2_dist > s1_dist:
               stepReward = -0.1  # Moved further away
           else:
               stepReward =-0.03

        return self.getState(), stepReward, done



    def getState(self):
        # collect snake direction
        heading_up = self.snake.direction.y < 0
        heading_down = self.snake.direction.y > 0
        heading_left = self.snake.direction.x < 0
        heading_right = self.snake.direction.x > 0

        # collect danger / wall or body direction
        hx, hy = self.snake.head.center
        danger_up = self.isDanger((hx, hy - self.tileSize))
        danger_down = self.isDanger((hx, hy + self.tileSize))
        danger_left = self.isDanger((hx - self.tileSize, hy))
        danger_right = self.isDanger((hx + self.tileSize, hy))

        # collect reward direction-> using grid "buckets"
        # Divides by tileSize to get discrete grid coordinates (e.g., "Food is 3 tiles right and 2 tiles down")
        dx_bucket = (self.reward.core.center[0] - hx) // self.tileSize
        dy_bucket = (self.reward.core.center[1] - hy) // self.tileSize

        return (heading_up, heading_down, heading_left, heading_right,
                danger_up, danger_down, danger_left, danger_right,
                dx_bucket, dy_bucket)

    def isDanger(self, pos):
        x, y = pos
        # wall check
        if x < 0 or x >= self.windowSize or y < 0 or y >= self.windowSize:
            return True
        # body check
        if pos in [bod.center for bod in self.snake.body]:
            return True
        return False

    def getRandomPos(self):
        return randrange(*self.range), randrange(*self.range)

    def rerun(self):
        self.snake.death()
        self.snake.head.center, self.reward.core.center = self.getRandomPos(), self.getRandomPos()
        self.score = 0
        return 1

    def render(self):
        self.screen.fill("black")
        for bod in self.snake.body:
            pygame.draw.rect(self.screen, 'green', bod)
        pygame.draw.rect(self.screen, 'red', self.reward.core)


class QLearningAgent:
    def __init__(self, env, epsilon=1, alpha=0.2, gamma=0.95):
        self.Q = {} #np.zeros((env.numTiles, env.numTiles, 4))
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.env = env

    def act(self, s):
        if np.random.rand() < self.epsilon:
            return np.random.randint(4)
        return int(np.argmax(self.Q.get(s, np.zeros(4))))

    def update(self, s, a, r, s2, done):
        if s not in self.Q:
            self.Q[s] = np.zeros(4)
        if s2 not in self.Q:
            self.Q[s2] = np.zeros(4)

        if done:
            target = r
        else:
            target = r + self.gamma * np.max(self.Q[s2])
        self.Q[s][a] += self.alpha * (target - self.Q[s][a])



# game loop vars
pygame.init()

run = True
clock = pygame.time.Clock()
time = 0
score_font = pygame.font.SysFont(None, 36)  # None = default font, 36 = size

#define environment
env = Environment(800, 100, 40)
agent = QLearningAgent(env)
state = env.getState()
clockSpeed = 10
episode = 0
episode_scores = []

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        clockSpeed+=30
    elif keys[pygame.K_DOWN]:
        if clockSpeed > 10:
            clockSpeed-=30
    elif keys[pygame.K_0]:
        clockSpeed=10

    action = agent.act(state)
    new_state, reward, done = env.step(action)
    agent.update(state, action, reward, new_state, done)
    state = new_state

    # episode logic
    if done:
        episode_scores.append(env.snake.length -1)
        episode+=1

        env.rerun()

        state = env.getState()
        agent.epsilon = max(0.05, agent.epsilon * 0.997) # decrease exploration over episodes

    env.render()
    # score & episode label
    score_text = score_font.render(f"Score: {env.snake.length - 1}", True, (255, 255, 255))
    episode_text = score_font.render(f"Episode: {episode}", True, (200, 255, 0))
    # in the render / score section
    if len(episode_scores) > 0:
        recent = episode_scores[-50:]
        avg = sum(recent) / len(recent)
    else:
        avg = 0.0
    average_text = score_font.render(f"Avg: {avg:.1f}", True, (0, 255, 200))
    env.screen.blit(score_text, (10, 10))  # top-left corner, 10px padding
    env.screen.blit(episode_text, (10,40))
    env.screen.blit(average_text, (10, 70))
    pygame.display.update()
    clock.tick(clockSpeed)
pygame.quit()