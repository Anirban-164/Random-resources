import numpy as np
import matplotlib.pyplot as plt

"""
Let the base signal be x(t) = cos(t) / (1 + t²), defined on [−π, π], zero outside.
Implement transform_signal(t, x, alpha, beta, gamma) that produces:
y(t) = gamma · x(alpha · t + beta),   where alpha > 0
This combines scaling, shifting, and amplitude scaling in one function.

Handle expansion-induced missing samples via interpolation.
Loop accepts alpha, beta, and gamma each iteration. Quit on 'q' at any prompt.
Plot x(t) and y(t) labelled clearly.
"""

DT = 0.05
T_MIN, T_MAX = -np.pi, np.pi

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)

def base_signal(t):
    x = np.cos(t) / (1 + t ** 2)
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


def transform_signal(t, x, alpha, beta, gamma):
    # TODO: implement y(t) = gamma * x(alpha * t + beta)
    y = np.zeros_like(x)

    for i, t_val in enumerate(t):
        query_t = alpha * t_val + beta
        y[i] = interpolate_signal(t, x, query_t)
    
    z = y * gamma
    return z

def plot_signals(t, x, y, alpha, beta, gamma):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x, label="x(t)", linewidth=2)
    plt.plot(t, y, label=f"y(t) = {gamma} * x({alpha}t + {beta})", linewidth=2, linestyle="--")
    plt.title("General Affine Transformation")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter alpha (>0), beta, and gamma to plot y(t) = gamma * x(alpha*t + beta).")
    print("Type 'q' at any prompt to quit.\n")

    while True:
        # TODO: complete the loop
        a = input("Enter alpha (>0): ")
        if a.lower() == 'q':
            break
        b = input("Enter beta: ")
        if b.lower() == 'q':
            break
        c = input("Enter gamma: ")
        if c.lower() == 'q':
            break

        try:
            alpha = float(a)
            beta = float(b)
            gamma = float(c)
            if alpha <=0:
                print("alpha must be >0")
                continue
        except ValueError:
            print("invalid input(s)")
            continue

        y = transform_signal(t, x, alpha, beta, gamma)
        plot_signals(t, x, y, alpha, beta, gamma)
        

    print("Exiting.")

if __name__ == "__main__":
    main()