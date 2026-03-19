import pygame
from random import randrange

#setup
pygame.init()
window_scale = 800

#snake tile logic
tile_s = 40 #so there are 20 tiles on screen
range = (tile_s//2, window_scale - tile_s //2, tile_s) # range for reward coordinate generating
get_rand_pos = lambda: [randrange(*range), randrange(*range)] # function for generating random positon, defined as lambda function for ease
snake = pygame.rect.Rect([0,0, tile_s-2, tile_s-2]) # snake sprite = basic rectangle
snake.center = get_rand_pos()
length = 1
blocks = [snake.copy()]

#pygame loop
screen = pygame.display.set_mode([window_scale]*2)
clock = pygame.time.Clock()
run = True
dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}

#snake direction
S_dir = pygame.Vector2(0,0)

# tic tracking
time, tic_delay = 0, 100

#move snake function:
def mov_snake():
    global time, blocks
    curr_time = pygame.time.get_ticks()
    if curr_time - time > tic_delay:
        time = curr_time
        snake.move_ip(S_dir)
        blocks.append(snake.copy())
        blocks = blocks[-length:]


#reward generation
reward = snake.copy()
reward.center = get_rand_pos()

#spawn reward func
def spawn_reward():
    while True:
        pos = get_rand_pos()
        if pos not in [block.center for block in blocks]:
            return pos

#score font
score_font = pygame.font.SysFont(None, 36)  # None = default font, 36 = size

#game over logic
def rerun(segments, snake_obj):
    snake_obj.center, reward.center = get_rand_pos(), get_rand_pos()
    S_dir.update(0, 0)
    segments[:] = [snake_obj.copy()] # modify list in-place
    return 1

#gameplay loop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    screen.fill("black")

    #controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and dirs[pygame.K_UP]:
        S_dir.y = -tile_s
        S_dir.x = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 0, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}
    elif keys[pygame.K_DOWN] and dirs[pygame.K_DOWN]:
        S_dir.y = tile_s
        S_dir.x = 0
        dirs = {pygame.K_UP: 0, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 1}
    elif keys[pygame.K_LEFT] and dirs[pygame.K_LEFT]:
        S_dir.x = -tile_s
        S_dir.y = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 1, pygame.K_RIGHT: 0}
    elif keys[pygame.K_RIGHT] and dirs[pygame.K_RIGHT]:
        S_dir.x = tile_s
        S_dir.y = 0
        dirs = {pygame.K_UP: 1, pygame.K_DOWN: 1, pygame.K_LEFT: 0, pygame.K_RIGHT: 1}

    # define self-eating
    self_eat = pygame.Rect.collidelist(snake, blocks[:-1]) != -1

    # enforce borders
    if snake.left < 0 or snake.right > window_scale or snake.top < 0 or snake.bottom > window_scale or self_eat:
        length = rerun(blocks, snake)

        # consume reward logic
    if snake.center == reward.center:
        length += 1
        reward.center = spawn_reward()


    # draw snake:
    [pygame.draw.rect(screen, 'green', block) for block in blocks]

    #draw reward
    pygame.draw.rect(screen, 'red', reward)

    #move snake
    mov_snake()

    #score label
    score_text = score_font.render(f"Score: {length - 1}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))  # top-left corner, 10px padding

    pygame.display.flip()
    #rf rate
    clock.tick(144)
pygame.quit()