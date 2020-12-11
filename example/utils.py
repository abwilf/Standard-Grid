import pathlib, os,json
import matplotlib.pyplot as plt
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

def save_json(file_stub, obj):
    filename = file_stub
    with open(filename, 'w') as f:
        json.dump(obj, f, cls=NumpyEncoder, indent=4)

def ar(a):
    return np.array(a)

def mkdirp(dir_path):
    if not os.path.isdir(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True)

def get_mtb(arr):
    '''take in arr of shape [num_epochs, num_trials], give back three tuple with means, tops, bots each of shape (num_epochs,)'''
    arr = ar(arr)
    if len(arr.shape) == 1:
        return arr, arr, arr    
    means = np.mean(arr, axis=-1)
    stds = np.std(arr, axis=-1)
    tops = means + stds
    bots = means - stds
    return means, tops, bots

def plot_mtb(perfs, x_label, y_label, title, path, x_ranges=None, labels=['model'], colors=['blue'], x_ticklabels=None, linestyles=None, ylim=None, xlim=None, subtitle=None, y_formatter=None, x_formatter=None):
    '''
    Plots individual lines, or clouds with mean, +- 1 std

    perfs: ar of shape (lines, x, trials), (x, trials), or (x,)
    x_ranges: (lines, x), (x,) or inferred as np.arange(x); dimensionality of x axis
    labels: list of shape (lines,)
    colors: list of shape (lines,); default=['blue']
    '''
    perfs = ar(perfs)
    perf_shape = len(perfs.shape)
    if perf_shape == 1:
        perfs = [np.expand_dims(perfs, axis=-1)]
    
    elif perf_shape == 2:
        perfs = [perfs]
    
    if labels is None:
        labels = ['']*len(perfs)
        legend = False
    else:
        legend = True
    
    x_ranges = np.arange(perfs[0].shape[-2]) if x_ranges is None else x_ranges
    x_ranges = ar(x_ranges)
    if len(x_ranges.shape) == 1:
        x_ranges = [x_ranges]*len(perfs)

    linestyles = ['-']*len(perfs) if linestyles is None else linestyles

    if labels is not None:
        assert len(labels) == len(colors) == len(perfs) == len(linestyles), f'Number of lines must be the same across perfs, labels, colors, and linestyles.  Currently, number of lines in perfs: {len(perfs)}; labels: {len(labels)}; colors: {len(colors)}; linestyles: {len(linestyles)}'
    else:
        assert len(labels) == len(colors) == len(perfs) == len(linestyles), f'Number of lines must be the same across perfs, labels, colors, and linestyles.  Currently, number of lines in perfs: {len(perfs)}; labels: {len(labels)}; colors: {len(colors)}; linestyles: {len(linestyles)}'

    perfs = [get_mtb(perf) for perf in perfs]
    
    fig, ax = plt.subplots()
    for perf, label, color,linestyle, x_range in zip(perfs, labels, colors, linestyles, x_ranges):
        means, tops, bots = perf
        if len(x_range) > len(means):
            x_range = x_range[:len(means)]
        plt.plot(x_range, means, color=color, label=label, linestyle=linestyle)
        plt.plot(x_range, tops, color=color, alpha=.1)
        plt.plot(x_range, bots, color=color, alpha=.1)
        plt.fill_between(x_range, means, tops, color=color, alpha=.05)
        plt.fill_between(x_range, means, bots, color=color, alpha=.05)

    ax.set_title(title)
    if x_ticklabels is not None:
        ax.set_xticks(x_range)
        ax.set_xticklabels(x_ticklabels)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if ylim is not None:
        plt.ylim(bottom=0)
    if xlim is not None:
        plt.xlim(left=xlim[0],right=xlim[1])
    if y_formatter is not None:
        ax.yaxis.set_major_formatter(y_formatter)
    if x_formatter is not None:
        ax.xaxis.set_major_formatter(x_formatter)
        
    ax.spines['top'].set_visible(False), ax.spines['right'].set_visible(False)
    if legend:
        plt.legend(loc="lower right")
    plt.savefig(path, bbox_inches='tight', dpi=300)
    print(f'Saving {title} plot to {path}')
    plt.show()