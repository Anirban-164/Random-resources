from concurrent import interpreters
from numpy._typing import _nested_sequence
import numpy as np
import matplotlib.pyplot as plt

"""
Let the base signal be x(t) = e^(−t) · sin(t), defined on [−π, π], zero outside.
Implement two functions:
even_signal(t, x)   →   x_e(t) = 0.5 · (x(t) + x(−t))
odd_signal(t, x)    →   x_o(t) = 0.5 · (x(t) − x(−t))

Verify that x_e(t) + x_o(t) == x(t) for all sample points.
On each iteration, plot three signals on the same figure: x(t), x_e(t), x_o(t).
No alpha or beta input — the loop simply re-plots on each Enter keypress and exits on 'q'.
"""

DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

def base_signal(t):
    x = np.exp(-t) * np.sin(t)
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate(t, x, t_query):
    if t_query < T_MIN or t_query > T_MAX:
        return 0.0
    
    idx = np.searchsorted(t, t_query)

    if idx < len(t) and abs(t[idx] - t_query) < 1e-5:
        return x[idx]

    left = idx-1
    right = idx

    if left < 0:
        return x[right]
    if right >= len(t):
        return x[left]

    return (x[right] + x[left])/2.0
    

def even_signal(t, x):
    # TODO: implement x_e(t) = 0.5 * (x(t) + x(-t))
    x_e = np.zeros_like(x)
    for i, t_val in enumerate(t):
        x_e[i] = (interpolate(t, x, t_val) + interpolate(t, x, -t_val))/2
    return x_e

def odd_signal(t, x):
    # TODO: implement x_o(t) = 0.5 * (x(t) - x(-t))
    x_o = np.zeros_like(x)
    for i, t_val in enumerate(t):
        x_o[i] = (interpolate(t, x, t_val) - interpolate(t, x, -t_val))/2
    return x_o

def plot_signals(t, x, x_e, x_o):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x,   label="x(t)",   linewidth=2)
    plt.plot(t, x_e, label="x_e(t)", linewidth=2, linestyle="--")
    plt.plot(t, x_o, label="x_o(t)", linewidth=2, linestyle=":")
    plt.title("Even and Odd Decomposition")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Press Enter to plot, or type 'q' to quit.\n")

    while True:
        # TODO: complete the loop
        a = input()
        if a.lower() == 'q':
            break
        if a == '':
            x_e = even_signal(t, x)
            x_o = odd_signal(t, x)
            plot_signals(t, x, x_e, x_o)

    print("Exiting.")

if __name__ == "__main__":
    main()