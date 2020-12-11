# Standard-Grid Extension
The goal of this repository is not to replace the wonderful [Standard Grid] (https://github.com/A2Zadeh/Standard-Grid), written by [Amir Zadeh](https://www.amir-zadeh.com/).  Amir's implementation is intentionally spare; in this repo, I provide some more structure and functionality around it, so that members of the CHAI lab can get up and running with the Grid in a few easy steps.

## What is the Standard-Grid?  Why should I use it?
The Standard-Grid is meant to allow you to take a standalone model program (e.g., `model.py`) that takes hyperparameters from standard input and quickly and reliably runs and collates the results of large grid searches, parallelized within and across GPU's.  Once I saw the system in action, I was hooked.  I hope you will be too!  All credit to Amir for its design, implementation and maintenance.

## Requirements for the Example
This example requires `python3` with `matplotlib`, `numpy`, and `requests` installed.  If you use conda (sorry to proselytize!), this is as simple as
```
conda create -n env python=3.7
conda activate env
pip install matplotlib numpy requests
```

## Example
Imagine you want to build a standalone model file and run it using command line arguments. In `example/model.py` you can find a simple implementation. To get it running, simply
1. `cd example`
2. Replace all instances of `SG_PATH` in `example/` with the path to your `Standard-Grid` folder
3. `python3 model.py`

You should see the following output...
```
Running model...
Saving Accuracy Plot plot to output/accuracy_plot.png
```

You'll notice that the model has written its output to `./output/`, including our plot and a `results.txt` file.

Now, imagine you want to execute a grid search over all the hyperparameters in `hp.py`
```python
hp = {
    'batch_size': [32,64,128],
    'epochs': list(np.arange(20,50,10)),
    'lr': [1e-2,1e-3],
}
```

WARNING: the following will use 3 gpus. You can change this in `generate.py`

First, you'll **create a grid**.  This is an object stored in `./{grid_hex}`, where `grid_hex` is a hash of your hyperparameters.  I shorten this hash for readability, though with large numbers of tests this may lead to a collision; if it does, you will see an eror at "compile time" - i.e., you'll see the error when grid is created in `generate.py`, not when the individual tests are run. This is a great feature. If you see an error, increase `hash_len` in `generate.py` until the collision disappears. To create the grid in this example, run
```
python3 generate.py
```

You should see some logging output, followed by
```
hash='c542'

root=/z/abwilf/Standard-Grid/example
attempt='0'
cd $root/results/${hash}/central/attempt_${attempt}/
chmod +x main.sh
./main.sh
cd $root
p status.py ${hash}
p interpret.py ${hash}
```

Copy and paste this output into your terminal to start the grid search.  You'll see that a few jobs are immediately running.
```
Running 6aea
Running 4e05
Running a2b8
```

If you check out `nvidia-smi`, you'll see that all three gpus are being utilized.
```
...
|    0   N/A  N/A     26249      C   python                           1439MiB |
|    1   N/A  N/A     22780      C   python                           1475MiB |
|    2   N/A  N/A     23799      C   python                           1475MiB |
```

If you want to check the status while your programs are running, you can jump over to another screen or shell and type
```
hash='c542'
python3 status.py $hash
```

If your search is still running, you'll see an output like this, giving you some helpful information:
```
##### Progress #####
Completed: 6
Remaining: 12
Total: 18
Time spent: 00:00:25 (per test: 00:00:04)
Time remaining: 00:00:50
ETA: Fri 04:31:14 PM
```

If your search has finished, you'll see an output more like this:
```
[2020-12-11 23:10:33.967] | Status  | Not started:      0.00%
[2020-12-11 23:10:33.968] | Status  | Unfinished*:      0.00%
[2020-12-11 23:10:33.968] | Status  | Finished:         100.00%
[2020-12-11 23:10:33.968] | Status  | Failed:           0.00%
Runtime: 1 mins
Total completed: 18
Time per test: 0.07 mins
```

When your search has finished, your results will be in `./results/{hash}/instances`.  Each run has its own hash, representing a different hyperparameter combination. If you look in one of these subdirectories, you will find the `output` directory we expect along with the `accuracy_plot.png` and `results.txt` for that run.

You'll see that your results have also been collated into a csv file.
```
[2020-12-11 23:10:18.343] | Success | Results gathered in results/8cee/csv_results.csv
```

This csv has as columns all the hyperparameters and keys in the `results.txt` objects.  I usually process this using `pandas`, remove `STD_GRID_` from the columns (`df.rename(columns={k: k.replace('STDGRID_', '') for k in df.columns})`), and sort by some attribute (e.g., `df.sort_values(by=['best_loss'], ascending=True)`) before creating summary plots. Our example `csv_results.csv` looks like:
```
best_loss,worst_loss,STDGRID_batch_size,STDGRID_epochs,STDGRID_lr,STDGRID_command_hex,STDGRID_grid_hex
0.00123,0.0123,128,40,0.001,b358,8cee
0.00123,0.0123,128,20,0.01,6d46,8cee
...
```

## Notes and Extras
1. To get this working with your code, you'll need to replace the following line in `generate.py` with the correct working directory where your code is stored
```
root=/path/to/your/proj
```
2. `results.txt` must have same columns across each element in a single grid search, otherwise the `results.txt` files will not be collated into a single csv.
3. If you need to stop a search in progress, I don't know of an incredibly elegant way (though there probably is one).  If you exit the program while `main.sh` is running, the workers will still run in the background.  I usually insert an error into `model.py` (e.g., an undefined `hi`), `kill` the processes currently running by finding it with `nvidia-smi` or `ps ax | grep python`, and watch as all the rest of the queued processes quickly fail.
4. I often find that I need to remove previous grid searches I've run, and it's a pain to do this by hand each time.  I wrote myself a helper function, and put it in my `~./bashrc`.  To get it to work, simply add this to your `bashrc`, `source ~/.bashrc`, and run it with `rmhash $hash` from the relevant directory.  Be careful! I accidentally wiped out the wrong folder once.

```bash
function rmhash {
    if [ $1 ]
    then
    echo "Cleaning up hash" $1
    rm -rf results/$1
    rm .$1.pkl
    echo "Clean!"
    else
    echo "No hash to clean up!"
    fi
}
```

5. I don't like waiting around for my code to finish, so in addition to the ETA you'll find in `status.py`, I wrote myself a function to email me when my program has finished. It uses [mailgun](https://www.mailgun.com/), which is free up to large number of emails. If you want to leverage this part of the code, get a `mailgun_secrets.json` file with your API key and modify the code in `generate.py` to point to it.  Then replace `email_args=None` with the correct object and you'll be ready to go.

