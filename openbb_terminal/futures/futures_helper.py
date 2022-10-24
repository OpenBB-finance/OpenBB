from matplotlib.axes import Axes


def make_white(ax: Axes) -> None:
    """Make the labels and ticks white

    Parameters
    ----------
    ax: Axes
        The axes to make white

    """
    ax.xaxis.label.set_color("white")
    ax.tick_params(axis="x", colors="white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(axis="y", colors="white")
