SG_PATH = '/z/abwilf/temp/Standard-Grid'
import sys
sys.path.append(SG_PATH)
import standard_grid
from utils import *
import pickle

if __name__=="__main__":
    hash_in = sys.argv[1]
    grid=pickle.load(open(f'.{hash_in}.pkl',"rb"))
    grid.get_status()
