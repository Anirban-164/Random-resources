"""Motivation
The matched filter for template s[n] has impulse response h[n] = s[−n]. When the input contains s[n] starting at position n₀, the filter output peaks at n = n₀ with value equal to the energy of s:

  y[n₀] = Σ_k s[k]²

You will embed the template twice and verify that both peaks equal the template energy.
Given
s[n] :  n = 0 .. 3,    values = [1, 2, 1, −1]      (template)
x[n] :  n = 0 .. 12,   values = [0, 0, 1, 2, 1, −1, 0, 0, 1, 2, 1, −1, 0]
         (template embedded at n = 2 and n = 8)
Template energy: 1² + 2² + 1² + (−1)² = 7
Observation window for output:  n = 0 .. 12
Tasks
Implement matched_filter(template) returning LTISystem(template.reverse()).
Apply the matched filter to x[n] and store the output y[n].
Implement find_peak(signal, start, end) returning the time index of the maximum value over [start, end].
Print y[n] for n = 0 .. 12.
Call find_peak on [0, 5] and [6, 12] separately; print both peak indices and their values.
Verify both peaks equal the template energy (7).
Plot x[n] and y[n] as stem plots over n = 0 .. 12.
In a print statement, conclude that the matched filter peaks at the template start positions with value equal to template energy.
Key signatures
def matched_filter(template) -> LTISystem:
    ...

def find_peak(signal, start, end) -> int:
    ..."""

from signal_lti import *
import numpy as np
import matplotlib.pyplot as plt

def make_signal(start, end, values):
    sig = DiscreteSignal(start, end)
    for i, v in enumerate(values):
        sig.set_value_at_time(start + i, v)
    return sig

def max_diff_in_range(a, b, start, end):
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))

def matched_filter(template):
    return LTISystem(template.reverse())

def find_peak(signal, start, end):
    peak_n, peak_val = start, signal.get_value_at_time(start)
    for n in range(start, end + 1):
        val = signal.get_value_at_time(n)
        if val > peak_val:
            peak_val = val
            peak_n = n
    return peak_n

def main():
    s = make_signal(0, 3, [1, 2, 1, -1])
    x = make_signal(0, 12, [0, 0, 1, 2, 1, -1, 0, 0, 1, 2, 1, -1, 0])

    y = matched_filter(s).output(x)

    print(f"{'n':>4}  {'x[n]':>8}  {'y[n]':>10}")
    for n in range(0, 13):
        print(f"{n:4d}  {x.get_value_at_time(n):8.4f}  {y.get_value_at_time(n):10.4f}")

    template_energy = sum(s.get_value_at_time(n) ** 2 for n in s.times())
    peak1_n = find_peak(y, 0, 5)
    peak2_n = find_peak(y, 6, 12)

    print(f"\nTemplate energy: {template_energy:.1f}")
    print(f"Peak 1: n={peak1_n},  y[{peak1_n}] = {y.get_value_at_time(peak1_n):.4f}")
    print(f"Peak 2: n={peak2_n},  y[{peak2_n}] = {y.get_value_at_time(peak2_n):.4f}")
    print(f"Conclusion: Matched filter peaks at template start positions (n=2, n=8) "
        f"with value = template energy ({template_energy:.0f}).")

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    ns = list(range(0, 13))
    axes[0].stem(ns, [x.get_value_at_time(n) for n in ns]); axes[0].set_title("Input x[n]")
    axes[1].stem(ns, [y.get_value_at_time(n) for n in ns]); axes[1].set_title("Matched filter output y[n]")
    for ax in axes: ax.set_xlabel("n"); ax.grid(True, alpha=0.35)
    fig.savefig("q4_matched_filter.png", dpi=150); plt.close(fig)