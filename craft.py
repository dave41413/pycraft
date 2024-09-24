from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
from time import time

app = Ursina()

# Configure the window size and remove borderless fullscreen
window.fullscreen = False
window.borderless = False
window.size = (640, 480)
window.color = color.blue # Blue sky color

# List to store mined blocks and inventory system
mined_blocks = []
inventory = {}

# FPS counter setup
fps_counter = Text(text='FPS:', position=(-0.4, 0.4), origin=(0, 0), scale=2, color=color.black)

# Define a simple block entity
class Block(Button):
    def __init__(self, position=(0, 0, 0), block_type='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture='white_cube',
            color=color.white,
            highlight_color=color.lime
        )
        self.block_type = block_type
        self.mining = False  # Initialize mining attribute

        # Set the color and type for each block
        if block_type == 'grass':
            self.color = color.green
        elif block_type == 'dirt':
            self.color = color.brown
        elif block_type == 'stone':
            self.color = color.gray
        elif block_type == 'wood':
            self.color = color.brown  # Brown for wood
        elif block_type == 'leaves':
            self.color = color.green  # Green for leaves

    # Mining mechanism with cooldown
    def input(self, key):
        if self.hovered and key == 'left mouse down':
            if not self.mining:  # Only mine if not already mining
                self.mining = True
                invoke(self.mine_block, delay=0.05)  # Cooldown for mining

    def mine_block(self):
        mined_blocks.append(self.position)  # Track mined blocks
        # Add block to inventory
        if self.block_type not in inventory:
            inventory[self.block_type] = 1
        else:
            inventory[self.block_type] += 1
        destroy(self)
        update_viewmodel(self.block_type)  # Update the hand viewmodel
        self.mining = False  # Reset mining flag

# Function to create terrain with layers (grass, dirt, stone)
def create_terrain():
    for z in range(20):  # Expand the land size
        for x in range(20):
            grass_block = Block(position=(x, 0, z), block_type='grass')
            dirt_block = Block(position=(x, -1, z), block_type='dirt')
            stone_block = Block(position=(x, -2, z), block_type='stone')

# Create trees at random positions
def create_trees():
    for i in range(5):  # Create 5 random trees
        x = random.randint(0, 19)
        z = random.randint(0, 19)
        Block(position=(x, 1, z), block_type='wood')  # Tree trunk
        Block(position=(x, 2, z), block_type='wood')  # Tree trunk 2
        Block(position=(x, 3, z), block_type='wood')  # Tree trunk 3
        Block(position=(x, 4, z), block_type='leaves')  # Leaves

# Add a void teleportation feature when player reaches the void
def check_void():
    if player.y < -5:  # If the player falls into the void
        # Find the nearest surface that is not mined
        for x in range(20):
            for z in range(20):
                if (x, 0, z) not in mined_blocks:  # Check for the first unmined block
                    player.position = (x, 2, z)
                    break

# Simple wandering NPC
class NPC(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=1.5,
            position=(random.randint(0, 19), 1, random.randint(0, 19))
        )

    def update(self):
        self.position += (random.uniform(-0.7, 0.7), 0, random.uniform(-0.5, 0.5))
        check_npc_void(self)

# Check if NPC falls into void and teleport back
def check_npc_void(npc):
    if npc.y < -5:
        npc.position = (random.randint(0, 19), 1, random.randint(0, 19))

# Update the hand/viewmodel based on the item collected
def update_viewmodel(item_type):
    hand.color = color.white  # Reset hand color for empty
    if item_type == 'grass':
        hand.color = color.green
    elif item_type == 'dirt':
        hand.color = color.brown
    elif item_type == 'stone':
        hand.color = color.gray
    elif item_type == 'wood':
        hand.color = color.rgb(139, 69, 19)
    elif item_type == 'leaves':
        hand.color = color.rgb(34, 139, 34)

# Create a simple hand/viewmodel
class Hand(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model='cube',
            scale=(0.2, 0.2, 0.2),
            color=color.white,
            position=Vec2(0.6, -0.5)
        )

# World border logic
def check_world_border():
    if player.x < 0 or player.x > 19 or player.z < 0 or player.z > 19:
        player.x = max(0, min(player.x, 19))
        player.z = max(0, min(player.z, 19))

# Optimizing performance by tracking frame time
last_time = time()
frame_count = 0

# Update the FPS counter
def update_fps_counter():
    global last_time, frame_count
    frame_count += 1
    current_time = time()
    elapsed_time = current_time - last_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        fps_counter.text = f'FPS: {int(fps)}'
        frame_count = 0
        last_time = current_time

# Setup player, terrain, trees, NPC, and hand
create_terrain()
create_trees()
npc = NPC()  # Create a wandering NPC
player = FirstPersonController()
hand = Hand()  # Create the player's hand viewmodel

# Game update logic
def update():
    check_void()  # Check if player falls into the void
    check_world_border()  # Check if player is outside world borders
    update_fps_counter()  # Update the FPS counter

app.run()
