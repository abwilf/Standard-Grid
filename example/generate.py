SG_PATH = '/z/abwilf/temp/Standard-Grid'
import sys
sys.path.append(SG_PATH)
import standard_grid
from utils import *
from hp import hp

if __name__=="__main__":
    num_chars = 4 # the number of characters in each hash.  if running lots of tests, may have collision if too few chars.  elif running few tests, can be nice to have smaller identifying strings
    grid = standard_grid.Grid('./model.py','./results/', num_chars=num_chars)

    for k,v in hp.items():
        grid.register(k,v)

    grid.generate_grid()
    grid.shuffle_grid()
    grid.generate_shell_instances(prefix='python ',postfix='')
    
    # Breaks the work across num_gpus GPUs, num_parallel jobs on each gpu
    num_gpus = 3
    num_parallel = 1
    hash_out = grid.create_runner(num_runners=num_gpus,runners_prefix=['CUDA_VISIBLE_DEVICES=%d sh'%i for i in range(num_gpus)],parallel=num_parallel)

    print(f'''
# update shell params

hash='{hash_out}'

root='/z/abwilf/temp/Standard-Grid/example'
attempt='0'
cd $root/results/${{hash}}/central/attempt_${{attempt}}/
chmod +x main.sh
./main.sh
cd $root
p status.py ${{hash}}
p interpret.py ${{hash}}

    ''')


