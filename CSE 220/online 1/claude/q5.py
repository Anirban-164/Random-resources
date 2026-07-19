import numpy as np
import matplotlib.pyplot as plt

"""
Let the base signal be x(t) = t² · sin(t), defined on [−π, π], zero outside.
Implement transform_signal(t, x, alpha) that produces two output signals:
y1(t) = alpha · x(t)       (amplitude scaling only)
y2(t) = alpha · x(−t)      (reversal + amplitude scaling)
Return both y1 and y2.

Plot all three — x(t), y1(t), y2(t) — on the same figure.
Loop accepts alpha repeatedly. Quit on 'q'.
Observe and note in a comment inside main: for what kind of signal would y1 == y2?
"""

DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

def base_signal(t):
    x = t ** 2 * np.sin(t)
    # x = t ** 2 * np.cos(t)
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate(t, x, query_t):
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

def transform_signal(t, x, alpha):
    # TODO: implement y1(t) = alpha * x(t)
    #                  y2(t) = alpha * x(-t)
    # return both y1 and y2
    y1 = np.zeros_like(x)
    y2 = np.zeros_like(x)
    for i, t_val in enumerate(t):
        y1[i] = alpha * interpolate(t, x, t_val)
        y2[i] = alpha * interpolate(t, x, -t_val)
    return y1, y2

def plot_signals(t, x, y1, y2, alpha):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x,  label="x(t)",               linewidth=2)
    plt.plot(t, y1, label=f"y1(t) = {alpha}*x(t)",  linewidth=2, linestyle="--")
    plt.plot(t, y2, label=f"y2(t) = {alpha}*x(-t)", linewidth=2, linestyle=":")
    plt.title("Folded and Scaled Comparison")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter alpha to plot y1(t) = alpha*x(t) and y2(t) = alpha*x(-t).")
    print("Type 'q' to quit.\n")

    while True:
        # TODO: complete the loop
        a = input("Enter alpha: ")
        if a.lower() == 'q':
            break
        
        try:
            alpha = float(a)
        except ValueError:
            continue

        y1, y2 = transform_signal(t, x, alpha)
        plot_signals(t, x, y1, y2, alpha)

        # Note: for what kind of signal would y1 == y2?
        # TODO: add your answer as a comment here
        if np.allclose(y1, y2):
            print("signal is even") # might not work even with cos due to assymetric array
    print("Exiting.")

if __name__ == "__main__":
    main()