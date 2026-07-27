"""
Add cross_correlate(self, other) to DiscreteSignal, returning Rxy as a new DiscreteSignal. Cross-correlation measures the similarity of two signals at different lags m. Do not use np.correlate or any built-in convolution.
Formula
R_xy[m] = Σ_k x[k] · y[k+m]

Output range:  m ∈ [y.start − x.end,  y.end − x.start]

Key identity:  R_xy[m] = (x[−n] * y[n])[m]
Method signature
def cross_correlate(self, other) -> "DiscreteSignal":
"""

from signal_lti import LTISystem
from signal_lti import DiscreteSignal
from signal_lti import *

class q6(DiscreteSignal):
    def cross_correlate(self, other):
        # R_xy[m] = (x[−n] * y[n])[m]
        x_reversed = self.reverse()
        sys = LTISystem(x_reversed)
        return sys.output(other)



if __name__ == "__main__":
    x = DiscreteSignal(0, 2)
    x.x = np.array([1.0, 2.0, 1.0])

    y = DiscreteSignal(0, 1)
    y.x = np.array([1.0, 1.0])

    r_xy = q6.cross_correlate(x, y)
    for i, values in enumerate(r_xy.values):
        print(r_xy.start_time + i, ': ', values)