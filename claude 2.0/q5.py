"""Motivation
A system can fail linearity while being time-invariant, or fail time-invariance while being linear:

  System C:  y_C[n] = x[n]²            — time-invariant, but nonlinear
  System D:  y_D[n] = x[n] · cos(πn/4) — linear, but time-varying

You will apply generic tests (callable-based, same pattern as A1/A2) to confirm both failures.
Given
x₁[n] :  n = −2 .. 2,   values = [1, 0, 2, −1, 3]
x₂[n] :  n = −1 .. 3,   values = [2, −3, 0, 1, 1]
a = 2,  b = −3,  k = 3
Tasks
Implement test_linearity(apply_system, x1, x2, a, b) returning max |T{ax₁+bx₂} − aT{x₁} − bT{x₂}|. Must accept any callable, not only LTISystem.
Implement test_time_invariance(apply_system, x, k) returning max |T{x[n−k]} − y[n−k]|.
Implement system_c(x) computing x[n]² sample by sample using DiscreteSignal.
Implement system_d(x) computing x[n]·cos(πn/4) using DiscreteSignal and numpy.
Run both tests on System C and System D using x₁, x₂, a, b, k; print all four max-difference values.
Plot the output of System C and System D for input x₁ as stem plots.
In a print statement, state which property each system fails and give a one-sentence mathematical reason for each.
Key signatures
def test_linearity(apply_system, x1, x2, a, b) -> float:
    ...

def test_time_invariance(apply_system, x, k) -> float:
    ...

def system_c(x) -> DiscreteSignal:
    ...

def system_d(x) -> DiscreteSignal"""

# from PIL import GimpPaletteFile
from signal_lti import *
import numpy as np
import matplotlib.pyplot as plt

def make_signal(start, end, values):
    sig = DiscreteSignal(start, end)
    for i, v in enumerate(values):
        sig.set_value_at_time(start + i, v)
    return sig

def max_diff(a, b):
    start = min(a.start_time, b.start_time)
    end   = max(a.end_time,   b.end_time)
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))

def test_linearity(apply_system, x1, x2, a, b):
    x1_scaled = x1.multiply(a)
    x2_scaled = x2.multiply(b)
    x_sum = x1_scaled.add(x2_scaled)
    ls = apply_system(x_sum)
    
    y1 = apply_system(x1).multiply(a)
    y2 = apply_system(x2).multiply(b)
    rs = y1.add(y2)

    return max_diff(ls, rs)

def test_time_invariance(apply_system, x, k):
    y_shifted = apply_system(x).shift(k)
    y2        = apply_system(x.shift(k))
    return max_diff(y_shifted, y2)


def system_c(x):
    # y_C[n] = x[n]^2 — time-invariant, nonlinear
    result = DiscreteSignal(x.start_time, x.end_time)
    for t in x.times():
        result.set_value_at_time(t, x.get_value_at_time(t) ** 2)
    return result

def system_d(x):
    # y_D[n] = x[n] * cos(pi*n/4) — linear, time-varying
    result = DiscreteSignal(x.start_time, x.end_time)
    for t in x.times():
        result.set_value_at_time(t, x.get_value_at_time(t) * np.cos(np.pi * t/4))
    return result


def main():
    x1 = make_signal(-2, 2, [1, 0, 2, -1, 3])
    x2 = make_signal(-1, 3, [2, -3, 0, 1, 1])
    a, b, k = 2, -3, 3

    print("System C: y_C[n] = x[n]^2")
    print(f"  Linearity diff:       {test_linearity(system_c, x1, x2, a, b):.6f}  (> 0 -> fails)")
    print(f"  Time-invariance diff: {test_time_invariance(system_c, x1, k):.6f}  (~ 0 -> passes)")

    print("\nSystem D: y_D[n] = x[n] * cos(pi*n/4)")
    print(f"  Linearity diff:       {test_linearity(system_d, x1, x2, a, b):.6f}  (~ 0 -> passes)")
    print(f"  Time-invariance diff: {test_time_invariance(system_d, x1, k):.6f}  (> 0 -> fails)")

    print("\nConclusion:")
    print("  System C fails linearity: T{ax} = a^2 x^2 != a * x^2 = a * T{x}.")
    print("  System D fails time-invariance: cos(pi*n/4) != cos(pi*(n-k)/4) in general.")

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), constrained_layout=True)
    ns = list(x1.times())
    axes[0].stem(ns, [system_c(x1).get_value_at_time(n) for n in ns]); axes[0].set_title("System C output: x₁[n]²")
    axes[1].stem(ns, [system_d(x1).get_value_at_time(n) for n in ns]); axes[1].set_title("System D output: x₁[n]·cos(πn/4)")
    for ax in axes: ax.set_xlabel("n"); ax.grid(True, alpha=0.35)
    fig.savefig("q5_nonlti.png", dpi=150); plt.close(fig)
        
if __name__ == "__main__":
    main()