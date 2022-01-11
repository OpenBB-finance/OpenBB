"""Helper classes."""
__docformat__ = "numpy"

import matplotlib
import matplotlib.pyplot as plt


class LineAnnotateDrawer:
    """Line drawing class."""

    def __init__(self, ax: matplotlib.axes = None):
        self.ax = ax

    def draw_lines_and_annotate(self):
        """Draw lines."""
        print("Click twice for annotation.\nClose window to keep using terminal.\n")

        while True:
            xy = plt.ginput(2)
            # Check whether the user has closed the window or not
            if not plt.get_fignums():
                print("")
                return

            if len(xy) == 2:
                x = [p[0] for p in xy]
                y = [p[1] for p in xy]

                if (x[0] == x[1]) and (y[0] == y[1]):
                    txt = input("Annotation: ")
                    self.ax.annotate(txt, (x[0], y[1]), ha="center", va="center")
                else:
                    self.ax.plot(x, y)

                self.ax.figure.canvas.draw()
