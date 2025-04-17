from deepmd.infer import calc_model_devi
from deepmd.infer import DeepPot as DP
import numpy as np

def data_relaticity(coord=[[1, 0, 0], [0, 0, 1.5], [1, 0, 3]], cell=10 * np.ones(3), atype = [1, 0, 1], model_list=["model.ckpt.pt"]):

    models = []
    for model in model_list:
        models.append(DP(f"{model}"))

    model_devi = calc_model_devi(coord, cell, atype, models)

    return model_devi
