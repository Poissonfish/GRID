from PyQt5.QtCore import QRect
from .Misc import Dir

class Agent():
    def __init__(self, name, row, col, imgH, imgW):
        '''
        '''
        self.name = name
        self.row, self.col = row, col
        self.imgH, self.imgW = int(imgH), int(imgW)
        self.y, self.x = 0, 0
        self.y_reset, self.x_reset = 0, 0
        self.pre_rg_W, self.pre_rg_H = range(0), range(0)
        self.border, self.border_reset = dict(), dict()
        for dir in list([Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]):
            self.border[dir.name] = 0
            self.border_reset[dir.name] = 0
    def get_col(self):
        '''
        '''
        return self.col
    def get_row(self):
        '''
        '''
        return self.row
    def get_coordinate(self):
        '''
        '''
        return self.x, self.y
    def get_pre_dim(self, isHeight=True):
        '''
        '''
        return self.pre_rg_H if isHeight else self.pre_rg_W
    def get_border(self, dir):
        return self.border[dir.name]
    def get_rect(self):
        x = self.get_border(Dir.WEST)
        y = self.get_border(Dir.NORTH)
        w = self.get_border(Dir.EAST) - x
        h = self.get_border(Dir.SOUTH) - y
        return QRect(x, y, w, h)
    def get_score_area(self, dir, img):
        '''
        Will ragne from 0 to 1
        '''
        isH = dir.value%2 # E->1, S->0
        rg = self.get_pre_dim(isHeight=isH)
        bd = self.get_border(dir)
        # print("==== row:%d, col:%d ====" %(self.row, self.col))
        # print(rg)
        # print(bd)
        return img[rg, bd].mean() if isH else img[bd, rg].mean()
    def get_score_grid(self, dir):
        '''
        Will ragne from 0 to 1
        '''
        isWE = dir.value%2 # is W, E or N, S
        pt_center = self.x if isWE else self.y
        pt_cur = self.get_border(dir)
        return abs(pt_cur-pt_center)
    def set_coordinate(self, x, y):
        '''
        '''
        self.x, self.y = int(x), int(y)
        self.x_reset, self.y_reset = int(x), int(y)
        self.set_border(Dir.NORTH, y)
        self.set_border(Dir.SOUTH, y)
        self.set_border(Dir.WEST, x)
        self.set_border(Dir.EAST, x)
    def set_pre_dim(self, rg):
        '''
        '''
        self.pre_rg_W = range(rg['WEST'], rg['EAST'])
        self.pre_rg_H = range(rg['NORTH'], rg['SOUTH'])
        self.x = int((rg['EAST']+rg['WEST'])/2)
        self.y = int((rg['NORTH']+rg['SOUTH'])/2)
        self.x_reset, self.y_reset = self.x, self.y
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border_reset[dir.name] = self.border[dir.name]
    def set_border(self, dir, value):
        '''
        '''
        self.border[dir.name] = int(value)
        self.check_border()
    def update_border(self, dir, value):
        '''
        '''
        self.border[dir.name] += int(value)
        self.check_border()
    def update_coordinate(self, val, axis=0):
        '''
        '''
        val = int(val)
        if axis==0:
            self.y += val
            self.border[Dir.NORTH.name] += val
            self.border[Dir.SOUTH.name] += val
        elif axis==1:
            self.x += val
            self.border[Dir.WEST.name] += val
            self.border[Dir.EAST.name] += val
        self.check_border()
    def check_border(self):
        if self.border[Dir.NORTH.name]<0:
            self.border[Dir.NORTH.name] = 0
        if self.border[Dir.WEST.name]<0:
            self.border[Dir.WEST.name] = 0
        if self.border[Dir.SOUTH.name]>=self.imgH:
            self.border[Dir.SOUTH.name] = self.imgH-1
        if self.border[Dir.EAST.name]>=self.imgW:
            self.border[Dir.EAST.name] = self.imgW-1
    def set_save(self, save=False):
        "do nothing"
    def reset_coordinate(self):
        self.x = self.x_reset
        self.y = self.y_reset
        self.reset_border()
    def reset_border(self):
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border[dir.name] = self.border_reset[dir.name]
