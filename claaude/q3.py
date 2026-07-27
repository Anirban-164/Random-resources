"""
Add is_causal(self) to LTISystem. An LTI system is causal when h[n] = 0 for all n < 0 — meaning the output at time n depends only on present and past inputs, never future ones.
Formula
Causal  ⟺  h[n] = 0   for all n < 0
Method signature
def is_causal(self) -> bool:
"""

from signal_lti import *

class q3(DiscreteSignal):
    def is_causal(self):
        if self.start_time >= 0:
            return True

        for(t, x) in self.nonzero_samples():
            if t>= 0:
                return True
            if np.abs(x)>0:
                return False


def main():
    x = q3(1, 2)
    x.set_value_at_time(1, 2)
    x.set_value_at_time(2, 3)
    print(x.is_causal())
    
    y = q3(-1, 2)
    y.set_value_at_time(-1, 2)
    y.set_value_at_time(0, 2)
    y.set_value_at_time(1, 3)
    y.set_value_at_time(2, 3)
    print(y.is_causal())

    z = q3(-1, 2)
    z.set_value_at_time(-1, 0)
    z.set_value_at_time(0, 2)
    z.set_value_at_time(1, 3)
    z.set_value_at_time(2, 3)
    print(z.is_causal())

if __name__ == "__main__":
    main()
