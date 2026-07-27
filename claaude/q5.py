"""
Add verify_time_invariance(self, x, k) to LTISystem. If y[n] is the output for x[n], then the output for x[n−k] must equal y[n−k]. Return the maximum absolute sample difference.
Formula
x[n] → y[n]   ⟹   x[n−k] → y[n−k]
return  max_n |T{x[n−k]}[n] − y[n−k]|
Method signature
def verify_time_invariance(self, x, k) -> float:
"""

from signal_lti import *

class q5(LTISystem):
    def verify_time_invariance(self, x, k):
        y = self.output(x)
        y_shifted = y.shift(k) # shift the output of original input

        x_shifted = x.shift(k)
        y2 = self.output(x_shifted) # output of the shifted input

        start = min(y_shifted.start_time, y2.start_time)
        end = max(y_shifted.end_time, y2.end_time)

        max_diff = 0.0
        for n in range(start, end + 1):
            diff = abs(y_shifted.get_value_at_time(n) - y2.get_value_at_time(n))
            max_diff = max(max_diff, diff)

        return max_diff

if __name__ == "__main__":
    h = DiscreteSignal(0, 1)
    h.x = np.array([1.0, 0.5])
    sys = q5(h)

    x = DiscreteSignal(0, 2)
    x.x = np.array([1.0, 2.0, 1.0])

    k = 2
    diff = sys.verify_time_invariance(x, k)
    print(f"Time-invariance difference (should be ~0): {diff}")
