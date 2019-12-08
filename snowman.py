from gpiozero import LED
import random

WIDTH=800
HEIGHT=600

def draw():
    screen.fill((192,192,192))


# LEDS and their gpio numbers
# Index starts with 0, not 1 as on the PCB, nose is last (not PCB numbering)
leds = [LED(7),LED(8),LED(9),LED(22),LED(18),LED(17),LED(23),LED(24),LED(25)]
# body on left go top to bottom
# body on right go bottom to top 

# Dictionary for led names - refers to position in leds list
led_dict = {
    "leftbody1":0, "leftbody2":1, "leftbody3":2,
    "rightbody1":3, "rightbody2":4, "rightbody3":5,
    "righteye":6, "lefteye":7,
    "carrot":8}
    
# left body 1,2,4
# right body 8,16,32
# eyes 64,128
# nose 256

play_seq = [12,18,33,192,256,0,12,30,63,255,511,0,511,511,511,0,511,511,511,0]

snowman = Actor("snowman.png", center=(400,300))

sequence_number = 0
speed_count = 0

# Speed is opposite - more delay slower speed
delay = 16

# Game difficulty 0,1,2
game_difficulty = 0
# Game has own timers 
# Starts at -1 as increment before display
game_seq = -1
game_speed_count =0 
game_delay = 16
game_default_delay = 16
# Used to indicate next level
# Prevents double counting because of key press
game_next_level = False
# Set to True once game has gone past first LED 
# Once set to true missing last LED = game over
game_start = False
game_score = 0


state = "default"

def draw():
    screen.fill((192,192,192))
    snowman.draw()

def update():
    global sequence_number, speed_count, state, delay, game_difficulty


    if (keyboard.up):
        state = "on"
    if (keyboard.down):
        state = "off"
    if (keyboard.left):
        state = "flicker"
    if (keyboard.right):
        state = "sequence"
    if (keyboard.lctrl):
        game_difficulty = 0
        state = "game"
        game_setup()
    if (keyboard.lshift):
        game_difficulty = 1
        state = "game"
        game_setup()
    if (keyboard.lalt):
        game_difficulty = 2
        state = "game"
        game_setup()
    if (keyboard.RETURN):
        state = "default"
    if (keyboard.escape):
        state = "default"
    if (keyboard.h):
        state = "leftwink"
    if (keyboard.l):
        state = "rightwink"
    if (keyboard.x and delay < 100):
        delay += 1
    if (keyboard.space and delay > 0):
        delay -= 1
    if (state != "game" and state != "gameover" and keyboard.z):
        state = "carrot"
    if (keyboard.o):
        state = "play"
      
      
      
    if (state == "game"):
        if (game_difficulty == 2):
            game_hard()
        elif (game_difficulty == 1):
            game_medium()
        else:
            game_easy()
    elif (state == "gameover"):
        game_over()
        
    elif (state == "play"):
        speed_count += 1
        if speed_count >= delay:
            speed_count = 0
            light_mask(play_seq[sequence_number])
            sequence_number += 1
            if (sequence_number >= len(play_seq)):
                sequence_number = 0

    elif (state == "sequence"):
        speed_count += 1
        if speed_count >= delay:
            speed_count = 0
            light_sequence(sequence_number)
            sequence_number += 1
            if (sequence_number >= len(leds)):
                sequence_number = 0
    elif (state == "flicker"):
        # faster than normal speed so increment by greater amount
        speed_count += 8
        if speed_count >= delay:
            speed_count = 0
            sequence_number += 1
            if (sequence_number >= len(leds)):
                sequence_number = 0
                all_off()
            else:
                all_on()
    elif (state == "leftwink"):
        # if button released then go back to default
        if (not keyboard.h):
            state = "default"
            return
        light_sequence_off(led_dict["lefteye"])
    elif (state == "rightwink"):
        # if button released then go back to default
        if (not keyboard.l):
            state = "default"
            return
        light_sequence_off(led_dict["righteye"])
    elif (state == "carrot"):
        # if button released then go back to default
        if (not keyboard.z):
            state = "default"
            return
        light_sequence(led_dict["carrot"])
    elif (state == "on"):
        all_on()
    elif (state == "off"):
        all_off()
    else :
        all_on()
        
# Reset game variables
def game_setup():
    global game_seq, game_speed_count, game_delay, game_default_delay, game_start, game_score
    game_seq = -1
    game_speed_count =0 
    game_delay = game_default_delay
    game_start = False
    game_score = 0
        
def light_mask(value):
    for i in range(0,len(leds)):
        if (value & 1<<i) > 0:
            leds[i].on()
        else:
            leds[i].off()
        
def game_easy():
    global state, game_seq, game_speed_count, game_delay, game_default_delay, game_next_level, game_score
    game_speed_count += 1
    if game_speed_count >= game_delay:
        game_seq += 1
        if (game_seq >= len(leds)):
            game_seq = 0
        game_speed_count = 0
        game_next_level = False
        light_sequence(game_seq)
    if keyboard.z and game_next_level == False:
        # If on nose then win 
        if (game_seq == 8):
            # Correct - flash all leds
            all_on()
            game_score += 1
            # reset the speed count to make sure stays on long enough
            game_speed_count = 0
            #  speed up the game - next level
            game_delay -= 2
            # Set to next level so don't kep counting button press
            game_next_level = True
            game_seq = -1
        # Wrong end game
        else:
            state = "gameover"


def game_medium():
    global state, game_seq, game_speed_count, game_delay, game_default_delay, game_next_level, game_score
    game_speed_count += 1
    if game_speed_count >= game_delay:
        # Check to see if it should be game over (LED missed)
        if (game_seq == 8):
            state = "gameover"
        game_seq += 1
        game_start = True
        if (game_seq >= len(leds)):
            game_seq = 0
        game_speed_count = 0
        game_next_level = False
        light_sequence(game_seq)
    if keyboard.z and game_next_level == False:
        # If on nose then win 
        if (game_seq == 8):
            # Correct - flash all leds
            all_on()
            game_score += 1
            # reset the speed count to make sure stays on long enough
            game_speed_count = 0
            #  speed up the game - next level
            game_delay -= 3
            # Set to next level so don't keep counting button press
            game_next_level = True
            game_seq = -1
        # Wrong end game
        else:
            state = "gameover"
            

def game_hard():
    global state, game_seq, game_speed_count, game_delay, game_default_delay, game_next_level, game_score
    game_speed_count += 1
    if game_speed_count >= game_delay:
        # Check to see if it should be game over (LED missed)
        if (game_seq == 8):
            state = "gameover"
        # If last was a carrot then this should not be
        if (game_seq == -1):
            game_seq = random.randint(0,7)
        else:    
            # Range is larger than number of LEDs to increase probability of carrot
            game_seq = random.randint(0,10)
            if (game_seq > 8):
                game_seq = 8
        game_start = True
        game_speed_count = 0
        game_next_level = False
        light_sequence(game_seq)
    if keyboard.z and game_next_level == False:
        # If on nose then win 
        if (game_seq == 8):
            # Correct - flash all leds
            all_on()
            game_score += 1
            # reset the speed count to make sure stays on long enough
            game_speed_count = 0
            #  speed up the game - next level
            game_delay -= 3
            # Set to next level so don't keep counting button press
            game_next_level = True
            # Set LED to -1 so as not to count as a missed
            game_seq = -1
        # Wrong end game
        else:
            state = "gameover"

# Show score
def game_over():
    global state, game_seq, game_speed_count, game_delay, game_default_delay, game_next_level, game_score
    
    # Set minimum display time for score
    game_delay = 16
    
    for i in range (0,len(leds)):
        if (i < game_score):
            leds[i].on()
        else:
            leds[i].off()
    
    game_speed_count += 1
    if game_speed_count >= game_delay:
        state = "off"
        
    


# Turns off all lights except listed which is turned on
def light_sequence(light_on):
    for i in range (0,len(leds)):
        if i == light_on:
            leds[i].on()
        else:
            leds[i].off()
            
# Opposite of light_sequence - only one led off
def light_sequence_off(light_off):
    for i in range (0,len(leds)):
        if i == light_off:
            leds[i].off()
        else:
            leds[i].on()


def all_on():
    for i in range (0,len(leds)):
        leds[i].on()
        
def all_off():
    for i in range (0,len(leds)):
        leds[i].off()
