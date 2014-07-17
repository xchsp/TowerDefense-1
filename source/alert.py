# Alert class
#
# Displays a message, inside a specified
# area to the screen
#
# 2014/7/15
# written by Michael Shawn Redmond

import pygame
from config import *
import time

class Alert():
    def __init__(self, position, width, height, message, expires = False, duration = 3, font = ALERT_FONT, font_size = ALERT_FONT_SIZE, font_color = ALERT_FONT_COLOR, margin_x = ALERT_MARGIN_X, margin_y = ALERT_MARGIN_Y, bg_color = ALERT_BG_COLOR, o_color = ALERT_O_COLOR):
        self.position = position # topleft
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(font, font_size)
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.format_message(message)
        self.font_color = font_color
        self.bg_color = bg_color
        self.o_color = o_color
        self.expires = expires
        self.duration = duration
        self.start = time.time()

    def format_message(self, message):
        # seperate the whole message into pieces
        # that fit within the width of the
        # given area
        messages = [message]
        while self.font.size(messages[-1])[0] > self.width - 2*self.margin_x:
            m1 = messages[-1][:-1]
            m2 = messages[-1][-1]
            while self.font.size(m1)[0] > self.width - 2*self.margin_x:
                word = m1[-1]
                m1 = m1[:-1]
                while not m1[-1].isspace():
                    word = m1[-1] + word
                    m1 = m1[:-1]
                    if len(m1) == 0:
                        break
                m2 = word + ' ' + m2
                m1 = m1[:-1]
            messages[-1] = m1
            messages.append(m2)
        self.messages = messages

        # store the sizes of each piece
        message_sizes = []
        for message in self.messages:
            message_sizes.append(self.font.size(message))
        self.message_sizes = message_sizes

        # store the positions of each piece
        message_positions = []
        y = self.margin_y
        for i in range(len(self.messages)):
            x = (self.width - self.message_sizes[i][0])*.5
            message_positions.append((x, y))
            y += self.margin_y + self.message_sizes[i][1]
        self.message_positions = message_positions

    def game_logic(self, keys, newkeys, mouse_pos, newclicks,):
        actions = []
        if self.expires and time.time() - self.start >= self.duration:
            actions.append((ALERT_EXP_MESSAGE, self))
        return actions

    def set_bg_color(self, bg_color):
        self.bg_color = bg_color

    def set_o_color(self, o_color):
        self.o_color = o_color

    def set_font(self, font, font_size):
        self.font = pygame.font.SysFont(font, font_size)

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def calc_center(self):
        px, py = self.position
        cx, cy = px + .5*self.width, py + .5*self.height
        return (int(cx), int(cy))

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position
        self.calc_center

    def get_center(self):
        return self.calc_center()

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width
        self.calc_center

    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height
        self.cacl_center

    def get_dims(self):
        return (self.get_width(), self.get_height())
    
    def paint(self, surface):
        a_surface = pygame.Surface((self.width, self.height))
        a_surface.fill(self.bg_color)
        r = pygame.Rect((0, 0), (self.width, self.height))
        pygame.draw.rect(a_surface, self.o_color, r, ALERT_OUTLINE_WIDTH)

        for i in range(len(self.messages)):
            temp_surface = self.font.render(self.messages[i], 1, self.font_color)
            a_surface.blit(temp_surface, self.message_positions[i])
            
        surface.blit(a_surface, self.position)

    def is_inside(self, position):
        if position[0] >= self.position[0] and position[0] < self.position[0] + self.width:
            if position[1] >= self.position[1] and position[1] < self.position[1] + self.height:
                return True
        return False