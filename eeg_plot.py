import numpy as np


class EEGPlot:
    def __init__(self):
        self.max_x_lim = 6.0
        self.scale_factor = 0.0004
        self.y_tick_pos = []

    def set_max_x_lim(self, x_lim: int):
        self.max_x_lim = x_lim

    def create_axes(self, fig, scale):

        self.scale_factor = scale * 1e-6 * self.max_x_lim

        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(0, self.max_x_lim)
        ax.set_ylim(-self.scale_factor, 22 * self.scale_factor)

        return ax

    def label_figure(self, axes, channel_names):
        # label the last axes
        axes.set_xlabel("time/s")
        # give each axes a y-label corresponding to teh channel
        # or bipolar montage pair name
        self.y_tick_pos = [i * self.scale_factor for i in range(len(channel_names))]

        axes.set_yticks(self.y_tick_pos)
        axes.set_yticklabels(channel_names)

        # disable yticks
        # axs.yaxis.set_major_locator(NullLocator())
        # axs.yaxis.set_minor_locator(NullLocator())

        return axes

    def plot_signal(self, raw_eeg, axes):
        """Plot EEG signal
        - Xticks should represent seconds
        """
        channel_names = raw_eeg.info["ch_names"]

        # label the axes
        axes = self.label_figure(axes, channel_names)
        s_freq = raw_eeg.info["sfreq"]

        # get the numpy array signal
        signal = raw_eeg.get_data()
        signal_length = signal.shape[-1]  # int(s_freq * 10)

        # in samples
        t = np.linspace(0, signal_length - 1, signal_length) / s_freq

        for i in range(len(channel_names)):
            y = i * self.scale_factor
            axes.axhline(y=y, linestyle='--', linewidth=0.5, alpha=0.4, color='black')

        # just plot on each exes for now
        for i in range(signal.shape[0]):
            axes.plot(t, i * self.scale_factor + signal[i, :signal_length], linewidth=1)
