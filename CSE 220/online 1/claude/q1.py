"""
Let the base signal be x(t) = sin(t) · e^(−|t|), defined on [−π, π], zero outside.
Implement a function transform_signal(t, x, beta) that produces:
y(t) = x(−t + β)

The signal is first reversed, then shifted by β.
Values of x at non-sample points must be interpolated (average of left and right neighbours).
In main, loop to accept beta repeatedly. Quit on 'q'.
Plot x(t) and y(t) on the same figure each iteration.
"""

import numpy as np
import matplotlib.pyplot as plt

DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

    """
    use linspace to guarantee the array is perfectly symmetric around 0
    by forcing it to start exactly at t_min and end exactly at t_max
    """
    # num_points = int(np.round((t_max - t_min) / dt)) + 1
    # return np.linspace(t_min, t_max, num_points)

def base_signal(t):
    x = np.sin(t) * np.exp(-np.abs(t))
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate_signal(t, x, query_t):
    # TODO: implement interpolation
    if query_t < T_MIN or query_t > T_MAX:
        return 0.0
    
    idx = np.searchsorted(t, query_t)

    if idx >=0 and idx < len(t) and abs(t[idx] - query_t) < 1e-5:
        return x[idx]

    left_idx = idx - 1
    right_idx = idx

    if left_idx < 0:
        return x[right_idx]
    
    if right_idx >= len(t):
        return x[left_idx]

    return (x[left_idx] + x[right_idx]) / 2

def transform_signal(t, x, beta):
    # TODO: implement y(t) = x(-t + beta)
    y = np.zeros_like(x)
    for i, t_val in enumerate(t):
        query_t = -t_val + beta
        y[i] = interpolate_signal(t, x, query_t)

    return y

"""
gives a little offset of around .042 bcz
2 * π is not perfectly divisible by your dt (0.05), your time array t = np.arange(-np.pi, np.pi + dt / 2, dt) is not perfectly symmetric around zero.
"""
# def transform_signal(t, x, beta):
#     y = np.zeros_like(x)
#     for i, t_val in enumerate(t):
#         query_t = t_val + beta
#         y[i] = interpolate_signal(t, x, query_t)

#     z = y[::-1]
#     return z


def plot_signals(t, x, y, beta):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x, label="x(t)", linewidth=2)
    plt.plot(t, y, label=f"y(t) = x(-t + {beta})", linewidth=2, linestyle="--")
    plt.title("Time Reversal with Shift")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter beta to plot y(t) = x(-t + beta).")
    print("Type 'q' to quit.\n")

    while True:
        # TODO: complete the loop
        b = input("Enter beta or 'q' to quit:")

        if 'q' == b.lower():
            break

        try:
            beta = float(b)
        except ValueError:
            continue

        y = transform_signal(t, x, beta)
        plot_signals(t, x, y, beta)
    
    print("Exiting.")

if __name__ == "__main__":
    main()