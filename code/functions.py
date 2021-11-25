import seaborn as sns
import matplotlib.pyplot as plt

def my_hbarplot(x, y, data, xlabel=None, ylabel=None, title=None, ax=None):
    plot = sns.barplot(y = y, x = x, orient = 'h', data = data, palette='deep')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title, fontsize = 16)
    plt.bar_label(plot.containers[0], label_type='center')
    
def savefig(name):
    plt.savefig(fname = name, facecolor='white', bbox_inches='tight')
    
def ms_to_hrs(x):
    round(x / np.timedelta64(1, 'h'),1)