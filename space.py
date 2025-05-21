import random, sys, pygame
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

# Game states
WELCOME = 'welcome'
MENU = 'menu'
INSTRUCTIONS = 'instructions'
GAME = 'game'
PAUSE = 'pause'
GAME_OVER = 'game_over'

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

class Button:
    def __init__(self, x, y, width, height, text, color=BRIGHTBLUE, hover_color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def show_welcome_screen(surface):
    surface.fill(BLACK)
    draw_text(surface, "SPACE", 72, WINDOWWIDTH//2, WINDOWHEIGHT//4-72)
    draw_text(surface, "SHOOTER", 72, WINDOWWIDTH//2, WINDOWHEIGHT//4)
    draw_text(surface, "Press any key to continue", 36, WINDOWWIDTH//2, WINDOWHEIGHT * 3//4)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYUP:
                waiting = False

def show_menu(surface):
    buttons = {
        'start': Button(WINDOWWIDTH//4, WINDOWHEIGHT//2 - 60, WINDOWWIDTH//2, 50, "Start Game"),
        'instructions': Button(WINDOWWIDTH//4, WINDOWHEIGHT//2, WINDOWWIDTH//2, 50, "Instructions"),
        'exit': Button(WINDOWWIDTH//4, WINDOWHEIGHT//2 + 60, WINDOWWIDTH//2, 50, "Exit")
    }
    
    while True:
        surface.fill(BLACK)
        draw_text(surface, "SPACE", 72, WINDOWWIDTH//2, WINDOWHEIGHT//4-72)
        draw_text(surface, "SHOOTER", 72, WINDOWWIDTH//2, WINDOWHEIGHT//4)
        
        for button in buttons.values():
            button.draw(surface)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            
            for button_name, button in buttons.items():
                if button.handle_event(event):
                    if button_name == 'start':
                        return GAME
                    elif button_name == 'instructions':
                        return INSTRUCTIONS
                    elif button_name == 'exit':
                        terminate()

def show_instructions(surface):
    instructions = [
        "HOW TO PLAY:",
        "Move: Left/Right Arrow Keys",
        "Shoot: Space Bar",
        "Pause: P",
        "Avoid rocks and enemy ships",
        "Shoot enemies for points",
        "You have 3 lives",
        "",
        "Press ESC to return to menu"
    ]
    
    while True:
        surface.fill(BLACK)
        draw_text(surface, "INSTRUCTIONS", 60, WINDOWWIDTH//2, 80)
        
        for i, line in enumerate(instructions):
            draw_text(surface, line, 30, WINDOWWIDTH//2, 180 + i * 40)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    return MENU

def show_pause_screen(surface):

    
    s = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))
    surface.blit(s, (0, 0))
    draw_text(surface, "PAUSED", 72, WINDOWWIDTH//2, WINDOWHEIGHT//3)
    draw_text(surface, "Press P to continue", 36, WINDOWWIDTH//2, WINDOWHEIGHT//2)
    draw_text(surface, "Press ESC for menu", 36, WINDOWWIDTH//2, WINDOWHEIGHT * 2//3)
    pygame.display.flip()

def reset_game():
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # Create player
    player = Player()
    all_sprites.add(player)

    return all_sprites, rocks, player_bullets, enemy_bullets, enemies, player

def main():
    pygame.init()
    pygame.mixer.init()  # Initialize the sound mixer
    
    # Load sound effects
    shoot_sound = pygame.mixer.Sound('piu.wav')
    explosion_sound = pygame.mixer.Sound('bum.wav')
    
    # Load and play background music
    pygame.mixer.music.load('audio.wav')
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    pygame.mixer.music.set_volume(0.5)  # Set the volume to 50%
    
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Space Shooter')

    game_state = WELCOME
    
    while True:
        if game_state == WELCOME:
            show_welcome_screen(DISPLAYSURF)
            game_state = MENU
            continue
            
        elif game_state == MENU:
            game_state = show_menu(DISPLAYSURF)
            continue
            
        elif game_state == INSTRUCTIONS:
            game_state = show_instructions(DISPLAYSURF)
            continue

        # Initialize game components
        all_sprites, rocks, player_bullets, enemy_bullets, enemies, player = reset_game()

        # Game variables
        score = 0
        game_over = False
        paused = False
        last_rock_spawn = 0
        rock_spawn_delay = 1000
        last_enemy_spawn = 0
        enemy_spawn_delay = 3000
        start_time = pygame.time.get_ticks()
        current_rock_speed = ROCKSPEED

        # Game loop
        while game_state == GAME:
            current_time = pygame.time.get_ticks()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE and not game_over and not paused:
                        bullet = player.shoot()
                        all_sprites.add(bullet)
                        player_bullets.add(bullet)
                        shoot_sound.play()
                    elif event.key == K_r and game_over:
                        # Reset all game components
                        all_sprites, rocks, player_bullets, enemy_bullets, enemies, player = reset_game()
                        game_over = False
                        score = 0
                        player.score = 0
                        player.lives = 3
                        current_rock_speed = ROCKSPEED
                        # Restart background music
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.5)
                        continue  # Skip to the next frame with reset state
                    elif event.key == K_p and not game_over:
                        paused = not paused
                        if paused:
                            show_pause_screen(DISPLAYSURF)
                        
                    elif event.key == K_ESCAPE:
                        if paused or game_over:
                            game_state = MENU
                            break

            if paused:
                FPSCLOCK.tick(FPS)
                continue

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
                    explosion_sound.play()  # Play explosion sound

                # Player bullets hitting enemies
                hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
                for hit in hits:
                    player.score += 20
                    explosion_sound.play()  # Play explosion sound

                # Rocks hitting player
                hits = pygame.sprite.spritecollide(player, rocks, True)
                if hits:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True
                        pygame.mixer.music.stop()  # Stop background music when game is over

                # Enemy bullets hitting player
                hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
                if hits:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True
                        pygame.mixer.music.stop()  # Stop background music when game is over

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
                game_over_text = font.render('Game Over!', True, WHITE)
                text_rect = game_over_text.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2 - 30))
                DISPLAYSURF.blit(game_over_text, text_rect)
                
                # Use a smaller font size for instructions
                small_font = pygame.font.Font(None, 30)
                instruction_text = small_font.render('Press R to restart or ESC for menu', True, WHITE)
                text_rect = instruction_text.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2 + 20))
                DISPLAYSURF.blit(instruction_text, text_rect)

            pygame.display.flip()
            FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    while True:
        main()

