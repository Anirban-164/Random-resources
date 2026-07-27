"""Motivation
Any discrete-time signal decomposes uniquely into an even part and an odd part:

  x_e[n] = (x[n] + x[−n]) / 2     (even:  x_e[n] =  x_e[−n])
  x_o[n] = (x[n] − x[−n]) / 2     (odd:   x_o[n] = −x_o[−n])
  x[n]   = x_e[n] + x_o[n]

Both parts follow directly from DiscreteSignal operations already in your class.
Given
x[n] :  n = −3 .. 3,   values = [1, −2, 3, 0, 1, 2, −1]
Observation window:  n = −3 .. 3
Tasks
Implement even_part(x) using x.add(x.reverse()).multiply(0.5).
Implement odd_part(x) using x.subtract(x.reverse()).multiply(0.5). (Add subtract to DiscreteSignal if not already present.)
Print x_e[n] and x_o[n] sample by sample for n = −3 .. 3.
Verify reconstruction: compute and print max |x_e[n] + x_o[n] − x[n]| over n = −3 .. 3.
Verify even symmetry: compute and print max |x_e[n] − x_e[−n]| ≈ 0.
Verify odd anti-symmetry: compute and print max |x_o[n] + x_o[−n]| ≈ 0.
Plot x[n], x_e[n], and x_o[n] as stem plots.
In a print statement, conclude that the decomposition is exact and the symmetry properties hold."""


from signal_lti import *
import numpy as np
import matplotlib.pyplot as plt

def make_signal(start, end, values):
    sig = DiscreteSignal(start, end)
    for i, v in enumerate(values):
        sig.set_value_at_time(start + i, v)
    return sig

def even_part(x):
    r = x.reverse()
    return x.add(r).multiply(0.5)

def odd_part(x):
    r = x.reverse().multiply(-1)
    return x.add(r).multiply(0.5)

def max_diff_in_range(a, b, start, end):
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))

def main():
    x = make_signal(-3, 3, [1, -2, 3, 0, 1, 2, -1])

    x_e = even_part(x)
    x_o = odd_part(x)

    print(f"{'n':>4}  {'x[n]':>8}  {'x_e[n]':>10}  {'x_o[n]':>10}")
    for n in range(-3, 4):
        print(f"{n:4d}  {x.get_value_at_time(n):8.4f}  "
            f"{x_e.get_value_at_time(n):10.4f}  "
            f"{x_o.get_value_at_time(n):10.4f}")

    reconstruction_err = max_diff_in_range(x_e.add(x_o), x, -3, 3)
    even_sym_err = max(abs(x_e.get_value_at_time(n) - x_e.get_value_at_time(-n)) for n in range(-3, 4))
    odd_sym_err  = max(abs(x_o.get_value_at_time(n) + x_o.get_value_at_time(-n)) for n in range(-3, 4))

    print(f"\nReconstruction error  max|x_e+x_o - x|  : {reconstruction_err:.2e}")
    print(f"Even symmetry error   max|x_e[n]-x_e[-n]|: {even_sym_err:.2e}")
    print(f"Odd  symmetry error   max|x_o[n]+x_o[-n]|: {odd_sym_err:.2e}")
    print("Conclusion: The even/odd decomposition is exact and all symmetry properties hold.")

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), constrained_layout=True)
    ns = list(range(-3, 4))
    axes[0].stem(ns, [x.get_value_at_time(n)   for n in ns]); axes[0].set_title("x[n]")
    axes[1].stem(ns, [x_e.get_value_at_time(n) for n in ns]); axes[1].set_title("Even part x_e[n]")
    axes[2].stem(ns, [x_o.get_value_at_time(n) for n in ns]); axes[2].set_title("Odd part x_o[n]")
    for ax in axes: ax.set_xlabel("n"); ax.grid(True, alpha=0.35)
    fig.savefig("q3_even_odd.png", dpi=150); plt.close(fig)


if __name__ == '__main__':
    main()