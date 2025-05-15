import random, sys, time, pygame
from pygame.locals import *

FPS = 30

WINDOWWIDTH = 360    
WINDOWHEIGHT = 640   

#                R    G    B
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
BRIGHTRED    = (255,   0,   0)
RED          = (155,   0,   0)
BRIGHTGREEN  = (  0, 255,   0)
GREEN        = (  0, 155,   0)
BRIGHTBLUE   = (  0,   0, 255)
BLUE         = (  0,   0, 155)
BRIGHTYELLOW = (255, 255,   0)
YELLOW       = (155, 155,   0)
DARKGRAY     = ( 40,  40,  40)
bgColor = BLACK

# Game constants
PLAYERSIZE = 40
ROCKSIZE = 30
BULLETSIZE = 5
PLAYERSPEED = 5
ROCKSPEED = 3
BULLETSPEED = 7
ENEMYSPEED = 2
ENEMY_SHOOT_RATE = 60  # Frames between enemy shots
SPEED_INCREASE_TIME = 20000  # Milliseconds before increasing speed
SPEED_INCREASE = 0.5

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYERSIZE, PLAYERSIZE))
        self.image.fill(BRIGHTBLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOWWIDTH // 2
        self.rect.bottom = WINDOWHEIGHT - 10
        self.lives = 3
        self.speed = PLAYERSPEED
        self.score = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < WINDOWWIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        return bullet

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ROCKSIZE, ROCKSIZE))
        self.image.fill(DARKGRAY)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOWWIDTH - ROCKSIZE)
        self.rect.y = -ROCKSIZE
        self.speed = ROCKSPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOWHEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLETSIZE, BULLETSIZE))
        self.image.fill(BRIGHTYELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BULLETSPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYERSIZE, PLAYERSIZE))
        self.image.fill(BRIGHTRED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOWWIDTH - PLAYERSIZE)
        self.rect.y = -PLAYERSIZE
        self.speed = ENEMYSPEED
        self.shoot_counter = 0

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOWHEIGHT:
            self.kill()
        
        self.shoot_counter += 1
        
    def shoot(self):
        if self.shoot_counter >= ENEMY_SHOOT_RATE:
            self.shoot_counter = 0
            return EnemyBullet(self.rect.centerx, self.rect.bottom)
        return None

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BULLETSIZE, BULLETSIZE))
        self.image.fill(BRIGHTRED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = BULLETSPEED // 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOWHEIGHT:
            self.kill()

def main():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Space Shooter')

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Create player
    player = Player()
    all_sprites.add(player)

    # Game variables
    score = 0
    game_over = False
    last_rock_spawn = 0
    rock_spawn_delay = 1000  # Milliseconds
    last_enemy_spawn = 0
    enemy_spawn_delay = 3000  # Milliseconds
    start_time = pygame.time.get_ticks()
    current_rock_speed = ROCKSPEED

    # Game loop
    while True:
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and not game_over:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    player_bullets.add(bullet)
                elif event.key == K_r and game_over:
                    return  # Restart game

        if not game_over:
            # Spawn rocks
            if current_time - last_rock_spawn > rock_spawn_delay:
                rock = Rock()
                rock.speed = current_rock_speed
                all_sprites.add(rock)
                rocks.add(rock)
                last_rock_spawn = current_time

            # Spawn enemies
            if current_time - last_enemy_spawn > enemy_spawn_delay:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
                last_enemy_spawn = current_time

            # Enemy shooting
            for enemy in enemies:
                bullet = enemy.shoot()
                if bullet:
                    all_sprites.add(bullet)
                    enemy_bullets.add(bullet)

            # Update
            all_sprites.update()

            # Increase difficulty over time
            if (current_time - start_time) % SPEED_INCREASE_TIME < 50:
                current_rock_speed += SPEED_INCREASE

            # Collision detection
            # Player bullets hitting rocks
            hits = pygame.sprite.groupcollide(rocks, player_bullets, True, True)
            for hit in hits:
                player.score += 10

            # Player bullets hitting enemies
            hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
            for hit in hits:
                player.score += 20

            # Rocks hitting player
            hits = pygame.sprite.spritecollide(player, rocks, True)
            if hits:
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True

            # Enemy bullets hitting player
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            if hits:
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True

        # Draw
        DISPLAYSURF.fill(bgColor)
        all_sprites.draw(DISPLAYSURF)
        
        # Draw score and lives
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {player.score}', True, WHITE)
        lives_text = font.render(f'Lives: {player.lives}', True, WHITE)
        DISPLAYSURF.blit(score_text, (10, 10))
        DISPLAYSURF.blit(lives_text, (10, 40))

        if game_over:
            game_over_text = font.render('Game Over! Press R to restart', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WINDOWWIDTH/2, WINDOWHEIGHT/2))
            DISPLAYSURF.blit(game_over_text, text_rect)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    while True:
        main()

