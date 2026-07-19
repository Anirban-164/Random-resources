import numpy as np
import matplotlib.pyplot as plt

DT = 0.05 # sampling interval for the time axis
T_MIN, T_MAX = -np.pi, np.pi # x(t) is defined only on this range

def generate_time_axis(t_min=T_MIN, t_max=T_MAX, dt=DT):
    return np.arange(t_min, t_max + dt / 2, dt)


def base_signal(t):
    x = np.sin(t)
    x[(t < T_MIN) | (t > T_MAX)] = 0
    return x

def interpolate_signal(t, x, query_t):
    # TODO: implement interpolation
    if query_t < T_MIN or query_t > T_MAX:
        return 0.0
    
    idx = np.searchsorted(t, query_t)

    if idx >= 0 and idx < len(t) and abs(query_t - t[idx]) < 1e-5:
        return x[idx]


    left_idx  = idx - 1
    right_idx = idx
 
    if left_idx < 0:          # query_t is before all samples
        return x[right_idx]
    if right_idx >= len(t):   # query_t is after all samples
        return x[left_idx]
 
    # Average of the two surrounding samples  (spec: y(1) = 0.5*(x(0)+x(1)))
    return 0.5 * (x[left_idx] + x[right_idx])

def transform_signal(t, x, alpha, beta):
    
    # TODO: implement transformation
    y = np.zeros_like(x)
    for i, t_val in enumerate(t):
        query_t = alpha * t_val + beta
        y[i] = interpolate_signal(t, x, query_t)
    return y

def plot_signals(t, x, y, alpha, beta):
    plt.figure(figsize=(9, 5))
    plt.plot(t, x, label="x(t)", linewidth=2)
    plt.plot(t, y, label=f"y(t) = x({alpha}t + {beta})", linewidth=2, linestyle="--")
    plt.title("Time Scaling and Shifting of a Signal")
    plt.xlabel("t")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    t = generate_time_axis()
    x = base_signal(t)

    print("Enter alpha and beta to plot y(t) = x(alpha*t + beta).")
    print("Type 'q' at any prompt to quit.\n")

    while True:
        
        # TODO: complete the loop
        alpha_str = input("Enter alpha (or 'q' to quit): ")
        if alpha_str.lower() == 'q':
            break
        
        beta_str = input("Enter beta (or 'q' to quit): ")
        if beta_str.lower() == 'q':
            break
        
        try:
            alpha = float(alpha_str)
            beta = float(beta_str)
        except ValueError:
            print("Please enter valid numbers.")
            continue

        y = transform_signal(t, x, alpha, beta)
        plot_signals(t, x, y, alpha, beta)

    print("Exiting.")


if __name__ == "__main__":
    main()