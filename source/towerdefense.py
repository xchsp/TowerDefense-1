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
import button
import display

class TowerDefense(game.Game):
    def __init__(self, name, screen_width, screen_height):
        # setup data members and the screen
        game.Game.__init__(self, name, screen_width, screen_height)

        ### World setup ###
        self.world = world.World((WORLD_X, WORLD_Y), WORLD_WIDTH, WORLD_HEIGHT, WORLD1)

        ###  Purchaser menu setup ###
        self.menu = menu.Menu((MENU_P_X, MENU_P_Y), MENU_P_WIDTH, MENU_P_HEIGHT, MENU_P_BG_COLOR, MENU_P_O_COLOR)
        self.towers_types = [tower.Tower, tower.GreenTower]
        for tt in self.towers_types:
            self.menu.add_purchaser(tt)

        ### Button menu setup ###
        self.b_menu = menu.Menu((MENU_B_X, MENU_B_Y), MENU_B_WIDTH, MENU_B_HEIGHT, MENU_B_BG_COLOR, MENU_B_O_COLOR)
        
        self.buttons = [button.NewWave]                      
        for btn in self.buttons:
            self.b_menu.add_button(btn)

        ### Display setup ###
        self.display = display.Display((DISPLAY_X, DISPLAY_Y), DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_BG_COLOR, DISPLAY_O_COLOR)
        
        self.towers = []
        self.money = STARTING_MONEY
        self.wave = 0
        self.creep_types = [creep.Creep]
        self.creeps = set()
        self.state = TD_CLEAR
        self.sub_state = TD_IDLE
        self.purchaser = None
        self.selected = None

        ### setup font ###
        self.font = pygame.font.SysFont(FONT, FONT_SIZE)
        self.font_color = FONT_COLOR

        ### setup location for money ###
        self.money_x = MONEY_X
        self.money_y = MONEY_Y

    def paint(self, surface):
        surface.fill(BG_COLOR)
        self.world.paint(surface)
        self.menu.paint(surface)
        self.b_menu.paint(surface)
        self.display.paint(surface)

        ### show money ###
        currency = "Current money: $%s" %(self.money)
        temp_surface = self.font.render(currency, 1, self.font_color)
        surface.blit(temp_surface, (self.money_x, self.money_y))
        
        for creep in self.creeps:
            creep.paint(surface)
        if self.sub_state == TD_SHOW:
            if self.selected is not None:
                self.selected.paint_range(surface)
        elif self.sub_state == TD_FOLLOW:
            if self.purchaser is not None:
                if not self.world.can_build(self.purchaser.get_position(), self.purchaser.get_dims()):
                    self.purchaser.bad_pos()
                    self.purchaser.paint_range(surface)
                else:
                    self.purchaser.good_pos()
                    self.purchaser.paint_range(surface)
                self.purchaser.paint(surface)
        for tower in self.towers:
            tower.paint(surface)
        for tower in self.towers:
            tower.paint_bullets(surface)
            
    def begin_wave(self):
        self.wave += 1
        if self.wave > len(WAVES)-1:
            return
        for i in range(CREEP_COUNT):
            for j in range(WAVES[self.wave][i]):
                c = self.creep_types[i]((0, 0))
                x, y = self.world.get_start()
                c.set_position((-(j+1)*(c.get_width() + CREEP_GAP), y))
                c.set_destination(self.world.next_waypoint(0))
                self.creeps.add(c)

    def calc_snap_loc(self, pos):
        if self.world.is_inside(pos):
                cell_num = self.world.get_cell_at(pos)
                snap_loc = self.world.get_cell_top_left(cell_num)
        else:
                snap_loc = pos
        return snap_loc

    def display_item(self, item):
        # clear display
        self.display.deactivate()
        # setup display
        self.display.set_image(item.get_image(), item.get_width(), item.get_height())
        self.display.add_data(item.get_info())
        self.display.activate()

    def game_logic(self, keys, newkeys, mouse_pos, newclicks):
        dead = set()
        for creep in self.creeps:
            if not creep.has_destination():
                dest = self.world.next_waypoint(creep.get_visited())
                if dest is not None:
                    creep.set_destination(self.world.next_waypoint(creep.get_visited()))
                else:
                    dest = self.world.next_waypoint(creep.get_visited())
                if dest is not None:
                    creep.set_destination(self.world.next_waypoint(creep.get_visited()))
                else:
                    creep.health = 0
        self.creeps -= dead
        if self.sub_state == TD_FOLLOW:
            # if we are placing a tower
            # snap its location to the
            # cells of the world
            self.purchaser.set_position(self.calc_snap_loc(mouse_pos))
        
        # collect actions for menu
        actions = []
        menu_actions = self.menu.game_logic(keys, newkeys, mouse_pos, newclicks)
        for action in menu_actions:
            if action is not None:
                actions.append(action)

        b_menu_actions = self.b_menu.game_logic(keys, newkeys, mouse_pos, newclicks)
        for action in b_menu_actions:
            if action is not None:
                actions.append(action)
        
        # collect actions for towers
        for tower in self.towers:
            tower_actions = tower.game_logic(keys, newkeys, mouse_pos, newclicks, self.creeps)
            for action in tower_actions:
                if action is not None:
                    actions.append(action)

        for creep in self.creeps:
            creep_actions = creep.game_logic(keys, newkeys, mouse_pos, newclicks)
            for action in creep_actions:
                if action is not None:
                    actions.append(action)
        
        # handle actions
        for action in actions:
            if action[0] == P_FOLLOW:
                # if we clicked on a menu item
                # to start placing a tower
                # keep track of that tower
                if self.sub_state == TD_SHOW:
                    self.selected.deactivate()
                    self.display.deactivate() # possible refactoring 2
                    self.selected = None
                self.sub_state = TD_FOLLOW
                self.purchaser = action[1]
                self.purchaser.activate()
                pygame.mouse.set_visible(False)
                self.display_item(self.purchaser)
            elif action[0] == P_PLACE:
                if self.purchaser is None:
                    break
                # verify ability to place tower
                f_pos = self.calc_snap_loc(mouse_pos)
                f_dims = self.purchaser.get_dims()
                cell_num = self.world.get_cell_at(f_pos)
                placed = False
                if self.world.has_cell(cell_num):
                    if self.purchaser.get_cost() <= self.money:
                        if self.world.can_build(f_pos, f_dims):
                            self.world.occupy_area(f_pos, f_dims)
                            self.purchaser.activate()
                            self.towers.append(self.purchaser)
                            self.money -= self.purchaser.get_cost()
                            self.selected = self.purchaser
                            self.sub_state = TD_SHOW # show new tower
                            self.display_item(self.selected)
                            placed = True
                if not placed:
                    self.sub_state = TD_IDLE
                self.purchaser = None
                pygame.mouse.set_visible(True)
            elif action[0] == T_SELECTED:
                # if we clicked on a tower
                # stop showing the range
                # of the previously selected
                # tower and show this tower's
                # range
                if self.sub_state == TD_FOLLOW:
                    self.purchaser = None
                if self.selected is not None:
                    self.selected.deactivate()
                    self.display.deactivate() # possible refactoring 2
                    self.selected = None
                self.selected = action[1]
                self.selected.activate()
                self.sub_state = TD_SHOW # show new tower

                self.display_item(self.selected)
            elif action[0] == C_DEAD:
                self.creeps.remove(action[1])
            elif action[0] == B_KILL:
                self.money += action[1]
            elif action[0] == BUTTON_NEW_WAVE_MSG:
                self.begin_wave()
        if 1 in newclicks: # left mouse click
            # if we clicked on an empty cell
            # stop showing the previously
            # selected tower's range
            cell_num = self.world.get_cell_at(mouse_pos)
            if self.sub_state == TD_SHOW:
                if self.world.has_cell(cell_num) and not self.world.is_occupied(cell_num):
                    self.selected.deactivate()
                    self.selected = None
                    self.sub_state = TD_IDLE
                    self.display.deactivate() # possible refactoring 2
        elif 3 in newclicks: # right mouse click
            if self.sub_state == TD_FOLLOW:
                self.purchaser.deactivate()
                self.purchaser = None
                self.selected = None
                self.sub_state = TD_IDLE
                pygame.mouse.set_visible(True)
                self.display.deactivate()
