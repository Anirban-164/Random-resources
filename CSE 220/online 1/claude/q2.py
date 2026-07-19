from asyncio import transports
import numpy as np
import matplotlib.pyplot as plt

"""
Let the base signal be x(t) = t · cos(2t), defined on [−π, π], zero outside.
Implement transform_signal(t, x, alpha, gamma) that produces:
y(t) = gamma · x(alpha · t),   where alpha > 0

alpha controls time scaling (compress if alpha > 1, expand if alpha < 1).
gamma controls amplitude scaling.
Expansion requires interpolation for missing samples.
Loop accepts alpha and gamma repeatedly. Quit on 'q'.
"""


DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

def base_signal(t):
    x = t * np.cos(2 * t)
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate_signal(t, x, query_t):
    # TODO: implement interpolation
    if query_t < T_MIN  or query_t> T_MAX:
        return 0

    idx = np.searchsorted(t, query_t)

    if idx >= 0 and idx < len(t) and abs(t[idx] - query_t) < 1e-5:
        return x[idx]

    left_idx = idx-1
    right_idx = idx

    if left_idx < 0:
        return x[right_idx]
    
    if right_idx >= len(t):
        return x[left_idx]

    return (x[left_idx] + x[right_idx])/2.0

def transform_signal(t, x, alpha, gamma):
    # TODO: implement y(t) = gamma * x(alpha * t)
    y = np.zeros_like(x)

    for i, t_val in enumerate(t):
        query_t = alpha * t_val
        y[i] = interpolate_signal(t, x, query_t)

    y = y * gamma
    return y

def plot_signals(t, x, y, alpha, gamma):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x, label="x(t)", linewidth=2)
    plt.plot(t, y, label=f"y(t) = {gamma} * x({alpha}t)", linewidth=2, linestyle="--")
    plt.title("Amplitude Scaling with Time Compression/Expansion")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter alpha (>0) and gamma to plot y(t) = gamma * x(alpha * t).")
    print("Type 'q' at any prompt to quit.\n")

    while True:
        # TODO: complete the loop
        g = input("Enter gamma: ")
        if g.lower() == 'q':
            break
        a = input("Enter alpha: ")
        if a.lower() == 'q':
            break

        try:
            gamma = float(g)
            alpha = float(a)

            if alpha <= 0:
                print("alpha must be > 0. Try again.")
                continue
        except ValueError:
            continue

        y = transform_signal(t, x, alpha, gamma)
        plot_signals(t, x, y, alpha, gamma)

    print("Exiting.")

if __name__ == "__main__":
    main()