import pygame
from random import randint
import time

# Global constants
 
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (105, 105, 105)
CAVE = (43, 39, 31)
PLATFORM = (71, 74, 62)
P2 = (70, 94, 154)
P3 = (73, 27, 38)
 
# Screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
global screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)


screen.fill((0, 0, 0))
image = pygame.image.load("start_screen1.png")
screen.blit(image, [250, 250, 900, 850])
pygame.display.update()
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                waiting = False

pygame.display.set_caption("RETRIBUTION")

class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """
 
    # -- Methods
    def __init__(self, level_num):
        """ Constructor function """
 
        # Call the parent's constructor
        super().__init__()
 
        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0
 
        # List of sprites we can bump against
        self.level = None

        self.level_num = level_num
        

                # This holds all the images for the animated walk left/right
        # of our player
        self.walking_frames_l = []
        self.walking_frames_r = []
 
        # What direction is the player facing?
        self.direction = "R"
  
        # Load all the right facing images into a list
        image = pygame.image.load("hero_5.png")
        self.walking_frames_r.append(image)
        image = pygame.image.load("hero_6.png")
        self.walking_frames_r.append(image)
        image = pygame.image.load("hero_7.png")
        self.walking_frames_r.append(image)
        image = pygame.image.load("hero_8.png")
        self.walking_frames_r.append(image)
 
        # Load all the right facing images, then flip them
        # to face left.
        image = pygame.image.load("hero_8.png")
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = pygame.image.load("hero_5.png")
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = pygame.image.load("hero_6.png")
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
        image = pygame.image.load("hero_7.png")
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)
 
        # Set the image the player starts with
        self.image = self.walking_frames_r[0]
 
        # Set a reference to the image rect.
        self.rect = self.image.get_rect()
 
    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()
 
        # Move left/right
        self.rect.x += self.change_x
        pos = self.rect.x + self.level.world_shift
        if self.direction == "R":
            frame = (pos // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]
        else:
            frame = (pos // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        for bullet in self.level.bullet_list:
            if pygame.sprite.collide_rect(self, bullet) and bullet.heroBullet == False:
                self.level.game_over()
 
        # Move up/down
        self.rect.y += self.change_y
 
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            # Stop our vertical movement
            self.change_y = 0
 
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35
 
        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT:
            self.level.game_over()

    def jump(self):
        """ Called when user hits 'jump' button. """
 
        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
 
        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0: #or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10
 
    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6
        self.direction = "L"
 
    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6
        self.direction = "R"
 
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0
        
class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """
 
    def __init__(self, width, height, color):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()
 
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        
 
        self.rect = self.image.get_rect()
        self.outline = pygame.draw.rect(self.image, CAVE, self.rect, 2)

class MovingPlatform(Platform):
    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0
 
    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0
 
    player = None
 
    level = None
 
    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """
 
        # Move left/right
        self.rect.x += self.change_x
 
        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.
 
            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right
 
        # Move up/down
        self.rect.y += self.change_y
 
        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        for bullet in self.level.bullet_list:
            if pygame.sprite.collide_rect(self, bullet) and bullet.heroBullet == True:
                self.level.bullet_list.remove(bullet)
                self.level.active_sprite_list.remove(bullet)
 
        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1
 
        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1

class Enemies(pygame.sprite.Sprite):
    """ Platform the user can jump on """
 
    def __init__(self, width, height, img):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()
 
        self.walking_frames_l = []
        self.walking_frames_r = []

        self.direction = "R"
  
        # Load all the right facing images into a list
        image = pygame.image.load(img)
        self.walking_frames_r.append(image)

        #left facing
        image = pygame.image.load(img)
        image = pygame.transform.flip(image, True, False)
        self.walking_frames_l.append(image)

                # Set the image the player starts with
        self.image = self.walking_frames_r[0]
        
 
        self.rect = self.image.get_rect()

class MovingEnemies(Enemies):
    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0
 
    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0
    lives = 1
    shooter = False
    demon = False
    gameEnder = False
 
    player = None
 
    level = None
 
    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """
 
        # Move left/right
        self.rect.x += self.change_x
 
        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            self.level.game_over()

        for bullet in self.level.bullet_list:
            if pygame.sprite.collide_rect(self, bullet) and bullet.heroBullet == True:
                if self.lives < 2:
                    self.level.enemy_list.remove(self)
                    self.level.active_sprite_list.remove(self)
                    if self.gameEnder == True:
                        self.level.you_win()
                self.level.bullet_list.remove(bullet)
                self.level.active_sprite_list.remove(bullet)
                self.lives -= 1
                
        if (self.shooter == True):
            x = randint(0,45)

            if x == 1:
                bullet = Bullet(self, False, True, self.demon)
                self.level.active_sprite_list.add(bullet)
                self.level.bullet_list.add(bullet)

        # Move up/down
        self.rect.y += self.change_y
 
        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1
 
        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left: 
            self.change_x *= -1
            frame = (cur_pos // 30) % len(self.walking_frames_r)
            self.image = self.walking_frames_r[frame]

        if cur_pos > self.boundary_right:
            frame = (cur_pos // 30) % len(self.walking_frames_l)
            self.image = self.walking_frames_l[frame]
            self.change_x *= -1

class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """
    def __init__(self, player, heroBullet, leftBullet, demon):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.demon = demon
        self.player = player
        self.heroBullet = heroBullet
        self.leftBullet = leftBullet
 
        if self.heroBullet == True:
            self.image = pygame.image.load("iceball.png")
        elif self.demon == True:
            self.image = pygame.image.load("orb.png")
        else:
            self.image = pygame.image.load("fireball.png")
 
        self.rect = self.image.get_rect()
        if self.heroBullet == True:
            self.rect.x = self.player.rect.x + 30
            self.rect.y = self.player.rect.y + 8
        elif demon == True:
            self.rect.x = self.player.rect.x
            self.rect.y = self.player.rect.y
        else:
            self.rect.x = self.player.rect.x
            self.rect.y = self.player.rect.y
 
    def update(self):
        """ Move the bullet. """
        if self.heroBullet == True and self.leftBullet == False:
            self.rect.x += 10
        elif self.demon == True:
            self.rect.x -= 4
        else: 
            self.rect.x -= 6

        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()

class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """
 
    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        #self.enemy_list = pygame.sprite.Group()
        self.player = player
        self.bullet_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.active_sprite_list = pygame.sprite.Group()
 
        # How far this world has been scrolled left/right
        self.world_shift = 0

    def game_over(self):
        self.bullet_list.empty()
        self.enemy_list.empty()
        self.platform_list.empty()
        self.active_sprite_list.empty()
        screen.fill((0, 0, 0))
        image = pygame.image.load("Game_Over.png")
        screen.blit(image, [250, 200, 800, 650])
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
        main(self.player.level_num)

    def you_win(self):
        self.bullet_list.empty()
        self.enemy_list.empty()
        self.platform_list.empty()
        self.active_sprite_list.empty()
        screen.fill((0, 0, 0))
        image = pygame.image.load("youwin.png")
        screen.blit(image, [400, 150, 800, 650])
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
        main(0)

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        #self.enemy_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        self.active_sprite_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """
 
        # Draw the background
        screen.fill(CAVE)
        screen.blit(self.background,(self.world_shift // 3,0))
 
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        #self.enemy_list.draw(screen)
        self.enemy_list.draw(screen)
 
    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """
 
        # Keep track of the shift amount
        self.world_shift += shift_x
 
        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x
 
        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for bullet in self.bullet_list:
            bullet.rect.x += shift_x
 
class Level_01(Level):
    """ Definition for level 1. """
 
    def __init__(self, player):
        """ Create level 1. """
 
        # Call the parent constructor
        Level.__init__(self, player)
 
        self.background = pygame.image.load('stage.png')
        self.level_limit = -4000

        # Array with width, height, x, and y of platform
        # level = [[350, 600, PLATFORM,-250, 0], #1
        #          [210, 30, PLATFORM, 500, 500], #2
        #          [210, 30, PLATFORM, 800, 400], #3
        #          [210, 30, PLATFORM, 1000, 500], #4
        #          [210, 30, PLATFORM, 1120, 280], #5
        #          [210, 30, PLATFORM, 850, 150], #6
        #          [800, 600, PLATFORM, 0, 590], #7
        #          [210, 30, PLATFORM, 1900, 280], #8
        #          [210, 30, PLATFORM, 2400, 590], #9
        #          [210, 30, PLATFORM, 500, 100], #10
        #          [10000, 5, PLATFORM, 850, -5], #11
        #          [210, 30, PLATFORM, 120, 250], #12
        #          [210, 30, PLATFORM, 2200, 140], #13
        #          [1000, 30, PLATFORM, 4500, 400], #14
        #          #[4000, 5, PLATFORM, 600, 600], #bottom
        #            ]       
 
        # # Go through the array above and add platforms
        # for platform in level:
        #     block = Platform(platform[0], platform[1], platform[2])
        #     block.rect.x = platform[3]
        #     block.rect.y = platform[4]
        #     block.player = self.player
        #     self.platform_list.add(block)


        #[width, height, x, y, top, bottom, left, right, dx, dy]
        movLevel = [[60, 30, PLATFORM, 1350, 280, 0, 0, 1350, 1550, -1, 0],
                    [60, 30, PLATFORM, 2700, 450, 400, 590, 0, 0, 0, -1],
                    [60, 30, PLATFORM, 2900, 350, 300, 540, 0, 0 , 0, -2],
                    [60, 30, PLATFORM, 3100, 250, 200, 490, 0, 0, 0, -2],
                    [60, 30, PLATFORM, 3300, 150, 100, 370, 0, 0, 0, -2],
                    [60, 30, PLATFORM, 3500, 100, 0, 0, 3450, 3900, -2, 0],
                    [100, 30, PLATFORM, 3800, 450, 0, 0, 3800, 4300, -3, 0],
                    [350, 600, PLATFORM,-250, 0,0,0,0,0,0,0], #1
                    [210, 30, PLATFORM, 500, 500,0,0,0,0,0,0], #2
                    [210, 30, PLATFORM, 800, 400,0,0,0,0,0,0], #3
                    [210, 30, PLATFORM, 1000, 500,0,0,0,0,0,0], #4
                    [210, 30, PLATFORM, 1120, 280,0,0,0,0,0,0], #5
                    [210, 30, PLATFORM, 850, 150,0,0,0,0,0,0], #6
                    [800, 600, PLATFORM, 0, 590,0,0,0,0,0,0], #7
                    [210, 30, PLATFORM, 1900, 280,0,0,0,0,0,0], #8
                    [210, 30, PLATFORM, 2400, 590,0,0,0,0,0,0], #9
                    [210, 30, PLATFORM, 500, 100,0,0,0,0,0,0], #10
                    [10000, 5, PLATFORM, 850, -5,0,0,0,0,0,0], #11
                    [210, 30, PLATFORM, 120, 250,0,0,0,0,0,0], #12
                    [210, 30, PLATFORM, 2200, 140,0,0,0,0,0,0], #13
                    [1000, 30, PLATFORM, 4500, 400,0,0,0,0,0,0], #14
                    #[4000, 5, PLATFORM, 600, 600,0,0,0,0,0,0], #bottom
        ]
                 

                # Add a custom moving platform
        for platform in movLevel:
            block = MovingPlatform(platform[0], platform[1], platform[2])
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.boundary_top = platform[5]
            block.boundary_bottom = platform[6]
            block.boundary_left = platform[7]
            block.boundary_right = platform[8]
            block.change_x = platform[9]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        #[width, height, image, x, y, top, bottom, left, right, dx, dy, life]
        enLevel = [[60, 30, "stalactites.png", 1902, 310, 0,0,0,0,0,0,1000],
                   [60, 30, "stalactites.png", 2210, 170, 0,0,0,0,0,0,1000],
                   [60, 30, "stalactites.png", 550, 130, 0,0,0,0,0,0,1000],
                   [60, 30, "stalactites.png", 1150, 310, 0,0,0,0,0,0,1000],
                   [60, 30, "stalactites.png", 200, 280, 0,0,0,0,0,0, 1000],
                   [60, 30, "stalactites.png", 4502, 430, 0,0,0,0,0,0,1000],
                   [60, 30, "door2.png", 40, 530, 0, 0, 0, 0, 0, 0, 1000], #4
                   [60, 30, "Reaper_Attack_1.png", 1000, 450, 0, 0, 1000, 1170, -1, 0, 2], #4
                   [60, 30, "Demon_Attack_1.png", 500, 430, 0, 0, 500, 670, -3, 0, 1], #2
                   [60, 30, "Skeleton_Attack_1.png", 800, 350, 0, 0, 800, 970, -2, 0, 1], #3
                   [60, 30, "Demon_Attack_1.png", 1190, 210, 0, 0, 1120, 1290, -3, 0, 1], #5
                   [60, 30, "Ogre_Attack_1.png", 850, 83, 0, 0, 850, 1020, -1, 0, 3], #6
                   [60, 30, "Demon_Attack_1.png", 500, 40, 0, 0, 500, 670, -3, 0, 1], #10
                   [60, 30, "Ghost.png", 1900, 200, 0, 0, 1900, 2070, -2, 0, 1], #8
                   [60, 30, "Reaper_Attack_1.png", 120, 200, 0, 0, 120, 290, -1, 0, 2], #12
                   [60, 30, "Demon_Attack_1.png", 2200, 80, 0, 0, 2200, 2370, -3, 0, 1], #13
                   [60, 30, "Demon_Attack_1.png", 2500, 530, 0, 0, 2400, 2570, -3, 0, 1],
                   [60, 30, "Ghost.png", 2800, 300, 250, 540, 0, 0, 0, -2, 1], 
                   [60, 30, "Ghost.png", 3000, 200, 150, 490, 0, 0, 0, -2, 1], 
                   [60, 30, "Ghost.png", 3200, 100, 50, 440, 0, 0, 0, -2, 1],
                   [60, 30, "Ghost.png", 3400, 0, 0, 390, 0, 0, 0, -2, 1],
                   [60, 30, "Ghost.png", 2700, 50, 0, 0, 2700, 4200, -2, 0, 1],
                   [60, 30, "Demon_Attack_1.png", 3500, 380, 0, 0, 3300, 4400, -3, 0, 1],
                   [60, 30, "Demon_Attack_1.png", 3600, 275, 275, 500, 3600, 4000, -3, -1, 1],
                   [60, 30, "door2.png", 5000, 338, 0, 0, 0, 0, 0, 0, 1000],
                   [60, 30, "stalactites.png", 802, 430, 0, 0, 0, 0, 0, 0, 1000],
                   [60, 30, "stalactites.png", 890, 180, 0, 0, 0, 0, 0, 0, 1000], #4
                   [60, 30, "Demon_Lord.png", 4800, 180, 0, 0, 4500, 4800, -2, 0, 15],
        ]
                 
                # Add a custom moving platform
        for emily in enLevel:
            block = MovingEnemies(emily[0], emily[1], emily[2])
            block.rect.x = emily[3]
            block.rect.y = emily[4]
            block.boundary_top = emily[5]
            block.boundary_bottom = emily[6]
            block.boundary_left = emily[7]
            block.boundary_right = emily[8]
            block.change_x = emily[9]
            block.change_y = emily[10]
            block.lives = emily[11]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

class Level_02(Level):
    """ Definition for level 2. """
 
    def __init__(self, player):
        """ Create level 1. """
 
        # Call the parent constructor
        Level.__init__(self, player)
 
        self.background = pygame.image.load('stage2.png')
        self.level_limit = -3900
 
        # Array with type of platform, and x, y location of the platform.
        # level = [[400, 600, P2, -300, 0], #2
        #          [10, 400, P2, -50, -400],
        #          [600, 600, P2, 100, 590], #1
        #          [30, 30, P2, 100, 500],#3
        #          [30, 30, P2, 100, 300], #5
        #          [30, 30, P2, 100, 200],#6
        #          [30, 30, P2, 100, 100],#7
        #          [30, 30, P2, 100, 0],#8
        #          [50, 30, P2, 445, 500], #9
        #          [50, 30, P2, 550, 400],#10
        #          [50, 30, P2, 445, 300], #11
        #          [50, 30, P2, 550, 200], #12
        #          [210, 30, P2, 650, 200], #13
        #          [10000, 5, P2, 300, -5], #14
        #          [50, 30, P2, 2500, 500], #15
        #          [50, 30, P2, 2600, 400],#16
        #          [50, 30, P2, 2500, 300], #17
        #          [50, 30, P2, 2600, 200], #18
        #          #[10000, 5, P2, 300, 600],
        #          [1250, 30, P2, 2800, 200],
        #          [250,30, P2, 3900, 250],
        #          [250,30, P2, 4000, 300],
        #          [250, 30, P2, 4100, 350],
        #          [250, 30, P2, 4200, 400],
        #          [250, 30, P2, 4300, 450],
        #          [250, 30, P2, 4400, 500],
        #          [450, 30, P2, 4500, 550],
        #          [100, 30, P2, 30, 400],#4
        # ]
 
        # # Go through the array above and add platforms
        # for platform in level:
        #     block = Platform(platform[0], platform[1], platform[2])
        #     block.rect.x = platform[3]
        #     block.rect.y = platform[4]
        #     block.player = self.player
        #     self.platform_list.add(block)

    #[width, height,color,  x, y, top, bottom, left, right, dx, dy]
        movLevel = [[30, 30, P2, 900, 190, 100, 300, 0, 0, 0, -1 ],#1
                    [30, 30, P2, 1100, 400, 280, 500, 0, 0, 0, -1],#2
                    [30, 30, P2, 1300, 500, 400, 590, 0, 0, 0, -1],#3
                    [100, 30, P2, 1600, 550, 0, 0, 1525, 1875, -2, 0],#4
                    [100, 30, P2, 2000, 550, 0, 0, 1925, 2375, -1, 0],#5
                    [400, 600, P2, -300, 0,0,0,0,0,0,0], #2
                    [10, 400, P2, -50, -400,0,0,0,0,0,0],
                    [600, 600, P2, 100, 590,0,0,0,0,0,0], #1
                    [30, 30, P2, 100, 500,0,0,0,0,0,0],#3
                    [30, 30, P2, 100, 300,0,0,0,0,0,0], #5
                    [30, 30, P2, 100, 200,0,0,0,0,0,0],#6
                    [30, 30, P2, 100, 100,0,0,0,0,0,0],#7
                    [30, 30, P2, 100, 0,0,0,0,0,0,0],#8
                    [50, 30, P2, 445, 500,0,0,0,0,0,0], #9
                    [50, 30, P2, 550, 400,0,0,0,0,0,0],#10
                    [50, 30, P2, 445, 300,0,0,0,0,0,0], #11
                    [50, 30, P2, 550, 200,0,0,0,0,0,0], #12
                    [210, 30, P2, 650, 200,0,0,0,0,0,0], #13
                    [10000, 5, P2, 300, -5,0,0,0,0,0,0], #14
                    [50, 30, P2, 2500, 500,0,0,0,0,0,0], #15
                    [50, 30, P2, 2600, 400,0,0,0,0,0,0],#16
                    [50, 30, P2, 2500, 300,0,0,0,0,0,0], #17
                    [50, 30, P2, 2600, 200,0,0,0,0,0,0], #18
                    #[10000, 5, P2, 300, 600,0,0,0,0,0,0],
                    [1250, 30, P2, 2800, 200,0,0,0,0,0,0],
                    [250,30, P2, 3900, 250,0,0,0,0,0,0],
                    [250,30, P2, 4000, 300,0,0,0,0,0,0],
                    [250, 30, P2, 4100, 350,0,0,0,0,0,0],
                    [250, 30, P2, 4200, 400,0,0,0,0,0,0],
                    [250, 30, P2, 4300, 450,0,0,0,0,0,0],
                    [250, 30, P2, 4400, 500,0,0,0,0,0,0],
                    [450, 30, P2, 4500, 550,0,0,0,0,0,0],
                    [100, 30, P2, 30, 400,0,0,0,0,0,0,0],#4
                 ]

                # Add a custom moving platform
        for platform in movLevel:
            block = MovingPlatform(platform[0], platform[1], platform[2])
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.boundary_top = platform[5]
            block.boundary_bottom = platform[6]
            block.boundary_left = platform[7]
            block.boundary_right = platform[8]
            block.change_x = platform[9]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        #[width, height, image, x, y, top, bottom, left, right, dx, dy, lives]
        enLevel = [[60, 30, "door2.png", 40, 337, 0, 0, 0, 0, 0, 0, 1000],
                   [60, 30, "Ghost.png", 1000, 380, 0, 0, 1000, 1170, -1, 0, 1],
                   [60, 30, "Reaper_Attack_1.png", 430, 450, 0, 0, 425,445, -1, 0, 2],
                   [60, 30, "Ogre_Attack_1.png", 525, 334, 0, 0, 515, 555, -1, 0, 3],
                   [60, 30, "Reaper_Attack_1.png", 430, 250, 0, 0, 425, 445, -1, 0, 2],
                   [60, 30, "Ogre_Attack_1.png", 525, 134, 0, 0, 515, 555, -1, 0, 3],
                   [60, 30, "Skeleton_Attack_1.png", 2490, 450, 0,0,2485,2515,-1,0,1],
                   [60, 30, "Skeleton_Attack_1.png", 2500, 250, 0,0,2485,2515,-1,0,1],
                   [60, 30, "Demon_Attack_1.png", 2590, 330, 0,0,2580,2615,-1,0,1],
                   [60, 30, "Demon_Attack_1.png", 2600, 130, 0,0,2580,2615,-1,0,1],
                   [60, 30, "Ghost.png", 1800, 480, 0,0, 1520, 2380, -3, 0, 1],
                   [60, 30, "door2.png", 4875, 490, 0, 0, 0, 0, 0, 0, 1000],
        ]
                 
                # Add a custom moving platform
        for emily in enLevel:
            block = MovingEnemies(emily[0], emily[1], emily[2])
            block.rect.x = emily[3]
            block.rect.y = emily[4]
            block.boundary_top = emily[5]
            block.boundary_bottom = emily[6]
            block.boundary_left = emily[7]
            block.boundary_right = emily[8]
            block.change_x = emily[9]
            block.change_y = emily[10]
            block.lives = emily[11]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

        enLevel = [[60, 30, "wraithe.png", 3800, 150, 0,0, 0, 0, 0, 0, 25]]

        for emily in enLevel:
            block = MovingEnemies(emily[0], emily[1], emily[2])
            block.rect.x = emily[3]
            block.rect.y = emily[4]
            block.boundary_top = emily[5]
            block.boundary_bottom = emily[6]
            block.boundary_left = emily[7]
            block.boundary_right = emily[8]
            block.change_x = emily[9]
            block.change_y = emily[10]
            block.lives = emily[11]
            block.player = self.player
            block.level = self
            block.shooter = True
            block.demon = True
            self.enemy_list.add(block)

class Level_03(Level):
    """ Definition for level 3. """
 
    def __init__(self, player):
        """ Create level 1. """
 
        # Call the parent constructor
        Level.__init__(self, player)
 
        self.background = pygame.image.load('stage3.png')
        self.level_limit = -5000
 
        # Array with type of platform, and x, y location of the platform.
        movLevel = [[150, 600, P3,-50, 0,0,0,0,0,0,0],
                 [5000, 30, P3, 100, 590,0,0,0,0,0,0],
                 ]
 
        # Go through the array above and add platforms
        for platform in movLevel:
            block = MovingPlatform(platform[0], platform[1], platform[2])
            block.rect.x = platform[3]
            block.rect.y = platform[4]
            block.boundary_top = platform[5]
            block.boundary_bottom = platform[6]
            block.boundary_left = platform[7]
            block.boundary_right = platform[8]
            block.change_x = platform[9]
            block.change_y = platform[10]
            block.player = self.player
            block.level = self
            self.platform_list.add(block)

        #[width, height, image, x, y, top, bottom, left, right, dx, dy, lives]
        enLevel = [[60, 30, "door2.png", 40, 530, 0, 0, 0, 0, 0, 0, 1000],
                   [60, 30, "Hydra_Resting.png", 1000, 250, 0, 0, 1000, 4000, -13, 0, 10],
                   [60, 30, "Hydra_Resting.png", 1000, 250, 0, 0, 1000, 4250, -13, 0, 10],
                   [60, 30, "Hydra_Resting.png", 1000, 250, 0, 0, 1000, 4500, -13, 0, 10],
                   [60, 30, "sign.png", 1000, 0, 0, 0, 0, 0, 0, 0, 10],
        ]
                 
                # Add a custom moving platform
        for emily in enLevel:
            block = MovingEnemies(emily[0], emily[1], emily[2])
            block.rect.x = emily[3]
            block.rect.y = emily[4]
            block.boundary_top = emily[5]
            block.boundary_bottom = emily[6]
            block.boundary_left = emily[7]
            block.boundary_right = emily[8]
            block.change_x = emily[9]
            block.change_y = emily[10]
            block.lives = emily[11]
            block.player = self.player
            block.level = self
            self.enemy_list.add(block)

        enLevel = [[60, 30, "enemymage.png", 5040, 540, 0, 0, 0, 0, 0, 0, 50]
        ]
                
                # Add a custom moving platform
        for emily in enLevel:
            block = MovingEnemies(emily[0], emily[1], emily[2])
            block.rect.x = emily[3]
            block.rect.y = emily[4]
            block.boundary_top = emily[5]
            block.boundary_bottom = emily[6]
            block.boundary_left = emily[7]
            block.boundary_right = emily[8]
            block.change_x = emily[9]
            block.change_y = emily[10]
            block.lives = emily[11]
            block.player = self.player
            block.shooter = True
            block.level = self
            block.gameEnder = True
            self.enemy_list.add(block)
 
def main(start_level_num):
    """ Main Program """
    pygame.init()

    # Create the player
    player = Player(start_level_num)
 
    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))
    level_list.append(Level_03(player))

    # Set the current level
    current_level_no = start_level_num
    current_level = level_list[current_level_no]
 
    player.level = current_level
 
    player.rect.x = 105
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    current_level.active_sprite_list.add(player)

   # bullet_list = pygame.sprite.Group()
 
    # Loop until the user clicks the close button.
    done = False
 
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
 
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    bullet = Bullet(player, True, False, False)
                    current_level.active_sprite_list.add(bullet)
                    current_level.bullet_list.add(bullet)
                if event.key == pygame.K_a:
                    bullet = Bullet(player, True, True, False)
                    current_level.active_sprite_list.add(bullet)
                    current_level.bullet_list.add(bullet)
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
 
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
 
        # Update the player.
        current_level.active_sprite_list.update()
 
        # Update items in the level
        current_level.update()
 
        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)
 
        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)
 
        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift
        if current_position < current_level.level_limit:
            player.rect.x = 120
            if current_level_no < len(level_list)-1:
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level
                player.level_num = current_level_no
                current_level.active_sprite_list.add(player)
 
        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        current_level.active_sprite_list.draw(screen)
 
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(30)
 
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()
 
if __name__ == "__main__":
    main(0)