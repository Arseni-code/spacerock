import pygame 
from pygame.mixer import Sound
from pygame.math import Vector2
from pygame.transform import rotozoom
from pygame import color
import sys
import random
def load_sound(name):
    return Sound("sounds/"+name)
def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % w, y % h)
def get_random_position(surface):
    return Vector2(random.randrange(surface.get_width()),random.randrange(surface.get_height()))
def get_random_velocity(min_speed,max_speed):
    speed = random.randint(min_speed,max_speed)
    angle = random.randrange(0,360)
    return Vector2(speed,0).rotate(angle)
def print_text(surface,text,font,color = "tomato"):
    text_surface = font.render(text,False,color)
    rect = text_surface.get_rect()
    rect.center =  Vector2(surface.get_size())//2
    surface.blit(text_surface,rect)
class SpaceRock():
    MIN_ASTEROID_DISTANCE=250
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1300,700))
        pygame.display.set_caption("Windows заблокирована!!")
        self.background = pygame.image.load("sprites/space.png").convert_alpha()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None,64)
        self.message = ""
        self.bullets = []
        self.spaceship = SpaceShip((400,300),self.bullets.append)
        self.asteroids = []
        for _ in range(2):
            while True:
                position = get_random_position(self.screen)
                if (position.distance_to(self.spaceship.position) > self.MIN_ASTEROID_DISTANCE):
                    break
            self.asteroids.append(Asteroid(position,self.asteroids.append))
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for game_object in self.get_game_objects():
            game_object.draw(self.screen)
        if self.message:
            print_text(self.screen,self.message,self.font )
        pygame.display.flip()
        self.clock.tick(60)
    def game_logic(self):
        for game_object in self.get_game_objects():
            game_object.move(self.screen)
        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.colides_with(self.spaceship):
                    self.spaceship = None
                    self.message = "You died!"
                    break 
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if asteroid.colides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.rubalka_asteroidov()
                    break
        for bullet in self.bullets:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)
        if not self.asteroids and self.spaceship:
            self.message = "You win!"
    def main_loop(self):    
        while 1:
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    sys.exit()
                if i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_ESCAPE:
                        quit()
                    if  i.key == pygame.K_SPACE and self.spaceship:
                        self.spaceship.shoot()
            is_pressed = pygame.key.get_pressed()
            if self.spaceship:
                if is_pressed[pygame.K_RIGHT]:
                    self.spaceship.rotate(clockwise=True)
                if is_pressed[pygame.K_LEFT]:
                    self.spaceship.rotate(clockwise=False)
                if is_pressed[pygame.K_UP]:
                    self.spaceship.accelerate()
                if is_pressed[pygame.K_DOWN]:
                    self.spaceship.deaccelerate()
            self.game_logic()
            self.draw()
    def get_game_objects(self):
        game_objects = [*self.asteroids,*self.bullets]
        if self.spaceship:
            game_objects.append(self.spaceship)
        return game_objects
class GameObject:
    def __init__(self,position,sprite,velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width()/2
        self.velocity = Vector2(velocity)
    def draw(self,surface):
        surface.blit(self.sprite,self.position-Vector2(self.radius))
    def move(self,surface):
        self.position = wrap_position(self.position + self.velocity, surface)
    def colides_with(self, other_object):
        distance = self.position.distance_to(other_object.position)
        return distance < self.radius + other_object.radius
UP = Vector2(0,-1)
class SpaceShip(GameObject):
    MANEUVERABILITY = 5
    ACCELERATION = 0.25
    BULLET_SPEED = 3
    def __init__(self,position,bullet_callback):
        self.laser = load_sound("laser.wav")
        self.bullet_callback = bullet_callback
        self.direction = Vector2(UP)
        self.ship = pygame.image.load("sprites/spaceship.png").convert_alpha()
        super().__init__(position,self.ship,Vector2(0))   
    def shoot(self):
        bullet_velocity = self.direction*self.BULLET_SPEED+self.velocity
        bullet = Bullet(self.position,bullet_velocity)
        self.bullet_callback(bullet)
        self.laser.play()
    def rotate(self,clockwise=True):
        sign = 1 if clockwise else -1  
        angle = self.MANEUVERABILITY*sign
        self.direction.rotate_ip(angle)  
    def draw(self,surface):
        angle = self.direction.angle_to(UP)    
        rotated_surface = rotozoom(self.sprite,angle,1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())   
        blit_position = self.position - rotated_surface_size//2
        surface.blit(rotated_surface,blit_position)
    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION
    def deaccelerate(self):
        self.velocity -= self.direction * self.ACCELERATION
class Asteroid(GameObject):
    def __init__(self, position,asteroid_callback,size = 3):
        self.size = size
        self.asteroid_callback = asteroid_callback
        size_to_scale = {3:10,2:0.5,1:0.25}
        sprite = rotozoom(pygame.image.load("sprites/asteroid.png").convert_alpha(),0,size_to_scale[size])
        super().__init__(position,sprite,get_random_velocity(1,3))
    def rubalka_asteroidov(self):
        if self.size > 1:
            for _ in range(2):
                asteroid =  Asteroid(self.position,self.asteroid_callback,self.size-1)
                self.asteroid_callback(asteroid)
class Bullet(GameObject):
    def __init__(self,position,velocity):
        sprite = rotozoom(pygame.image.load("sprites/bullet.png").convert_alpha(),0,1)
        super().__init__(position, sprite  ,velocity)
    def move(self,surface):
        self.position = self.position + self.velocity
a = SpaceRock()
a.main_loop()