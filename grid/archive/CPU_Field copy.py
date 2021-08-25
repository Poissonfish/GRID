import numpy as np
import pandas as pd
from scipy.signal import convolve2d
from .Misc import Dir
from .CPU_Agent import Agent

class Field():
    def __init__(self, **params):
        '''
        '''
        self.img_raw = params['crop']
        self.img_bin = params['bin']
        self.img_binsm = self.denoise(self.img_bin, 30)
        self.img_k = params['k']
        self.ls_bin = params['ls_bin']
        self.map = params['map']
        self.anchors = params['anchors']
        self.px_H, self.px_W = self.img_bin.shape[0], self.img_bin.shape[1]
        self.nrow, self.ncol = params['nr'], params['nc']
        self.ch_nir, self.ch_red = params['ch_nir'], params['ch_red']
        self.n_ch = self.img_raw.shape[2]
        self.agents = []
        self.cpu_seg()
    def cpu_seg(self, coef_grid=.2):
        self.set_anchors()
        self.cpu_pre_dim()
        self.cpu_bound(coef_grid=coef_grid)
    def set_anchors(self, center=0):
        '''
        '''
        idx = 0
        idx_name = 1
        for row in range(self.nrow): # then y
            agents_row = []
            for col in range(self.ncol): # start from x
                # get name
                try:
                    name = self.map.iloc[row, col]
                except:
                    name = "id_%d" %(idx_name)
                    idx_name += 1
                # initialize agent
                agent = Agent(name, row, col, self.px_H, self.px_W)
                px_anchors = self.anchors[idx]
                # set position
                pos_x = int(px_anchors['x'])
                pos_y = int(px_anchors['y'])
                agent.set_coordinate(x=pos_x, y=pos_y)
                # see if reduncdent
                rg_x = 20
                rg_y = 20
                try:
                    sc_W = self.img_binsm[(pos_y-rg_y):(pos_y+rg_y), (pos_x-rg_x):pos_x].sum()
                except:
                    sc_W = 0
                try:
                    sc_E = self.img_binsm[(pos_y-rg_y):(pos_y+rg_y), pos_x:(pos_x+rg_x)].sum()
                except:
                    sc_E = 0
                try:
                    sc_N = self.img_binsm[(pos_y-rg_y):pos_y, (pos_x-rg_x):(pos_x+rg_x)].sum()
                except:
                    sc_N = 0
                try:
                    sc_S = self.img_binsm[pos_y:(pos_y+rg_y), (pos_x-rg_x):(pos_x+rg_x)].sum()
                except:
                    sc_S = 0
                # print((sc_W+sc_E+sc_N+sc_S)/(rg_x*rg_y*8))
                if ((sc_W+sc_E+sc_N+sc_S)/(rg_x*rg_y*8))>=center:
                    agent.set_save(save=True)
                # output agent
                agents_row.extend([agent])
                idx += 1
            self.agents.extend([agents_row])
    def cpu_pre_dim(self, tol=5):
        '''
        '''
        img = self.img_binsm
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent_self = self.get_agent(row, col)
                rg_temp = dict()
                for axis in [0, 1]:
                    # extract direction info and 1dImg
                    dir_1 = Dir(axis) # axis:0, return N(0) and S(2)
                    dir_2 = Dir(axis+2) # axis:1, return W(1) and E(3)
                    axis_rev = (not axis)*1
                    img_1d = img[agent_self.y, :] if axis else img[:, agent_self.x]
                    # extract agents info
                    pt_self = agent_self.get_coordinate()[axis_rev]
                    agent_neig1 = self.get_agent_neighbor(row, col, dir_1)
                    agent_neig2 = self.get_agent_neighbor(row, col, dir_2)
                    # if both neighbors exists
                    if (agent_neig1!=0) & (agent_neig2!=0):
                        pt_neig1 = agent_neig1.get_coordinate()[axis_rev]
                        pt_neig2 = agent_neig2.get_coordinate()[axis_rev]
                        pt_mid = int((pt_neig1+pt_neig2)/2)
                        pt_bd1 = int((pt_neig1+pt_mid)/2)
                        pt_bd2 = int((pt_neig2+pt_mid)/2)
                    # if only left/up side exist
                    elif agent_neig1:
                        pt_neig1 = agent_neig1.get_coordinate()[axis_rev]
                        pt_bd1 = int((pt_self+pt_neig1)/2)
                        pt_bd2 = img.shape[axis]
                        agent_self.set_border(dir_2, pt_bd2)
                    # if only right/down side exist
                    elif agent_neig2:
                        pt_neig2 = agent_neig2.get_coordinate()[axis_rev]
                        pt_bd1 = 0
                        pt_bd2 = int((pt_self+pt_neig2)/2)
                        agent_self.set_border(dir_1, pt_bd1)
                    # if neither side exist
                    else:
                        pt_bd1 = 0
                        pt_bd2 = img.shape[axis]
                        agent_self.set_border(dir_1, pt_bd1)
                        agent_self.set_border(dir_2, pt_bd2)
                    # negative side (neighber 1)
                    pt_cur = pt_self
                    tol_cur = 0
                    while (tol_cur < tol) & (pt_cur > pt_bd1):
                        try:
                            img_val = img_1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur -= 1
                    rg_temp[dir_1.name] = pt_cur
                    # positive side (neighber 2)
                    pt_cur = pt_self
                    tol_cur = 0
                    while (tol_cur < tol) & (pt_bd2 > pt_cur):
                        try:
                            img_val = img_1d[pt_cur]
                        except:
                            break
                        tol_cur += 1 if img_val==0 else -tol_cur #else reset to 0
                        pt_cur += 1
                    rg_temp[dir_2.name] = pt_cur
                agent_self.set_pre_dim(rg_temp)
                # print("==== row:%d, col:%d ====" %(row, col))
                # print(rg_temp)
    def cpu_bound(self, coef_grid=.2):
        '''
        '''
        for row in range(self.nrow):
            for col in range(self.ncol):
                self.get_agent(row, col).reset_border()
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent_self = self.get_agent(row, col)
                for dir in list([Dir.EAST, Dir.SOUTH]):
                    agent_neig = self.get_agent_neighbor(row, col, dir)
                    dir_neig = list(Dir)[(dir.value+2)%4] # reverse the direction
                    if agent_neig:
                        # reset agent border
                        agent_self.border[dir.name] = agent_self.border_reset[dir.name]
                        agent_neig.border[dir_neig.name] = agent_neig.border_reset[dir_neig.name]
                        # calculate border
                        dist_agents = abs(agent_self.x-agent_neig.x) if dir==Dir.EAST else abs(agent_self.y-agent_neig.y)
                        while abs(agent_self.get_border(dir)-agent_neig.get_border(dir_neig))>1:
                            scA_self = agent_self.get_score_area(dir, self.img_bin)
                            scG_self = agent_self.get_score_grid(dir)/dist_agents
                            scA_neig = agent_neig.get_score_area(dir_neig, self.img_bin)
                            scG_neig = agent_neig.get_score_grid(dir_neig)/dist_agents
                            score_self = scA_self - (scG_self*coef_grid)
                            score_neig = scA_neig - (scG_neig*coef_grid)
                            if score_self > score_neig:
                                agent_self.update_border(dir, 1)
                            elif score_self < score_neig:
                                agent_neig.update_border(dir_neig, -1)
                            else:
                                agent_self.update_border(dir, 1)
                                agent_neig.update_border(dir_neig, -1)
    def fix_bound(self, width, length):
        '''
        '''
        w_unit = (self.px_W/self.ncol)/100
        l_unit = (self.px_H/self.nrow)/100
        w_side = round(width/2*w_unit)
        l_side = round(length/2*l_unit)
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                agent.reset_border()
                # set border
                if (row==(self.nrow-1)) & (length==100):
                    agent.set_border(Dir.SOUTH, self.px_H)
                else:
                    agent.set_border(Dir.SOUTH, agent.y+l_side)
                if (row==0) & (length==100):
                    agent.set_border(Dir.NORTH, 0)
                else:
                    agent.set_border(Dir.NORTH, agent.y-l_side)
                if (col==(self.ncol-1)) & (width==100):
                    agent.set_border(Dir.EAST, self.px_W)
                else:
                    agent.set_border(Dir.EAST, agent.x+w_side)
                if (col==0) & (width==100):
                    agent.set_border(Dir.WEST, 0)
                else:
                    agent.set_border(Dir.WEST, agent.x-w_side)
    def denoise(self, img, n_denoise=1):
        '''
        '''
        k_blur = np.array((
            [1, 4, 1],\
            [4, 9, 4],\
            [1, 4, 1]), dtype='int')/29
        for i in range(n_denoise):
            img = convolve2d(img, k_blur, mode="same")
        img[img>0.5] = 1
        img[img<=0.5] = 0
        return img
    def get_agent(self, row, col):
        '''
        '''
        if (row<0) | (row>=self.nrow) | (col<0) | (col>=self.ncol):
            return 0
        else:
            return self.agents[row][col]
    def get_agent_neighbor(self, row, col, dir=Dir.NORTH):
        '''
        '''
        if dir==Dir.NORTH:
            return self.get_agent(row-1, col)
        elif dir==Dir.EAST:
            return self.get_agent(row, col+1)
        elif dir==Dir.SOUTH:
            return self.get_agent(row+1, col)
        elif dir==Dir.WEST:
            return self.get_agent(row, col-1)
    def get_DF(self):
        df = pd.DataFrame(columns=['var', 'row', 'col',\
                                   'border_N', 'border_W', 'border_S', 'border_E',\
                                   'area_all', 'area_veg'])
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                entry = dict(var=agent.name, row=agent.row, col=agent.col,\
                             border_N=agent.get_border(Dir.NORTH),\
                             border_W=agent.get_border(Dir.WEST),\
                             border_S=agent.get_border(Dir.SOUTH),\
                             border_E=agent.get_border(Dir.EAST))
                rg_row = range(entry['border_N'], entry['border_S'])
                rg_col = range(entry['border_W'], entry['border_E'])
                img_bin_agent = self.img_bin[rg_row, :][:, rg_col]
                entry['area_all'] = len(rg_row)*len(rg_col)
                entry['area_veg'] = img_bin_agent.sum()
                df.loc[len(df)] = entry
        idx_na = pd.isna(df['var'].values)
        idx_keep = [not boo for boo in idx_na]
        df = df.loc[idx_keep,:]
        return df
    def get_index(self, ch_1, ch_2=-1, ch_3=-1, isSingle=False, isRatio=False, isContrast=False, isThree=False, name_index="index"):
        img_raw = self.img_raw.copy().astype(np.int)
        if img_raw.shape[2]==3 and ch_1==3:
            ch_1 = 1
        if isSingle:
            img_index = (img_raw[:,:,ch_1])
        if isRatio:
            img_index = img_raw[:,:,ch_1]/(img_raw[:,:,ch_2]+1e-8)
        if isContrast:
            img_index = (img_raw[:,:,ch_1]-img_raw[:,:,ch_2])/(img_raw[:,:,ch_1]+img_raw[:,:,ch_2]+1e-8)
        if isThree:
            img_index = (2*img_raw[:,:,ch_1]-img_raw[:,:,ch_2]-img_raw[:,:,ch_3])/(img_raw[:,:,ch_1]+img_raw[:,:,ch_2]+img_raw[:,:,ch_3]+1e-8)
        df = pd.DataFrame(columns=['var', 'index'])
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                entry = dict(var=agent.name, index=0)
                rg_row = range(agent.get_border(Dir.NORTH), agent.get_border(Dir.SOUTH))
                rg_col = range(agent.get_border(Dir.WEST), agent.get_border(Dir.EAST))
                img_bin_agent = self.img_bin[rg_row, :][:, rg_col]
                img_index_agent = img_index[rg_row, :][:, rg_col]
                n_veg = img_bin_agent.sum()
                sum_index = np.multiply(img_bin_agent, img_index_agent).sum()
                entry['index'] = sum_index/(n_veg+1e-8)
                df.loc[len(df)] = entry
        df.columns = ['var', name_index]
        # remove na var
        # idx_na = pd.isna(df['var'].values)
        # idx_keep = [not boo for boo in idx_na]
        # df = df.loc[idx_keep,:]
        return df
    def get_cluster(self):
        # get var name
        df_final = pd.DataFrame(columns=['var'])
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row, col)
                entry = dict(var=agent.name)
                df_final.loc[len(df_final)] = entry
        # get cluster
        cluster = 0
        for i in self.ls_bin:
            img_index = ((np.isin(self.img_k, i))*1).astype(np.int)
            df = pd.DataFrame(columns=['var', 'index'])
            for row in range(self.nrow):
                for col in range(self.ncol):
                    agent = self.get_agent(row, col)
                    entry = dict(var=agent.name, index=0)
                    rg_row = range(agent.get_border(Dir.NORTH), agent.get_border(Dir.SOUTH))
                    rg_col = range(agent.get_border(Dir.WEST), agent.get_border(Dir.EAST))
                    img_bin_agent = self.img_bin[rg_row, :][:, rg_col]
                    img_index_agent = img_index[rg_row, :][:, rg_col]
                    n_veg = img_bin_agent.sum()
                    sum_index = np.multiply(img_bin_agent, img_index_agent).sum()
                    entry['index'] = sum_index/(n_veg+1e-8)
                    df.loc[len(df)] = entry
            df.columns = ['var', "cluster_%d"%cluster]
            df_final = pd.merge(df_final, df, on='var', how='left')
            cluster += 1
        return df_final
    def align(self, method, axis=0):
        '''
        '''
        if method==0:
            # None
            for row in range(self.nrow):
                for col in range(self.ncol):
                    agent = self.get_agent(row=row, col=col)
                    if axis==0:
                        dist = agent.y_reset - agent.y
                    elif axis==1:
                        dist = agent.x_reset - agent.x
                    agent.update_coordinate(dist, axis=axis)
        elif method==1:
            # Top/Left
            if axis==0:
                for row in range(self.nrow):
                    val = 1e10
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        val_temp = agent.y
                        val = val_temp if val_temp<val else val
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.y
                        agent.update_coordinate(dist, axis=axis)
            elif axis==1:
                for col in range(self.ncol):
                    val = 1e10
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        val_temp = agent.x
                        val = val_temp if val_temp<val else val
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.x
                        agent.update_coordinate(dist, axis=axis)
        elif method==3:
            # Bottom/Right
            if axis==0:
                for row in range(self.nrow):
                    val = -1
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        val_temp = agent.y
                        val = val_temp if val_temp>val else val
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.y
                        agent.update_coordinate(dist, axis=axis)
            elif axis==1:
                for col in range(self.ncol):
                    val = -1
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        val_temp = agent.x
                        val = val_temp if val_temp>val else val
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.x
                        agent.update_coordinate(dist, axis=axis)
        elif method==2:
            # Middle/Center
            if axis==0:
                for row in range(self.nrow):
                    val = 0
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        val += agent.y
                    val = int(val/(self.ncol))
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.y
                        agent.update_coordinate(dist, axis=axis)
            elif axis==1:
                for col in range(self.ncol):
                    val = 0
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        val += agent.x
                    val = int(val/(self.nrow))
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        dist = val - agent.x
                        agent.update_coordinate(dist, axis=axis)
    def pan(self, axis, target, value):
        if axis==0:
            for col in range(self.ncol):
                agent = self.get_agent(row=target, col=col)
                dist = value - agent.y
                agent.update_coordinate(dist, axis=axis)
        elif axis==1:
            for row in range(self.nrow):
                agent = self.get_agent(row=row, col=target)
                dist = value - agent.x
                agent.update_coordinate(dist, axis=axis)
    def distributed(self, axis, isEven):
        if isEven:
            if axis==0:
                y_North = self.get_agent(row=0, col=0).y
                y_South = self.get_agent(row=self.nrow-1, col=0).y
                dist = y_South-y_North
                pos_new = np.arange(y_North, y_South, dist/(self.nrow-1))
                pos_new = np.append(pos_new, y_South)
                for row in range(self.nrow):
                    for col in range(self.ncol):
                        agent = self.get_agent(row=row, col=col)
                        dist = pos_new[row] - agent.y
                        agent.update_coordinate(dist, axis=0)
            else:
                x_West = self.get_agent(row=0, col=0).x
                x_East = self.get_agent(row=0, col=self.ncol-1).x
                dist = x_East-x_West
                pos_new = np.arange(x_West, x_East, dist/(self.ncol-1))
                pos_new = np.append(pos_new, x_East)
                for col in range(self.ncol):
                    for row in range(self.nrow):
                        agent = self.get_agent(row=row, col=col)
                        dist = pos_new[col] - agent.x
                        agent.update_coordinate(dist, axis=1)
        else:
            for row in range(self.nrow):
                for col in range(self.ncol):
                    agent = self.get_agent(row=row, col=col)
                    if axis==0:
                        dist = agent.y_reset - agent.y
                    elif axis==1:
                        dist = agent.x_reset - agent.x
                    agent.update_coordinate(dist, axis=axis)
    def reset_coordinate(self):
        for row in range(self.nrow):
            for col in range(self.ncol):
                agent = self.get_agent(row=row, col=col)
                agent.reset_coordinate()
