# basic imports
import numpy as np
import pandas as pd

# self imports
from .lib import *
from .dir import Dir


class GAgent():

    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """

        self.agents = []
        self.img = None
        self.shape = (0, 0)
        self.imgH, self.imgW = self.shape
        self.nRow, self.nCol = 0, 0
        self.rowFake, self.colFake = -1, -1
        self.coef = 0

        # progress bar
        self.flag = True
        self.subflag = True
        self.window = 1000

    def setup(self, gmap, gimg):
        """
        ----------
        Parameters
        ----------
        """

        self.agents = []
        self.img = gimg.get('binSeg')
        self.shape = self.img.shape
        self.imgH, self.imgW = self.shape

        # get nrow, ncol, and data.frame
        if not gimg.hasShp:
            self.nRow, self.nCol = gmap.nRow, gmap.nCol
            dt = gmap.dt
        else:
            '''
            A case when a shapefile is loaded
            '''
            # get transformation info
            affine = gimg.tiff_transform
            pts_crop = gimg.pts_crop
            mat_H = gimg.mat_H

            # load agents
            agents = gimg.f_shp.shapeRecords()

            # iteratively search for agents
            ls_id = []
            ls_row = []
            ls_col = []
            ls_ct = []
            ls_w, ls_n, ls_e, ls_s = [], [], [], []
            nrow = -1
            ncol = -1

            n_agents = len(agents)
            for i in range(n_agents):
                # extract agent info
                pts_ag = agents[i].shape.points
                att_ag = agents[i].record

                # find the remap pts
                pts_xy = [invAffine(pts_ag[i], affine) for i in range(4)]

                pts_crop_temp = np.matmul(
                    mat_H, np.float32(pts_xy).transpose()).transpose()

                pts_crop = np.array([pts_crop_temp[i, :2] / pts_crop_temp[i, 2]
                                     for i in range(4)], dtype=int)
                # pts_crop = np.array(pts_crop_temp[:, :2], dtype=int)

                # find the centers
                pt_ct = np.mean(pts_crop, axis=0, dtype=int)
                ls_ct.append(pt_ct)
                # find the borders
                bd_w, bd_n = np.min(pts_crop, axis=0)
                bd_e, bd_s = np.max(pts_crop, axis=0)
                # examine the border
                bd_w = 0 if bd_w < 0 else bd_w
                bd_n = 0 if bd_n < 0 else bd_n
                bd_e = self.imgW - 1 if bd_e >= self.imgW else bd_e
                bd_s = self.imgH - 1 if bd_s >= self.imgH else bd_s
                # put in the list
                ls_w.append(bd_w)
                ls_n.append(bd_n)
                ls_e.append(bd_e)
                ls_s.append(bd_s)
                # get row and col
                row, col = np.array(att_ag[1:3], dtype=int)
                ls_row.append(row)
                ls_col.append(col)
                nrow = row if row > nrow else nrow
                ncol = col if col > ncol else ncol
                # get name
                name = att_ag[0]
                ls_id.append(name)

            # add by 1 as it's 0-index
            nrow += 1
            ncol += 1

            # assign
            self.nRow, self.nCol = nrow, ncol
            gmap.dt = pd.DataFrame(
                {"var": ls_id, "row": ls_row, "col": ls_col, "pt": ls_ct,
                 "bd_w": ls_w, "bd_n": ls_n, "bd_e": ls_e, "bd_s": ls_s})
            dt = gmap.dt

        # initialize agents
        fr, fc = [], []
        for row in range(self.nRow):
            lsAgentsRow = []
            for col in range(self.nCol):
                try:
                    entry = dt[(dt.row == row) & (dt.col == col)].iloc[0]
                    ptX, ptY = entry["pt"]
                    name = entry["var"]
                except Exception:
                    # handle inconsistant # of rows/cols
                    fr.append(row)
                    fc.append(col)
                    ptX, ptY = (-1, -1)
                    name = "_FAKE"
                agent = Agent(name=name, row=row, col=col)
                self.setCoordinate(agent=agent, x=ptX, y=ptY)
                try:
                    # load boundaries if available
                    agent.setBorder(Dir.WEST, entry['bd_w'])
                    agent.setBorder(Dir.NORTH, entry['bd_n'])
                    agent.setBorder(Dir.EAST, entry['bd_e'])
                    agent.setBorder(Dir.SOUTH, entry['bd_s'])
                except Exception:
                    None
                lsAgentsRow.append(agent)
            self.agents.append(lsAgentsRow)

        self.rowFake, self.colFake = -1, -1
        # determine fake plots
        if len(fr) > 1 and np.array(fr).var() == 0:
            self.rowFake = fr[0]
        elif len(fc) > 1 and np.array(fc).var() == 0:
            self.colFake = fc[0]

    def get(self, row, col):
        """
        ----------
        Parameters
        ----------
        """

        if row < 0 or col < 0:
            # negative index
            return False
        else:
            try:
                return self.agents[int(row)][int(col)]
            except Exception:
                # outside frame
                return False

    def getNeib(self, row, col, dir):
        """
        ----------
        Parameters
        ----------
        """

        if dir == Dir.EAST:
            agent = self.get(row, col+1)
            if not agent:
                # outside image
                return False
            elif (col+1 == self.colFake):
                # on fake line
                return agent
            elif agent.isFake():
                return self.get(row-1, col+1)
            else:
                return agent
        elif dir == Dir.SOUTH:
            agent = self.get(row+1, col)
            if not agent:
                # outside image
                return False
            elif (row+1 == self.rowFake):
                # on fake line
                return agent
            elif agent.isFake():
                return self.get(row+1, col-1)
            else:
                return agent
        elif dir == Dir.WEST:
            agent = self.get(row, col-1)
            if not agent:
                # outside image
                return False
            elif agent.isFake():
                return self.get(row-1, col-1)
            else:
                return agent
        elif dir == Dir.NORTH:
            agent = self.get(row-1, col)
            if not agent:
                # outside image
                return False
            elif agent.isFake():
                return self.get(row+1, col-1)
            else:
                return agent

    def cpuPreDim(self, tol=5):
        """
        ----------
        Parameters
        ----------
        """
        self.isWork = True

        # prog = initProgress(self.nRow, name="Estimating dimentions")
        for row in range(self.nRow):
            # updateProgress(prog)
            for col in range(self.nCol):
                agentSelf = self.get(row, col)
                agentSelf.resetBorderHard()
                if not agentSelf or agentSelf.isFake():
                    continue
                rgTemp = dict()
                for axis in [0, 1]:
                    # extract direction info and 1dImg
                    dir1 = Dir(axis)  # axis:0, return N(0) and S(2)
                    dir2 = Dir(axis + 2)  # axis:1, return W(1) and E(3)
                    axisRev = (not axis) * 1
                    # img1d = self.img[agentSelf.y,
                    #                  :] if axis else self.img[:, agentSelf.x]
                    # extract agents info
                    ptSelf = agentSelf.getCoordinate()[axisRev]
                    agentNeig1 = self.getNeib(row, col, dir1)
                    agentNeig2 = self.getNeib(row, col, dir2)
                    # if both neighbors exists
                    if (agentNeig1 != 0) and (agentNeig2 != 0) and (not agentNeig1.isFake()) and (not agentNeig2.isFake()):
                        ptNeig1 = agentNeig1.getCoordinate()[axisRev]
                        ptNeig2 = agentNeig2.getCoordinate()[axisRev]
                        ptMid = int((ptNeig1 + ptNeig2) / 2)
                        ptBd1 = int((ptNeig1 + ptMid) / 2)
                        ptBd2 = int((ptNeig2 + ptMid) / 2)
                    # if only left/up side exist
                    elif agentNeig1:
                        ptNeig1 = agentNeig1.getCoordinate()[axisRev]
                        ptBd1 = int((ptSelf + ptNeig1) / 2)
                        ptBd2 = self.img.shape[axis]
                        self.setBorder(agentSelf, dir2, ptBd2)
                    # if only right/down side exist
                    elif agentNeig2:
                        ptNeig2 = agentNeig2.getCoordinate()[axisRev]
                        ptBd1 = 0
                        ptBd2 = int((ptSelf + ptNeig2) / 2)
                        self.setBorder(agentSelf, dir1, ptBd1)
                    # if neither side exist
                    elif self.nRow == 1 or self.nCol == 1:
                        ptBd1 = 0
                        ptBd2 = self.img.shape[axis]
                        self.setBorder(agentSelf, dir1, ptBd1)
                        self.setBorder(agentSelf, dir2, ptBd2)

                    # check if invade to its neigbor
                    # new_centroid = (ptBd1 + ptBd2) / 2
                    # if new_centroid >=

                    # # get predim
                    # # negative side (neighber 1)
                    # pt_cur = ptSelf
                    # tol_cur = 0
                    # while (tol_cur < tol) & (pt_cur > ptBd1):
                    #     try:
                    #         img_val = img1d[pt_cur]
                    #     except Exception:
                    #         break
                    #     tol_cur += 1 if img_val == 0 else - tol_cur  # else reset to 0
                    #     pt_cur -= 1
                    # rgTemp[dir1.name] = pt_cur
                    # # positive side (neighber 2)
                    # pt_cur = ptSelf
                    # tol_cur = 0
                    # while (tol_cur < tol) & (ptBd2 > pt_cur):
                    #     try:
                    #         img_val = img1d[pt_cur]
                    #     except Exception:
                    #         break
                    #     tol_cur += 1 if img_val == 0 else - tol_cur  # else reset to 0
                    #     pt_cur += 1
                    # rgTemp[dir2.name] = pt_cur

                    rgTemp[dir1.name] = ptBd1
                    rgTemp[dir2.name] = ptBd2

                agentSelf.setPreDim(rgTemp)

    def autoSeg(self, coefGrid=.2):
        """
        ----------
        Parameters
        ----------
        """
        self.coef = coefGrid

        # reset the border first
        self.resetBorder()

        # progress bar
        prog = None
        if self.flag:
            self.flag = False
            prog = initProgress(self.nRow, name="Segmenting")

        # loop over rows and cols
        for row in range(self.nRow):
            updateProgress(prog, flag=self.subflag)
            for col in range(self.nCol):
                agentSelf = self.get(row, col)
                for dir in list([Dir.EAST, Dir.SOUTH]):
                    agentNeib = self.getNeib(row, col, dir)
                    dirNeib = list(Dir)[(dir.value+2) %
                                         4]  # reverse the direction
                    if not agentSelf or agentSelf.isFake() or not agentNeib or agentNeib.isFake():
                        continue
                    # reset agent border
                    agentSelf.border[dir.name] = agentSelf.border_reset[dir.name]
                    agentNeib.border[dirNeib.name] = agentNeib.border_reset[dirNeib.name]
                    # calculate border
                    if dir == Dir.EAST:
                        dist_agents = abs(agentSelf.x - agentNeib.x)
                    else:
                        dist_agents = abs(agentSelf.y-agentNeib.y)

                    while (agentNeib.getBorder(dirNeib) - agentSelf.getBorder(dir)) > 1:
                        scASelf = agentSelf.getScoreArea(
                            dir, self.img)
                        scGSelf = agentSelf.getScoreGrid(
                            dir) / dist_agents
                        scANeib = agentNeib.getScoreArea(
                            dirNeib, self.img)
                        scGNeib = agentNeib.getScoreGrid(
                            dirNeib) / dist_agents
                        # except Exception as e:
                        scoreSelf = scASelf - (scGSelf * coefGrid)
                        scoreNeib = scANeib - (scGNeib * coefGrid)
                        if scoreSelf > scoreNeib:
                            self.updateBorder(agentSelf, dir, 1)
                        elif scoreSelf < scoreNeib:
                            self.updateBorder(agentNeib, dirNeib, -1)
                        else:
                            self.updateBorder(agentSelf, dir, 1)
                            self.updateBorder(agentNeib, dirNeib, -1)

        if self.subflag and "__main__.py" in sys.argv[0]:
            self.subflag = False
            QTimer.singleShot(self.window, lambda: setattr(self, "flag", True))
            QTimer.singleShot(self.window, lambda: setattr(self, "subflag", True))

        # rescue plots on fake line
        if self.rowFake != -1:
            for col in range(1, self.nCol):
                agent = self.get(self.rowFake, col)
                if not agent.isFake():
                    agentNeig = self.get(self.rowFake-1, col-1)
                    agent.setBorder(Dir.WEST, agentNeig.getBorder(Dir.EAST))
        elif self.colFake != -1:
            for row in range(1, self.nRow):
                agent = self.get(row, self.colFake)
                if not agent.isFake():
                    agentNeig = self.get(row-1, self.colFake-1)
                    agent.setBorder(Dir.NORTH, agentNeig.getBorder(Dir.SOUTH))

    def fixSeg(self, width, length):
        w_unit = (self.imgW / self.nCol) / 100
        l_unit = (self.imgH / self.nRow) / 100
        w_side = round(width / 2 * w_unit)
        l_side = round(length / 2 * l_unit)
        for row in range(self.nRow):
            for col in range(self.nCol):
                agent = self.get(row, col)
                if not agent or agent.isFake():
                    continue
                agent.resetBorder()
                # set border
                if (row == (self.nRow-1)) & (length == 100):
                    self.setBorder(agent, Dir.SOUTH, self.imgH)
                else:
                    self.setBorder(agent, Dir.SOUTH, agent.y+l_side)
                if (row == 0) & (length == 100):
                    self.setBorder(agent, Dir.NORTH, 0)
                else:
                    self.setBorder(agent, Dir.NORTH, agent.y-l_side)
                if (col == (self.nCol-1)) & (width == 100):
                    self.setBorder(agent, Dir.EAST, self.imgW)
                else:
                    self.setBorder(agent, Dir.EAST, agent.x+w_side)
                if (col == 0) & (width == 100):
                    self.setBorder(agent, Dir.WEST, 0)
                else:
                    self.setBorder(agent, Dir.WEST, agent.x-w_side)

    def setCoordinate(self, agent, x, y):
        agent.setCoordinate(x, y)
        self.checkBorder(agent)

    def updateCoordinate(self, agent, value, axis):
        agent.updateCoordinate(value, axis)
        self.checkBorder(agent)

    def setBorder(self, agent, dir, value):
        agent.setBorder(dir, value)
        self.checkBorder(agent)

    def updateBorder(self, agent, dir, value):
        agent.updateBorder(dir, value)
        self.checkBorder(agent)

    def resetCoordinate(self):
        for row in range(self.nRow):
            for col in range(self.nCol):
                try:
                    self.get(row=row, col=col).resetCoordinate()
                except Exception:
                    None

    def resetBorder(self):
        for row in range(self.nRow):
            for col in range(self.nCol):
                try:
                    self.get(row=row, col=col).resetBorder()
                except Exception:
                    None

    def checkBorder(self, agent):
        if agent.border[Dir.NORTH.name] < 0:
            agent.border[Dir.NORTH.name] = 0
        if agent.border[Dir.WEST.name] < 0:
            agent.border[Dir.WEST.name] = 0
        if agent.border[Dir.SOUTH.name] >= self.imgH:
            agent.border[Dir.SOUTH.name] = self.imgH-1
        if agent.border[Dir.EAST.name] >= self.imgW:
            agent.border[Dir.EAST.name] = self.imgW-1

    def align(self, method, axis=0):
        '''
        '''
        if method == 0:
            # None
            for row in range(self.nRow):
                for col in range(self.nCol):
                    agent = self.get(row=row, col=col)
                    if not agent or agent.isFake():
                        continue
                    if axis == 0:
                        dist = agent.y_reset - agent.y
                    elif axis == 1:
                        dist = agent.x_reset - agent.x
                    self.updateCoordinate(agent, dist, axis=axis)
        elif method == 1:
            # Top/Left
            if axis == 0:
                for row in range(self.nRow):
                    val = 1e10
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.y
                        val = val_temp if val_temp < val else val
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = 1e10
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.x
                        val = val_temp if val_temp < val else val
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)
        elif method == 3:
            # Bottom/Right
            if axis == 0:
                for row in range(self.nRow):
                    val = -1
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.y
                        val = val_temp if val_temp > val else val
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = -1
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val_temp = agent.x
                        val = val_temp if val_temp > val else val
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)
        elif method == 2:
            # Middle/Center
            if axis == 0:
                for row in range(self.nRow):
                    val = 0
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val += agent.y
                    val = int(val/(self.nCol))
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.y
                        self.updateCoordinate(agent, dist, axis=axis)
            elif axis == 1:
                for col in range(self.nCol):
                    val = 0
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        val += agent.x
                    val = int(val/(self.nRow))
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = val - agent.x
                        self.updateCoordinate(agent, dist, axis=axis)

    def pan(self, axis, target, value):
        if axis == 0:
            for col in range(self.nCol):
                agent = self.get(row=target, col=col)
                # dist = value - agent.y
                self.updateCoordinate(agent, value, axis=axis)
        elif axis == 1:
            for row in range(self.nRow):
                agent = self.get(row=row, col=target)
                # dist = value - agent.x
                self.updateCoordinate(agent, value, axis=axis)

    def distributed(self, axis, isEven):
        if isEven:
            if axis == 0:
                # row
                y_North = self.get(row=0, col=0).y
                y_South = self.get(row=self.nRow - 1, col=0).y
                dist = y_South - y_North
                pos_new = np.arange(y_North, y_South, dist / (self.nRow - 1))
                pos_new = np.append(pos_new, y_South)
                for row in range(self.nRow):
                    for col in range(self.nCol):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = pos_new[row] - agent.y
                        self.updateCoordinate(agent=agent, value=dist, axis=0)
            else:
                # col
                x_West = self.get(row=0, col=0).x
                x_East = self.get(row=0, col=self.nCol - 1).x
                dist = x_East-x_West
                pos_new = np.arange(x_West, x_East, dist / (self.nCol - 1))
                pos_new = np.append(pos_new, x_East)
                for col in range(self.nCol):
                    for row in range(self.nRow):
                        agent = self.get(row=row, col=col)
                        if not agent or agent.isFake():
                            continue
                        dist = pos_new[col] - agent.x
                        self.updateCoordinate(agent=agent, value=dist, axis=1)
        else:
            for row in range(self.nRow):
                for col in range(self.nCol):
                    agent = self.get(row=row, col=col)
                    if not agent or agent.isFake():
                        continue
                    if axis == 0:
                        dist = agent.y_reset - agent.y
                    elif axis == 1:
                        dist = agent.x_reset - agent.x
                    self.updateCoordinate(agent=agent, value=dist, axis=axis)


class Agent():
    def __init__(self, name, row, col):
        '''
        '''
        self.name = name
        self.row, self.col = row, col
        self.y, self.x = 0, 0
        self.y_float, self.x_float = 0.0, 0.0  # range from 0 to 0.9999
        self.y_reset, self.x_reset = 0, 0
        self.pre_rg_W, self.pre_rg_H = range(0), range(0)
        self.border, self.border_reset = dict(), dict()
        for dir in list([Dir.NORTH, Dir.EAST, Dir.SOUTH, Dir.WEST]):
            self.border[dir.name] = 0
            self.border_reset[dir.name] = 0

    def getCoordinate(self):
        '''
        '''
        return self.x, self.y

    def getPreDim(self, isHeight=True):
        '''
        '''
        return self.pre_rg_H if isHeight else self.pre_rg_W

    def getBorder(self, dir):
        return self.border[dir.name]

    def getScoreArea(self, dir, img):
        '''
        Will ragne from 0 to 1
        '''
        isH = dir.value % 2 # E->1, S->0
        rg = self.getPreDim(isHeight=isH)
        bd = self.getBorder(dir)
        return img[rg, bd].mean() if isH else img[bd, rg].mean()

    def getScoreGrid(self, dir):
        '''
        Will ragne from 0 to 1
        '''
        isWE = dir.value % 2 # is W, E or N, S
        pt_center = self.x if isWE else self.y
        pt_cur = self.getBorder(dir)
        return abs(pt_cur-pt_center)

    def setCoordinate(self, x, y):
        '''
        '''
        self.x, self.y = int(x), int(y)
        self.x_reset, self.y_reset = int(x), int(y)
        self.setBorder(Dir.NORTH, y)
        self.setBorder(Dir.SOUTH, y)
        self.setBorder(Dir.WEST, x)
        self.setBorder(Dir.EAST, x)

    def setPreDim(self, rg):
        '''
        '''
        self.pre_rg_W = range(rg['WEST'], rg['EAST'])
        self.pre_rg_H = range(rg['NORTH'], rg['SOUTH'])
        # self.x = int((rg['EAST']+rg['WEST'])/2)
        # self.y = int((rg['NORTH']+rg['SOUTH'])/2)
        # self.x_reset, self.y_reset = self.x, self.y
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border_reset[dir.name] = self.border[dir.name]

    def setBorder(self, dir, value):
        '''
        '''
        self.border[dir.name] = int(value)

    def updateBorder(self, dir, value):
        '''
        '''
        self.border[dir.name] += int(value)

    def updateCoordinate(self, value, axis=0):
        '''
        decompose value to integer and floating parts
        '''
        if axis == 0:
            self.y_float += value
            dy, self.y_float = self.y_float // 1, self.y_float % 1
            self.y += dy
            self.border[Dir.NORTH.name] += dy
            self.border[Dir.SOUTH.name] += dy
        elif axis == 1:
            self.x_float += value
            dx, self.x_float = self.x_float // 1, self.x_float % 1
            self.x += dx
            self.border[Dir.WEST.name] += dx
            self.border[Dir.EAST.name] += dx

    def getQRect(self):
        """
        GUI SPECIFIC
        """
        x = self.getBorder(Dir.WEST)
        y = self.getBorder(Dir.NORTH)
        w = self.getBorder(Dir.EAST) - x
        h = self.getBorder(Dir.SOUTH) - y
        return QRect(x, y, w, h)

    def resetCoordinate(self):
        self.x = self.x_reset
        self.y = self.y_reset
        self.resetBorder()

    def resetBorder(self):
        for dir in list([Dir.NORTH, Dir.WEST, Dir.SOUTH, Dir.EAST]):
            self.border[dir.name] = self.border_reset[dir.name]

    def resetBorderHard(self):
        self.setBorder(Dir.WEST, self.x)
        self.setBorder(Dir.EAST, self.x)
        self.setBorder(Dir.NORTH, self.y)
        self.setBorder(Dir.SOUTH, self.y)

    def isFake(self):
        return self.name == "_FAKE"
