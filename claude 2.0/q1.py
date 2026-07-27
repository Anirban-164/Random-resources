# from practice.convo2 import LTISystem
from signal_lti import *

"""
Motivation
Two LTI systems h₁ and h₂ in parallel are equivalent to a single LTI system whose impulse response is the sum of the two:

  y[n] = (h₁ * x)[n] + (h₂ * x)[n] = (h_eq * x)[n],   h_eq[n] = h₁[n] + h₂[n]

You will verify this numerically using the given signals.
Given
x[n]  :  n = −1 .. 4,   values = [3, −1, 2, 0, 1, −2]
h₁[n] :  n = 0 .. 1,    values = [1, −0.5]          (weighted difference)
h₂[n] :  n = 0 .. 2,    values = [0.25, 0.5, 0.25]  (3-point smoother)
Observation window:  n = −1 .. 6
Tasks
Implement parallel(sys1, sys2, input_signal) that applies sys1 and sys2 separately, returning (y1, y2, y_parallel) where y_parallel = y1.add(y2).
Construct h_eq = h1.add(h2) and compute y_single = LTISystem(h_eq).output(x).
Implement max_absolute_difference_in_range(a, b, start, end) over an inclusive range.
Print x[n], y_parallel[n], and y_single[n] sample by sample for n = −1 .. 6.
Plot x[n], y_parallel[n], and y_single[n] as discrete-time stem plots.
Compute and print the maximum absolute difference between y_parallel and y_single over n = −1 .. 6.
In a print statement, conclude that the parallel combination equals a single system with h_eq = h₁ + h₂.
Key signatures
def parallel(sys1, sys2, input_signal):
    ...
    return y1, y2, y_parallel

def max_absolute_difference_in_range(a, b, start, end):
"""

def parallel(sys1, sys2, input_signal):
    y1 = sys1.output(input_signal)
    y2 = sys2.output(input_signal)
    y_parallel = y1.add(y2)
    return y1, y2, y_parallel

def max_absolute_difference_in_range(a, b, start, end):
    return max(abs(a.get_value_at_time(t) - b.get_value_at_time(t)) for t in range(start, end+1))
    

def main():
    x_start, x_end = -1, 4
    x_values = [3, -1, 2, 0, 1, -2]
    h1_start, h1_end = 0, 1
    h1_values = [1, -0.5]
    h2_start, h2_end = 0, 2
    h2_values = [0.25, 0.5, 0.25]
    observation_start, observation_end = -1, 6

    x = DiscreteSignal(x_start, x_end)
    for t,val in enumerate(x_values):
        x.set_value_at_time(t+x_start, val)
        
    h1 = DiscreteSignal(h1_start, h1_end)
    for t,val in enumerate(h1_values):
        h1.set_value_at_time(t+h1_start, val)
        
    h2 = DiscreteSignal(h2_start, h2_end)
    for t,val in enumerate(h2_values):
        h2.set_value_at_time(t+h2_start, val)

    sys1 = LTISystem(h1)
    sys2 = LTISystem(h2)
    
    # 1. Apply systems in parallel
    y1, y2, y_parallel = parallel(sys1, sys2, x)
    
    # 2. Construct h_eq = h1 + h2 and compute y_single
    h_eq = h1.add(h2)
    sys_eq = LTISystem(h_eq)
    y_single = sys_eq.output(x)
    
    # 3. Print sample by sample
    print(f"{'n':>3} | {'x[n]':>8} | {'y_parallel[n]':>14} | {'y_single[n]':>14}")
    print("-" * 47)
    for n in range(observation_start, observation_end + 1):
        xn = x.get_value_at_time(n)
        yp = y_parallel.get_value_at_time(n)
        ys = y_single.get_value_at_time(n)
        print(f"{n:3} | {xn:8.3f} | {yp:14.3f} | {ys:14.3f}")

    # 4. Compute and print max absolute difference
    max_diff = max_absolute_difference_in_range(y_parallel, y_single, observation_start, observation_end)
    print(f"\nMaximum absolute difference over observation window: {max_diff}")
    
    # 5. Conclusion
    print("Conclusion: The parallel combination is equal to a single system with h_eq = h1 + h2.")

    # 6. Plot the signals
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    
    times = list(range(observation_start, observation_end + 1))
    x_vals = [x.get_value_at_time(n) for n in times]
    yp_vals = [y_parallel.get_value_at_time(n) for n in times]
    ys_vals = [y_single.get_value_at_time(n) for n in times]
    
    axes[0].stem(times, x_vals)
    axes[0].set_title("Input signal x[n]")
    axes[0].grid(True)
    
    axes[1].stem(times, yp_vals)
    axes[1].set_title("Parallel Output y_parallel[n]")
    axes[1].grid(True)
    
    axes[2].stem(times, ys_vals)
    axes[2].set_title("Single System Output y_single[n]")
    axes[2].set_xlabel("n")
    axes[2].grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()