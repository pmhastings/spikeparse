import matplotlib.pyplot as plt
import numpy as np

SIM_LENGTH = 1000
num_items = 10

def plot_spiketrains(label, segment):
    for spiketrain in segment.spiketrains:
        y = np.ones_like(spiketrain) * spiketrain.annotations['source_index']  # ['source_id']
        plt.plot(spiketrain, y, '.')
        plt.ylabel(label)    # segment.name)
        plt.setp(plt.gca().get_xticklabels(), visible=False)
    plt.ylim([0,num_items-1])

# def plot_signal(signal, index, colour='b'):
#     label = "Neuron %d" % signal.annotations['source_ids'][index]
#     plt.plot(signal.times, signal[:, index], colour, label=label)
#     plt.ylabel("%s (%s)" % (signal.name, signal.units._dimensionality.string))
#     plt.setp(plt.gca().get_xticklabels(), visible=False)
#     plt.legend()

def plotMemSpikes(pops):

    fig_settings = {
        'lines.linewidth': 0.5,
        'axes.linewidth': 0.5,
        'axes.labelsize': 'small',
        'legend.fontsize': 'small',
        'font.size': 8
    }

    plt.rcParams.update(fig_settings)
    plt.figure(1, figsize=(6,8))

    n_panels = len(pops)
    panel = 1
    for pop in pops:
        data = pop.get_data()
        plt.subplot(n_panels, 1, panel)
        plot_spiketrains(pop.label, data.segments[0])
        panel += 1
    plt.xlabel("time (%s)" % data.segments[0].spiketrains[0].times.units._dimensionality.string)
    plt.setp(plt.gca().get_xticklabels(), visible=True)
    plt.xlim([0,SIM_LENGTH])

    plt.show()
