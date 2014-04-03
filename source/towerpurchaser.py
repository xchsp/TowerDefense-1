# Towerpurchaser Class
#
# Displays a picture of a given
# tower and alerts the menu when
# the image is clicked to signal
# an the beginning of a purchase
# of a specific tower
#
# 2014/3/27
# written by Michael Shawn Redmond

import rectangle
from config import *

class TowerPurchaser():
    def __init__(self, position, towertype, tower_width, tower_height):
        self.position = position
        self.towertype = towertype
        self.tower = towertype(position)
        self.status = P_IDLE
        self.follower = None
        self.width = tower_width
        self.height = tower_height
        
    def get_width(self):
        return self.width
        
    def get_height(self):
        return self.height
        
    def get_dims(self):
        return (self.get_width(), self.get_height())

    def paint(self, surface):
        self.tower.paint(surface)
        if self.status == P_FOLLOW:
            self.follower.paint(surface)

    def toggle_status(self):
        if self.status == P_IDLE:
            self.status = P_FOLLOW
        else:
            self.status =  P_IDLE

    def game_logic(self, keys, newkeys, mouse_pos, newclicks, instructions):
        for instruction in instructions:
            if instruction[0] == P_SNAP_LOC and self.status == P_FOLLOW:
                self.follower.set_position(instruction[1])
        
        actions = []
        if 1 in newclicks: # left click
            if self.status == P_IDLE and self.tower.is_inside(mouse_pos):
                self.follower = self.towertype(self.position)
                actions.append((P_FOLLOW, self.towertype))
                self.toggle_status()
            elif self.status == P_FOLLOW :
                actions.append((P_PLACE, self.towertype))
                self.follower = None
                self.toggle_status()
        return actions