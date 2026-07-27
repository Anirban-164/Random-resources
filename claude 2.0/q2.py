# from practice.convo2 import LTISystem
from signal_lti import *
import numpy as np
import matplotlib.pyplot as plt

"""
Motivation
Convolution is commutative: (x * h)[n] = (h * x)[n]. Treating x as the impulse response and h as input must give the same output as the standard arrangement.

You will verify this identity numerically over the full union output range.
Given
x[n] :  n = −1 .. 3,   values = [2, 1, −1, 3, 0]
h[n] :  n = 0 .. 2,    values = [1, 0.5, −0.5]
Union output range:  n = −1 .. 5
Tasks
Implement convolve_signals(a, b) using LTISystem(a).output(b).
Compute y1 = convolve_signals(x, h) and y2 = convolve_signals(h, x).
Implement max_absolute_difference_in_range(a, b, start, end).
Print y1[n] and y2[n] side by side for n = −1 .. 5.
Plot y1[n] and y2[n] as stem plots on the same observation window.
Compute and print the maximum absolute difference over the union output range.
In a print statement, conclude that convolution is commutative.
"""

def make_signal(start, end, values):
    sig = DiscreteSignal(start, end)
    for i, val in enumerate(values):
        sig.set_value_at_time(i + start, val)
    return sig


def max_absolute_difference_in_range(a, b, start, end):
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))

def main():
    x = make_signal(-1, 3, [2, 1, -1, 3, 0])
    h = make_signal(0, 2, [1, 0.5, -0.5])

    sys1 = LTISystem(x)
    y1  = sys1.output(h)

    sys2 = LTISystem(h)
    y2 = sys2.output(x)

    obs_start = min(y1.start_time, y2.start_time)
    obs_end   = max(y1.end_time,   y2.end_time)

    print(f"{'n':>4}  {'y1 = x*h':>12}  {'y2 = h*x':>12}")
    for n in range(obs_start, obs_end + 1):
        print(f"{n:4d}  {y1.get_value_at_time(n):12.4f}  {y2.get_value_at_time(n):12.4f}")

    diff = max_absolute_difference_in_range(y1, y2, obs_start, obs_end)
    print(f"\nMax absolute difference: {diff:.2e}")
    print("Conclusion: Convolution is commutative — x*h = h*x holds exactly.")

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    ns = list(range(obs_start, obs_end + 1))
    axes[0].stem(ns, [y1.get_value_at_time(n) for n in ns]); axes[0].set_title("y1 = x * h  (LTISystem(x).output(h))")
    axes[1].stem(ns, [y2.get_value_at_time(n) for n in ns]); axes[1].set_title("y2 = h * x  (LTISystem(h).output(x))")
    for ax in axes: ax.set_xlabel("n"); ax.grid(True, alpha=0.35)
    fig.savefig("q2_commutativity.png", dpi=150); plt.close(fig)

if __name__ == '__main__':
    main()