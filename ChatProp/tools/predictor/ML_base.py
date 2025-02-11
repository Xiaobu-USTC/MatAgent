import subprocess
import sys
import os
import numpy as np
from deepmd.infer import DeepPot

class PT_Predictor():
    def __init__(self, path, cor, box, atype):
        self.path = path
        self.cor = cor
        self.box = box
        self.atype = atype
    

    def cal_dpmd(self):
        dp = DeepPot(self.path)
        e, f, v = dp.eval(self.cor, self.box, self.atype)
        # print(f"e: {e}\n, f: {f}\n, v: {v}\n")
        return [e[0][0], f[0][0], v[0][0]]
    
    def cal_fp_predictor(self, pro):
        res= self.cal_dpmd()
        ret = ''
        if 'energy' in pro:
            ret += f'energy: {res[0]}. '
        if 'force' in pro:
            ret += f'foece: {res[1]}. '  
        return ret