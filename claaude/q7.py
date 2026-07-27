"""
Add step_response(self, n_start, n_end) to LTISystem. Construct a unit step u[n] over [n_start, n_end] (= 1 for n ≥ 0, else 0), compute and return s = T{u}. Also verify the first-difference property: s[n] − s[n−1] = h[n] for every n in h's stored range.
Formula
u[n] = 1 (n ≥ 0),   0 (n < 0)
s[n] = (u * h)[n]

First-difference property:
s[n] − s[n−1] = h[n]   for n in h's range

Method signature
def step_response(self, n_start, n_end) -> "DiscreteSignal":
    # also print max |s[n]−s[n−1] − h[n]| as verification

Sample I/O
h = first_diff = {h[0]=1, h[1]=−1},  u over [0, 6]
s[0]=1, s[1]=0, …, s[6]=0
s[0]−s[−1] = 1  = h[0]  ✓
s[1]−s[0]  = −1 = h[1]  ✓
(edge artefacts outside h's range are expected)
"""

from signal_lti import DiscreteSignal
from signal_lti import *

class q7(LTISystem):
    def step_response(self, n_start, n_end):
        u = DiscreteSignal(n_start, n_end)
        for n in range(max(0, n_start), n_end + 1):
            # u[n] = 1 for n ≥ 0, else 0
            u.set_value_at_time(n, 1.0)

        s = self.output(u)

        # s[n] − s[n−1] = h[n]   for n in h's range
        max_err = 0.0
        for n in self.h.times():
            first_diff = s.get_value_at_time(n) - s.get_value_at_time(n - 1)
            err = abs(first_diff - self.h.get_value_at_time(n))
            max_err = max(max_err, err)

        print(f"First-difference check: max |s[n]-s[n-1]-h[n]| = {max_err:.2e}")
        return s

def main():
    h = DiscreteSignal(0, 1)
    h.x = np.array([1.0, -1.0])
    sys = q7(h)
    
    print("Testing step response for u over [0, 6]")
    s = sys.step_response(0, 6)
    
    print("Output samples:")
    for n in range(0, 7):
        print(f"s[{n}] = {s.get_value_at_time(n)}")

if __name__ == "__main__":
    main()