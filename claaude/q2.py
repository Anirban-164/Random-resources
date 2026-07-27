"""
Add subtract(self, other) to DiscreteSignal, returning x[n] − other[n] over the union of both time ranges. Then refactor max_absolute_difference() in main.py to use it.
Formula
z[n] = x[n] - y[n]
Method signature
def subtract(self, other) -> "DiscreteSignal":
"""

from signal_lti import *

class q2(DiscreteSignal):
    def subtract(self, other):
        start_time = min(self.start_time, other.start_time)
        end_time = max(self.end_time, other.end_time)

        result = DiscreteSignal(start_time, end_time)
        for t in result.times():
            val = self.get_value_at_time(t) - other.get_value_at_time(t)

            result.set_value_at_time(t, val)
        return result

def main():
    x = q2(0, 3)
    y = DiscreteSignal(0, 1)

    x.set_value_at_time(0, 1)
    x.set_value_at_time(1, 2)
    x.set_value_at_time(2, 3)
    y.set_value_at_time(0, 2)
    y.set_value_at_time(1, 2)

    z = (x.subtract(y))
    print(z.values)


if __name__ == "__main__":
    main()
