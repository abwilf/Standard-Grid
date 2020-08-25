import standard_grid
import time
import os

if __name__=="__main__":
	for i in range (100):
		print ("DO NOT RUN THIS ON MUTLICOMP ATLAS CLUSTER! USE CONTROLLED! ")
	grid=standard_grid.Grid("../../../ml_code_json.py","./results/")

	grid.register('bs', [32,64])
	grid.register('lr_net', [0.001,0.01,0.0001])
	grid.register('epochs', [5000,6000,100000000000])

	grid.generate_grid()
	grid.shuffle_grid()

	grid.generate_shell_instances(prefix="python ",postfix="")
	grid.create_runner(num_runners=None,runners_prefix=["sbatch -p gpu_low -c 1 --gres=gpu:1"])


