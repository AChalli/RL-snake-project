import pygame
from random import randrange
import numpy as np

class Snake:
    def __init__(self, tileSize, pos):
        self.tileSize= tileSize
        self.head = pygame.rect.Rect([0, 0, tileSize-2, tileSize-2]) # snake sprite = basic rectangle
        self.head.center = pos
        self.body = [self.head.copy()] #snake body
        self.direction = pygame.Vector2(0,0)
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
        #self.done = True
        self.screen = pygame.display.set_mode([windowSize] * 2)

    def step(self):
        print("no step")

    def getRandomPos(self):
        return randrange(*self.range), randrange(*self.range)

    def rerun(self):
        self.snake.death()
        self.snake.head.center, self.reward.core.center = self.getRandomPos(), self.getRandomPos()
        self.score = 0
        #self.done = True
        return 1

    def render(self):
        self.screen.fill("black")
        for bod in self.snake.body:
            pygame.draw.rect(self.screen, 'green', bod)
        pygame.draw.rect(self.screen, 'red', self.reward.core)


class QLearningAgent:
    def __init__(self, env, epsilon=0.1, alpha=0.5, gamma=1.0):
        self.Q = np.zeros((env.rows, env.cols, 4))
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def act(self, s):
        if np.random.rand() < self.epsilon:
            return np.random.randint(4)
        return int(np.argmax(self.Q[s]))

    def update(self, s, a, r, s2, done):
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
dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}
score_font = pygame.font.SysFont(None, 36)  # None = default font, 36 = size

#define environment
env = Environment(800, 100, 40)

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
    env.render()

    snake = env.snake
    reward = env.reward

    # controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and dirs[pygame.K_UP]:
        snake.direction.y = -env.tileSize
        snake.direction.x = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 0, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}
    elif keys[pygame.K_DOWN] and dirs[pygame.K_DOWN]:
        snake.direction.y = env.tileSize
        snake.direction.x = 0
        dirs = {pygame.K_UP: 0, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}
    elif keys[pygame.K_LEFT] and dirs[pygame.K_LEFT]:
        snake.direction.x = -env.tileSize
        snake.direction.y = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 0}
    elif keys[pygame.K_RIGHT] and dirs[pygame.K_RIGHT]:
        snake.direction.x = env.tileSize
        snake.direction.y = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}

    if env.snake.head.left < 0 or env.snake.head.right > env.windowSize or env.snake.head.top < 0 or env.snake.head.bottom > env.windowSize or env.snake.selfEat():
        env.rerun()

    # consume reward logic
    if snake.head.center == reward.core.center:
        snake.length += 1
        reward.core.center = reward.spawn(snake.body, env.getRandomPos)

    snake.move(snake.direction)

    # score label
    score_text = score_font.render(f"Score: {env.snake.length - 1}", True, (255, 255, 255))
    env.screen.blit(score_text, (10, 10))  # top-left corner, 10px padding
    pygame.display.update()
    clock.tick(10)
pygame.quit()