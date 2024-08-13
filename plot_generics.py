import matplotlib.pyplot as plt
import matplotlib

def plot_generic(title, xlabel, ylabel):
    plt.rcParams.update({'font.size': 13})
    fig, ax = plt.subplots(dpi=600)

    ax.minorticks_on()
    ax.tick_params(direction='in', which='both')
    ax.grid(visible=True, axis='both', which='major', linestyle='--', 
            alpha=0.5)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    
    return fig, ax


def line(ax, x, y, label, colour='none', alpha=1, linewidth=0.5):
    if colour == 'none':
        ax.plot(x, y, label=label, alpha=alpha, linewidth=linewidth)
        return
    
    ax.plot(x, y, label=label, color=colour, alpha=alpha, linewidth=linewidth)
    
    
def show(ax):
    ax.legend()

    plt.show()
    

def save(ax, fname):
    ax.legend()
    
    plt.savefig(fname)
