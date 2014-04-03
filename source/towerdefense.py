# TowerDefense game subclass
#
# Stores the items necessary for
# a game of tower defense. Handles
# tower, creep, map, menu, and
# money storage, user input,
# and changing the states of
# the game.
#
# 2014/3/21
# written by Michael Shawn Redmond

import pygame
from config import *
import game
import creep
import world
import tower
import menu

class TowerDefense(game.Game):
    def __init__(self, name, screen_width, screen_height):
        # setup data members and the screen
        game.Game.__init__(self, name, screen_width, screen_width)

        ### World setup ###
        world_pos_x = (screen_width - WORLD_DEFAULT_WIDTH)/2
        world_pos_y = MARGIN
        self.world = world.World((world_pos_x, world_pos_y), \
                                 WORLD_DEFAULT_WIDTH, WORLD_DEFAULT_HEIGHT, WORLD1)

        ### Menu setup ###
        self.menu = menu.Menu((world_pos_x, \
                               world_pos_y + WORLD_DEFAULT_HEIGHT + MARGIN), \
                              WORLD_DEFAULT_WIDTH*.5, \
                              screen_height - (world_pos_y + WORLD_DEFAULT_HEIGHT + 2*MARGIN), \
                              MENU_COLOR)
        self.towers_types = [tower.Tower, tower.GreenTower]
        for tt in self.towers_types:
            self.menu.add_purchaser(tt)
        
        self.towers = []#[tower.Tower((16,16), pygame.image.load(TOWER_BASIC_IMAGE), TOWER_BASIC_WIDTH, TOWER_BASIC_HEIGHT)]
        self.money = STARTING_MONEY
        #self.waves = [wave for wave in WAVES]
        self.wave = 0
        #self.creeps_types = [creep.Creep(CREEP_TYPES[i]) for i in range(CREEP_TYPE_COUNT)]
        self.creeps = []#[creep.Creep((0,0), pygame.image.load(CREEP_DEFAULT_IMAGE), CREEP_DEFAULT_WIDTH, CREEP_DEFAULT_HEIGHT)]
        self.state = TD_CLEAR
        self.sub_state = TD_IDLE
        self.purchaser = None
        self.selected = None

    def paint(self, surface):
        surface.fill(BACKGROUND_COLOR)
        self.world.paint(surface)
        self.menu.paint(surface)
        for creep in self.creeps:
            creep.paint(surface)
        for tower in self.towers:
            tower.paint(surface)

    def game_logic(self, keys, newkeys, mouse_pos, newclicks):
        # generate instructions
        instructions = []
        if self.sub_state == TD_FOLLOW:
            if self.world.is_inside(mouse_pos):
                cell_num = self.world.get_cell_at(mouse_pos)
                snap_loc = self.world.get_cell_top_left(cell_num)
            else:
                snap_loc = mouse_pos
            instructions.append((P_SNAP_LOC, snap_loc))
        # collect actions
        actions = []
        menu_actions = self.menu.game_logic(keys, newkeys, mouse_pos, newclicks, instructions)
        for action in menu_actions:
            if action is not None:
                actions.append(action)

        # handle actions
        for action in actions:
            if action[0] == P_FOLLOW:
                self.sub_state = TD_FOLLOW
                self.purchaser = action[1]
                pygame.mouse.set_visible(False)
            elif action[0] == P_PLACE:
                # verify ability to place tower
                cell_num = self.world.get_cell_at(mouse_pos)
                can_position = self.world.get_cell_top_left(cell_num)
                candidate = self.purchaser(can_position)
                if candidate.get_cost() <= self.money:
                    can_dimensions = candidate.get_dims() 
                    if self.world.can_build(can_position, can_dimensions):
                        collision = False
                        for t in self.towers:
                            if t.collide(candidate):
                                collision = True
                                break
                        if not collision:
                            print "Tower Placed"
                            self.towers.append(candidate)
                            self.money -= candidate.get_cost()
                self.sub_state = TD_IDLE
                self.purchaser = None
                pygame.mouse.set_visible(True)
