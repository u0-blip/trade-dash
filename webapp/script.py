import sys
import torch.nn as nn

sys.path.append('/home/peter/source/')
train_on_gpu = True
from tv_script import web_interface
from tv_script.helper import RNN

def wrap_script(name):
    name = name + ':'
    return web_interface.get_script(name)
