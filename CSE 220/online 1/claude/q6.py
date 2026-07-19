from importlib import machinery
import numpy as np
import matplotlib.pyplot as plt

"""
Let the base signal be x(t) = sin(2t) · e^(−0.5t²), defined on [−π, π], zero outside.
Implement two separate functions applied sequentially:
def first_transform(t, x, alpha):
    # produces z(t) = x(alpha · t),   alpha > 0

def second_transform(t, z, beta):
    # produces y(t) = z(−t + beta)
The final output is y(t) = x(alpha · (−t + beta)).

Expansion in first_transform requires interpolation.
second_transform uses the output of first_transform as its input signal.
Loop accepts alpha then beta each iteration. Quit on 'q' at either prompt.
Plot x(t) and y(t) on the same figure.
"""

DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

def base_signal(t):
    x = np.sin(2 * t) * np.exp(-0.5 * t ** 2)
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate_signal(t, x, query_t):
    # TODO: implement interpolation
    if query_t < T_MIN or query_t > T_MAX:
        return 0.0
    
    idx = np.searchsorted(t, query_t)
    if idx < len(t) and abs(query_t - t[idx]) < 1e-5:
        return x[idx]

    left = idx-1
    right = idx

    if left < 0:
        return x[right]
    if right >= len(t):
        return x[left]

    return (x[left] + x[right])/2.0

def first_transform(t, x, alpha):
    # TODO: implement z(t) = x(alpha * t),   alpha > 0
    z = np.zeros_like(x)
    for i, t_val in enumerate(t):
        query_t = alpha * t_val
        z[i] = interpolate_signal(t, x, query_t)
    return z

def second_transform(t, z, beta):
    # TODO: implement y(t) = z(-t + beta)
    y = np.zeros_like(z)
    for i, t_val in enumerate(t):
        query_t = beta - t_val
        y[i] = interpolate_signal(t, z, query_t)
    return y

def plot_signals(t, x, y, alpha, beta):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x, label="x(t)", linewidth=2)
    plt.plot(t, y, label=f"y(t) = x({alpha}*(-t + {beta}))", linewidth=2, linestyle="--")
    plt.title("Cascade of Two Transformations")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter alpha (>0) and beta to plot y(t) = x(alpha*(-t + beta)).")
    print("Type 'q' at any prompt to quit.\n")

    while True:
        # TODO: complete the loop
        a = input("Enter alpha: ")
        if a.lower() == 'q':
            break
        b = input("Enter beta: ")
        if b.lower() == 'q':
            break
        
        try:
            alpha = float(a)
            beta = float(b)
        except ValueError:
            print("Invalid")
            continue
        
        z = first_transform(t, x, alpha)
        y = second_transform(t, z, beta)

        plot_signals(t, x, y, alpha, beta)

    print("Exiting.")

if __name__ == "__main__":
    main()