SG_PATH = '/z/abwilf/Standard-Grid'
import sys
sys.path.append(SG_PATH)
import standard_grid, os, time, pickle, json, pathlib
from os.path import join
from utils import *

def get_arguments():
    parser = standard_grid.ArgParser()
    
    # format: (name, type, default, help msg)
    args = [
        ('--batch_size', int, 32, 'The batch size.'),
        ('--lr', float, 0.001, 'Learning rate.'),
        ('--epochs', int, 25, 'The number of epochs.'),
    ]
    
    for param in args:
        parser.register_parameter(*param)
    args = parser.compile_argparse()
    return vars(args)

def main(args):
    '''ML model code goes here!'''
    print('Running model...')
    time.sleep(10)

    results = {
        'best_loss': .00123,
        'worst_loss': .0123,
    }

    # you can dump anything you'd like into out_dir.  It will be associated with this HP combination with a unique hash
    dummy_data = ar([ar([np.arange(10), np.arange(10) + 2, np.arange(10)-2]).T, ar([np.arange(4,14), np.arange(4,14) + 2, np.arange(4,14)-2]).T])

    plot_args = {
        'perfs': dummy_data,
        'x_label': 'Epochs',
        'y_label': 'Accuracy',
        'title': 'Accuracy Plot',
        'path': args['plot_path'],
        'labels': ['one', 'two'],
        'colors': ['blue', 'red'],
        'linestyles': ['-', '-.'],
    }
    plot_mtb(**plot_args)

    return results

if __name__ == '__main__':
    base_path = '/z/abwilf/Standard-Grid/example'
    out_dir = 'output/'
    mkdirp(out_dir)

    args = {
        **get_arguments(), # get hyperparams
        'cifar_path': join(base_path, 'cifar.pk'), # if you want to load data
        'plot_path': join(out_dir, 'accuracy_plot.png'), 
    }

    # our dummy ML model
    res = main(args)
    
    # this is where the results of your tests go - they will be cleaned up and made into a csv in "interpret"
    save_json(join(out_dir,'results.txt'), res)


