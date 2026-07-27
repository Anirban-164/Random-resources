"""
Add two methods to DiscreteSignal: energy() returns the total signal energy E, and l2_norm() returns its square root. These appear in SNR calculations and filter analysis.
Formula
E  =  Σ_n |x[n]|²
L₂ =  √E
"""

from signal_lti import *

class q1(DiscreteSignal):
    def energy(self):
        co_eff = self.values ** 2
        return np.sum(co_eff)

    def l2_norm(self):
        return np.sqrt(self.energy())

def main():
    x = q1(0, 2)
    x.set_value_at_time(0, 1)
    x.set_value_at_time(1, 2)
    x.set_value_at_time(2, 3)
    print(x.energy())
    print(round(x.l2_norm(), 4))


if __name__ == "__main__":
    main()
