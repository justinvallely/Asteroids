# Modified take on the classic game of Asteroids
# To be run on www.codeskulptor.org or with SimpleGUICS2Pygame

try:
    import simplegui
except:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
high_score = 0
lives = 3
time = 0.5
started = False
rock_group = set()
missile_group = set()
explosion_group = set()
powerup_group = set()
powerups = 1
EXPLOSION_DIM = [9, 9]
run_once = True

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False, color = None):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated
        self.color = color

    def get_center(self):
        return self.center
    
    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated
    
    def get_color(self):
        return self.color
    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_brown.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("https://dl.dropboxusercontent.com/s/pyruyqxptkua20t/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot1.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")
asteroid_small_info = ImageInfo([45, 45], [90, 90], 15)
asteroid_small_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([50, 50], [100, 100], 17, 81, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/explosion.hasgraphics.png")

# power-up images - curtesty of darkcobalt86
powerup_red_info = ImageInfo([50, 43], [100, 86], 43, 240, False, 'red')
powerup_red_image = simplegui.load_image("https://dl.dropboxusercontent.com/s/6lzowg49l7wgggw/red.png")
powerup_green_info = ImageInfo([50, 43], [100, 86], 43, 240, False, 'green')
powerup_green_image = simplegui.load_image("https://dl.dropboxusercontent.com/s/huf1xrp8wn1fnbh/green.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")
powerup_red_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/s/4wy4s5omr3wxja1/smb_powerup.mp3")
powerup_green_sound = simplegui.load_sound("https://dl.dropboxusercontent.com/s/7ujhjfora20243w/smb_1-up.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust == True:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0] , self.image_center[1]], self.image_size, self.pos, self.image_size, self.angle)
            ship_thrust_sound.play()
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
            ship_thrust_sound.rewind()
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        
        # accelerate in the forward facing vector while thrusting
        if self.thrust == True:
            self.vel[0] += .1 * angle_to_vector(self.angle)[0]
            self.vel[1] += .1 * angle_to_vector(self.angle)[1]
        
        # wrap position around the endges of the frame when it goes off the edge
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        
        # slow down due to friction
        self.vel[0] *= (1 - 0.01)
        self.vel[1] *= (1 - 0.01)
    
    def turn_left(self):
        self.angle_vel = -.1
            
    def turn_right(self):
        self.angle_vel = .1
        
    def stop_turn(self):
        self.angle_vel = 0
        
    def thrusters(self, on):
        if on == True:
            self.thrust = True
        else:
            self.thrust = False
            
    def shoot(self):
        global missile_group, powerups
        
        # increase missile count for each power-up collected
        for i in range(powerups):
            if powerups > 5: powerups = 5 # limit the amount of powerups to prevent bog down
            if powerups > 1:
                # spread the missiles out evenly from the tip of the ship in a +/- 15deg (.25rad) range
                spread_angle = .5
                starting_angle = -spread_angle / 2
                shot_angle = i * (spread_angle / (powerups - 1)) + starting_angle
            else:
                shot_angle = 0
                
            missile_group.add(Sprite([my_ship.pos[0] + angle_to_vector(my_ship.angle)[0] * my_ship.radius, 
                                my_ship.pos[1] + angle_to_vector(my_ship.angle)[1] * my_ship.radius], 
                               [my_ship.vel[0] + 5 * angle_to_vector(my_ship.angle + shot_angle)[0], 
                                my_ship.vel[1] + 5 * angle_to_vector(my_ship.angle + shot_angle)[1]], 
                               0, 0, missile_image, missile_info, 1, missile_sound))

    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, scale = 1, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.color = info.get_color()
        self.age = 0
        self.scale = scale
        if sound:
            sound.rewind()
            sound.play()
        
    def draw(self, canvas):
        if self.animated:
            explosion_index = [self.age % EXPLOSION_DIM[0], (self.age // EXPLOSION_DIM[0]) % EXPLOSION_DIM[1]]
            canvas.draw_image(self.image, 
                              [self.image_center[0] + explosion_index[0] * self.image_size[0], 
                               self.image_center[1] + explosion_index[1] * self.image_size[1]], 
                              self.image_size, 
                              self.pos, 
                              [self.image_size[0] * self.scale, self.image_size[1] * self.scale], 
                              self.angle)
        else:
            canvas.draw_image(self.image, 
                              self.image_center, 
                              self.image_size, 
                              self.pos, 
                              [self.image_size[0] * self.scale, self.image_size[1] * self.scale], 
                              self.angle)
    
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        
        # wrap position around the endges of the frame when it goes off the edge
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] = self.pos[1] % HEIGHT
        
        self.age += 1
        if self.age >= self.lifespan:
            # remove sprite
            return True
        else:
            # keep sprite
            return False
        
    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) <= self.radius + other_object.get_radius():
            return True
        else:
            return False
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def get_center(self):
        return self.image_center
    
    def get_size(self):
        return self.image_size

def draw(canvas):
    global time, lives, score, high_score, started, rock_group, powerup_group, powerups
    
    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    
    # draw and update sprite groups
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    process_sprite_group(powerup_group, canvas)
    
    # display lives
    canvas.draw_text("Lives: " + str(lives), [30, 30], 24, "Blue", "sans-serif")
    # draw ship icons for number of lives
    scoot = 0
    for i in range(lives):
        canvas.draw_image(ship_image, ship_info.get_center(), ship_info.get_size(), [30 + scoot, 60], [50, 50], 3*math.pi/2)
        scoot += 50
    # display score
    canvas.draw_text("Score: " + str(score), [WIDTH - 170, 30], 24, "Blue", "sans-serif")
    canvas.draw_text("High Score: " + str(high_score), [WIDTH - 170, 60], 24, "Blue", "sans-serif")
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        
    # determine if the ship hit any of the rocks
    if group_collide(rock_group, my_ship):
        lives -= 1
        
    # game over
    if lives <= 0:
        started = False
        soundtrack.pause()
        powerups = 1
        # erase all sprites
        rock_group = set()
        powerup_group = set()
        #record the high score
        if score > high_score:
            high_score = score
    
    # increment score when a missle hits a rock
    if group_group_collide(rock_group, missile_group) >= 1:
        score += 1
    
    # spawn a red power-up every 10 points
    if score > 0 and score % 10 == 0:
        global run_once
        # ensure powerup_spawner only gets called once
        while run_once == True:
            powerup_spawner(random.choice(['red', 'green']))
            run_once = False
    else:
        run_once = True
        
    # determine if the ship hits any power-ups
    group_collide(powerup_group, my_ship)
    
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    
    if len(rock_group) < 10 and started:
        # assign random values to sprite variables
        pos = [random.random() * WIDTH, random.random() * HEIGHT]
        vel = [random.randint(1, 18)/6.0 * random.choice([-1,1]), random.randint(1, 18)/6.0 * random.choice([-1,1])]
        ang = 0
        ang_vel = random.random()/6.0 * random.choice([-1,1])
        
        # increase velocity as score goes up
        for i in range(len(vel)):
            vel[i] *= 1 + (score / 30.0)
            
        # create a new rock with the above parameters
        new_rock = Sprite(pos, vel, ang, ang_vel, asteroid_image, asteroid_info, 1)
        
        # ignore a rock spawn event if the spawned rock is too close to the ship
        if not new_rock.collide(my_ship):
            rock_group.add(new_rock)
    
    return rock_group

def split_rock(rock, missile):
    global rock_group
    # spawn two new rocks if the rock that is destroyed is greater than a certain size
    
    radius = rock.get_radius()
    asteroid_radius = asteroid_info.get_radius()
    
    if radius >= asteroid_radius:
        theta = math.atan2(missile.vel[1], missile.vel[0])	# vector to angle
        angle_mod = math.pi * 0.125							# modify new trajectory
        comp_mod = 2 + math.log(score + 1, 10)				# modify new velocity
        
        new_direction = [angle_to_vector(theta + i) for i in (-angle_mod, +angle_mod)]
        
        for d in new_direction:
            rock_group.add(Sprite(rock.get_position(), 
                                  [d[0]*comp_mod, d[1]*comp_mod], 
                                  rock.angle, 
                                  rock.angle_vel, 
                                  asteroid_small_image, 
                                  asteroid_small_info, 
                                  0.5))
        
        return True		# a rock was split
    return False		# no rock was split

# handler that spawns a power-up    
def powerup_spawner(color):
    global powerup_group
    
    if color == 'red':
        image = powerup_red_image
        info = powerup_red_info
    elif color == 'green':
        image = powerup_green_image
        info = powerup_green_info
        
    # assign random position value to sprite variables
    pos = [random.random() * WIDTH, random.random() * HEIGHT]
    powerup_group.add(Sprite(pos, [0,0], 0, 0, image, info, 1))
    return powerup_group

# take a set and a canvas and call the update and draw methods for each sprite in the group
def process_sprite_group(sprite_set, canvas):
    for sprite in set(sprite_set):
        sprite.draw(canvas)
        if sprite.update():
            sprite_set.remove(sprite)
            
# check for collisions between other_object and elements of the group
def group_collide(group, other_object):
    global powerups, lives
    for item in set(group):
        if item.collide(other_object):
            # remove item from group
            group.remove(item)
            if item.color == None:
                if split_rock(other_object, item): scale = 1
                else: scale = 0.5
                    
                explosion_group.add(Sprite(other_object.pos, 
                                           other_object.vel, 
                                           other_object.angle, 
                                           0, 
                                           explosion_image, 
                                           explosion_info, 
                                           scale, 
                                           explosion_sound))
            elif item.color == 'red':
                powerup_red_sound.rewind()
                powerup_red_sound.play()
                powerups += 1
            elif item.color == 'green':
                powerup_green_sound.rewind()
                powerup_green_sound.play()
                lives += 1
            return True
        
# check for collisions between groups of rocks and groups of missiles
def group_group_collide(group, other_group):
    count = 0
    for item in set(group):
        if group_collide(other_group, item):
            count += 1
            group.remove(item)
            return count
        
# key down handler
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.turn_left()
        
    if key == simplegui.KEY_MAP['right']:
        my_ship.turn_right()
        
    if key == simplegui.KEY_MAP['up']:
        my_ship.thrusters(True)
        
    if key == simplegui.KEY_MAP['space']:
        my_ship.shoot()

# key up handler
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.stop_turn()
        
    if key == simplegui.KEY_MAP['right']:
        my_ship.stop_turn()
        
    if key == simplegui.KEY_MAP['up']:
        my_ship.thrusters(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()
        
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and one sprite
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
