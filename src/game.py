import pygame
import player
import utils
import settings
from asteroid import Asteroid
import random
import math

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, 
                                               settings.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = player.Player(400, 300, self.screen)
        self.asteroids = []
        self.bullets = []
        self.current_wave = 1
        self.asteroids_in_wave = 3
        self.time_between_waves = 5000
        self.last_wave_time = pygame.time.get_ticks()

    def spawn_asteroids(self):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x = random.uniform(0, settings.SCREEN_WIDTH)
            y = -50
            angle = random.uniform(-math.pi / 2, math.pi / 2)
        elif edge == 'bottom':
            x = random.uniform(0, settings.SCREEN_WIDTH)
            y = settings.SCREEN_HEIGHT + 50
            angle = random.uniform(math.pi / 2, 3 * math.pi / 2)
        elif edge == 'left':
            x = -50
            y = random.uniform(0, settings.SCREEN_HEIGHT)
            angle = random.uniform(0, math.pi)
        elif edge == 'right':
            x = settings.SCREEN_WIDTH + 50
            y = random.uniform(0, settings.SCREEN_HEIGHT)
            angle = random.uniform(-math.pi, 0)

        size = random.choice(['large', 'medium', 'small'])
        speed = random.uniform(1, 3)

        new_asteroid = Asteroid(x, y, size, self.screen, angle, speed)
        self.asteroids.append(new_asteroid)

    def spawn_wave(self):
        for _ in range(self.asteroids_in_wave):
            self.spawn_asteroids()
        self.current_wave += 1
        self.asteroids_in_wave = min(5 + self.current_wave, 15)
        self.time_between_waves = max(5000, self.time_between_waves - 100)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.shoot(self.bullets)
                    
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.rotate_left()
        if keys[pygame.K_RIGHT]:
            self.player.rotate_right()
        if keys[pygame.K_UP]:
            self.player.accelerate()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(120)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_wave_time > self.time_between_waves:
            self.spawn_wave()
            self.last_wave_time = current_time

        self.player.update()
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.is_alive():
                self.bullets.remove(bullet)
            else:
                for asteroid in self.asteroids[:]:  
                    if utils.check_collision(bullet, asteroid):
                        self.handle_asteroid_destruction(asteroid)
                        bullet.alive = False
                        break
        
        for asteroid in self.asteroids:
            asteroid.update()

        self.asteroids = [a for a in self.asteroids if 
                          not getattr(a, 'marked_for_removal', False)]

    def handle_asteroid_destruction(self, asteroid):
        if asteroid.size == 'large':
            new_sizes = ['medium', 'medium']
        elif asteroid.size == 'medium':
            new_sizes = ['small', 'small', 'small']
        else:
            new_sizes = []
        
        angle_spread = math.pi / 6

        for size in new_sizes:
            new_angle_variation = random.uniform(-angle_spread, angle_spread)
            new_angle = asteroid.angle + new_angle_variation

            new_speed = asteroid.speed + random.uniform(0.5, 1.5)

            new_asteroid = Asteroid(asteroid.x, asteroid.y, size, self.screen, 
                                    new_angle, new_speed)
            self.asteroids.append(new_asteroid)

        self.asteroids.remove(asteroid)

    def draw(self):
        self.screen.fill(settings.BLACK)
        self.player.draw()
        for bullet in self.bullets:
            bullet.draw()
        for asteroid in self.asteroids:
            asteroid.draw()
        self.draw_ui()
        pygame.display.flip()


    def draw_ui(self):
        ammo_count = 5 - len([b for b in self.bullets if b.is_alive()])
        ammo_text = f"Ammo: {ammo_count}"
        font = pygame.font.SysFont(None, 36)
        text_surf = font.render(ammo_text, True, settings.WHITE)
        self.screen.blit(text_surf, (10, self.screen.get_height() - 40))