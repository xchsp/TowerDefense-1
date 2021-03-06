# World Class
#
# Stores the map in a useful way,
# keeps track of cell info, loads
# new maps from files, and answers
# questions about the map.
#
# 2014/3/21
# written by Michael Shawn Redmond

from config import *
import rectangle
import pygame
import os

class World:
    def __init__(self, position, width, height, layout_file=None):
        self.position = position
        self.width = self.safe_assign("Width", width, int, WORLD_DEFAULT_WIDTH)
        self.height = self.safe_assign("Height", height, int, WORLD_DEFAULT_HEIGHT)
        self.cell_width = TILE_WIDTH
        self.cell_height = TILE_HEIGHT
        self.occupied_locations = []
        self.layout = []
        self.tile_types = []
        self.waypoints = []
        self.start_cell = None
        if layout_file is not None:
            self.load_from_file(layout_file)
        self.start = self.get_cell_top_left(self.loc_to_cell(self.start_cell[0], self.start_cell[1]))
        self.order_waypoints()

    def get_position(self):
        return self.position

    def get_dims(self):
        return (self.width, self.height)

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height
            
    # attempts to assign a variable called var_name (for debugging)
    # to a value of value but assigns it to value: default
    # if the original type cannot be casted into desired_type
    def safe_assign(self, var_name, value, desired_type, default):
        if type(desired_type) != type(type(int)):
            print "Desired_type was not a valid type"
            print "Defaulting to type(str)"
            desired_type = str
        if type(value) != desired_type:
            print str(var_name) + " expected to be " + str(desired_type)
            print "Attempting Cast..."
            try:
                value = desired_type(value)
            except:
                print "Unable to convert ", type(value), " to type " + str(desired_type)
                print "Defaulting to", default
                value = default
            print "Type-cast completed"
        return value

    # attempts to open the world file and store the information
    # does nothing if the file was invalid in any way
    def load_from_file(self, layout_file):
        # locate the file
        if not os.path.exists(layout_file):
            print "Error loading world file " + layout_file + ": File was not found."
            print "File will not be loaded"
            return

        # open and read the file
        f = open(layout_file, 'rb')
        fin = [line.strip() for line in f.readlines()]
        f.close()

        # skip past the non-world data
        fin = fin[4:] # skips money, lives, and towers
        skip = int(fin[0])
        fin = fin[skip+1:]

        # grab the dimensions of the world and the starting
        # tile of the path
        data = fin[0].split()
        dim = [0, 0]
        try:
            dim[0] = int(data[0])
            dim[1] = int(data[1])
            if len(data) != 4:
                raise Exception("Invalid layout description\n" + str(dim))
            self.start_cell = (int(data[2]), int(data[3]))

            # verify dimensions
            layout = []
            fin = fin[1:]
            for line in fin:
                if len(line) != dim[0]:
                    raise Exception("Invalid/Mismatched width\n" + str(line))
                else:
                    layout.append(line)
            if len(layout) != dim[1]:
                l = ""
                for i in layout:
                    l += i + '\n'
                l = l.strip()
                raise Exception("Invalid/Mismatched height\n" + l)
        except Exception, e:
            print "Error loading world file " + layout_file + ": Invalid formatting"
            print e
            return False

        # fills remaining tiles to fill world size
        row_size = self.width/self.cell_width
        col_size = self.height/self.cell_height
        filled_rows = int(dim[0])
        filled_cols = int(dim[1])
        empty_rows = row_size - filled_rows
        empty_cols = col_size - filled_cols
        for i in range(len(layout)):
            fill = empty_rows*str(GRASS)
            layout[i] = layout[i] + fill
        for i in range(empty_cols):
            fill = row_size*str(GRASS)
            layout.append(fill)

        # records each tile and its type
        self.layout = []
        waypoints = []
        for j in range(len(layout)):
            r_row = []
            t_row = []
            t_locations = []
            for i in range(len(layout[j])):
                tile = layout[j][i]
                if tile == str(GRASS):
                    img = GRASS_IMG
                elif tile == str(ROCK):
                    img = ROCK_IMG
                else:
                    img = PATH_IMG
                    if tile == str(WAYPOINT):
                        waypoints.append((i, j))
                x = self.position[0] + (i)*self.cell_width
                y = self.position[1] + (j)*self.cell_height
                t_row.append(int(tile))
                
                # tower location default to 0
                t_locations.append(0)
                
                r_row.append(rectangle.Rectangle(KIND_TILE, (x, y), self.cell_width, self.cell_height, img))
            self.layout.append(r_row)
            self.tile_types.append(t_row)
            self.occupied_locations.append(t_locations)
        for point in waypoints:
            self.waypoints.append(self.get_cell_top_left(self.loc_to_cell(point[0], point[1])))
        return True

    # a cell is a middle path if
    # it is surrounded by ONLY
    # path cells (diagonals included) 
    def cell_is_middle_path(self, i, j):
        # waypoints are assumed to be placed correctly
        if self.tile_types[j][i] == WAYPOINT:
            return True

        # looks in each direction
        can_top = j > 0
        can_left = i > 0
        can_right = i < self.width - 1
        can_bottom = j < self.height - 1
        if can_top:
            if not self.cell_is_path(self.loc_to_cell(i, j-1)):
                return False
            if can_left:
                if not self.cell_is_path(self.loc_to_cell(i-1, j-1)):
                    return False
            if can_right:
                if not self.cell_is_path(self.loc_to_cell(i+1, j-1)):
                    return False
        else:
            return False
        if not can_left or not self.cell_is_path(self.loc_to_cell(i-1, j)):
            return False
        if not can_right or not self.cell_is_path(self.loc_to_cell(i+1, j)):
            return False
        if can_bottom:
            if not self.cell_is_path(self.loc_to_cell(i, j+1)):
                return False
            if can_left:
                if not self.cell_is_path(self.loc_to_cell(i-1, j+1)):
                    return False
            if can_right:
                if not self.cell_is_path(self.loc_to_cell(i+1, j+1)):
                    return False
        else:
            return False
        return True

    # finds the possible neighbors to a middle path cell
    def get_path_neighbors(self, i, j): # diagonals not included
        neighbors = []
        # check for bounds
        can_top = j > 0
        can_left = i > 0
        can_right = i < self.width - 1
        can_bottom = j < self.height - 1
        if can_top and self.cell_is_middle_path(i, j-1):
            neighbors.append((i, j-1))
        if can_left and self.cell_is_middle_path(i-1, j):
            neighbors.append((i-1, j))
        if can_right and self.cell_is_middle_path(i+1, j):
            neighbors.append((i+1, j))
        if can_bottom and self.cell_is_middle_path(i, j+1):
            neighbors.append((i, j+1))
        return neighbors

    # orders the waypoints in the order
    # that they would be reached when
    # walking the path
    def order_waypoints(self):
        ordered_waypoints = []
        i, j = self.start_cell
        count = 0
        end = len(self.waypoints)
        prev = []
        while count < end:
            next_prev = []
            neighbors = self.get_path_neighbors(i, j)
            for neighbor in neighbors:
                # verify that the neighbor is a middle path cell (path in every direction)
                if neighbor not in prev:
                    next_prev.append((i, j))
                    i, j = neighbor
                    if self.tile_types[j][i] == WAYPOINT:
                        count += 1
                        ordered_waypoints.append(self.get_cell_top_left(self.loc_to_cell(i, j)))
            prev = next_prev[:]
        self.waypoints = ordered_waypoints[:]
        
        # adds an extra waypoint to make the
        # "end" of the path be slightly off
        # of the screen
        last = self.waypoints[-1]
        p = self.get_cell_top_left(self.loc_to_cell(prev[0][0], prev[0][1]))
        dx, dy = (last[0]-p[0], last[1]-p[1])
        end = (last[0]+dx*2, last[1]+dy*2)
        self.waypoints.append(end)

    # given how many waypoints have been reached
    # returns the next waypoint's position
    def next_waypoint(self, num_visited):
        if num_visited > len(self.waypoints):
            return None
        elif num_visited == 0:
            return self.start
        else:
            return self.waypoints[num_visited-1]

    def get_waypoints(self):
        return self.waypoints

    def paint(self, surface):
        for row in self.layout:
            for cell in row:
                cell.paint(surface)

    # returns the cell number of a cell containing
    # a certain position
    def get_cell_at(self, position):
        for j in range(len(self.layout)):
            for i in range(len(self.layout[0])):
                if self.layout[j][i].is_inside(position):
                    return self.loc_to_cell(i, j)
        return None
        
    def get_start(self):
        return self.start

    def get_end(self):
        return self.waypoints[-1]

    # returns the cell number corresponding to given coordinates
    def loc_to_cell(self, i, j):
        # where i is the column, j is the row
        return j*(self.width/self.cell_width) + i

    # returns the coordinates corresponding to a given cell number
    def cell_to_loc(self, cell_num):
        i = cell_num%(self.width/self.cell_width)
        j = cell_num/(self.width/self.cell_width)
        return i, j

    # returns the position of the top left corner
    # of a cell specified by a given cell number
    def get_cell_top_left(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        return self.layout[j][i].get_position()

    # returns the position of the center of a
    # cell specified by a given cell number
    def get_cell_center(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        return self.layout[j][i].get_center()

    # returns if a given cell is a path cell
    def cell_is_path(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        return self.tile_types[j][i] == PATH or self.tile_types[j][i] == WAYPOINT

    # returns if a given cell is a rock cell
    def cell_is_rock(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        return self.tile_types[j][i] == ROCK

    # records that a given cell is occupied 
    def occupy_cell(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        self.occupied_locations[j][i] = 1

    # records that a group of cells is occupied
    def occupy_area(self, pos, dims):
        x_span = dims[0] / self.cell_width
        y_span = dims[1] / self.cell_height
        for i in range(x_span):
            for j in range(y_span):
                p = (pos[0] + i*self.cell_width, pos[1] + j*self.cell_height)
                cell_num = self.get_cell_at(p)
                self.occupy_cell(cell_num)

    # records that a cell is free
    def free_cell(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        self.occupied_locations[j][i] = 0

    # records that an group of cells is free
    def free_area(self, pos, dims):
        x_span = dims[0] / self.cell_width
        y_span = dims[1] / self.cell_height
        for i in range(x_span):
            for j in range(y_span):
                p = (pos[0] + i*self.cell_width, pos[1] + j*self.cell_height)
                cell_num = self.get_cell_at(p)
                self.free_cell(cell_num)

    # returns whether or not a given cell number exists
    def has_cell(self, cell_num):
        if cell_num is None or cell_num >= (self.width/self.cell_width)*(self.height/self.cell_height):
            return False
        return True

    # returns whether or not a given cell is occupied
    def is_occupied(self, cell_num):
        i, j = self.cell_to_loc(cell_num)
        return self.occupied_locations[j][i] == 1

    # returns whether or not the cells in a
    # certain area are buildable
    def can_build_tower(self, pos, dims):
        # assumes that the object's size is a whole amount of tiles
        x_span = dims[0] / self.cell_width
        y_span = dims[1] / self.cell_height
        for i in range(x_span):
            for j in range(y_span):
                p = (pos[0] + i*self.cell_width, pos[1] + j*self.cell_height)
                cell_num = self.get_cell_at(p)
                if not self.has_cell(cell_num) or self.cell_is_path(cell_num) or self.is_occupied(cell_num) or self.cell_is_rock(cell_num):
                    return False
        return True

    def can_build_trap(self, pos, dims):
        # assumes that the object's size is a whole amount of tiles
        x_span = dims[0] / self.cell_width
        y_span = dims[1] / self.cell_height
        for i in range(x_span):
            for j in range(y_span):
                p = (pos[0] + i*self.cell_width, pos[1] + j*self.cell_height)
                cell_num = self.get_cell_at(p)
                if not self.has_cell(cell_num):
                    return False
                i, j = self.cell_to_loc(cell_num)
                if not self.cell_is_middle_path(i, j) or self.is_occupied(cell_num) or self.cell_is_rock(cell_num):
                    return False
        return True

    # returns whether or not a position is inside the world
    def is_inside(self, position):
        if position[0] >= self.position[0] and position[0] < self.position[0] + self.width:
            if position[1] >= self.position[1] and position[1] < self.position[1] + self.height:
                return True
        return False

    # prints the world to the screen in text format
    def __str__(self):
        board = ""
        for row in self.layout:
            line = ""
            for cell in row:
                line += str(cell)
            board += line + '\n'
        return board
