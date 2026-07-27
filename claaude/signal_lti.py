# from _typeshed import importlib
import numpy as np


def readable_time_ticks(time_values, max_labels=18):
    if len(time_values) <= max_labels:
        return time_values

    step = int(np.ceil(len(time_values) / max_labels))
    ticks = time_values[::step]

    if ticks[-1] != time_values[-1]:
        ticks.append(time_values[-1])

    return ticks


class DiscreteSignal:
    """Finite discrete-time signal with integer indices."""

    # Create a finite discrete-time signal over the given integer range.
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.x = np.zeros(end_time - start_time + 1)


    # Return the number of stored samples in the signal.
    def __len__(self):
        return len(self.x)


    # Return the integer time indices covered by the signal.
    def times(self):
        t = range(self.start_time, self.end_time + 1)
        
        return t


    # Return the signal value at the given time index.
    def get_value_at_time(self, t):
        if t < self.start_time or t > self.end_time:
            return 0
        return self.x[t - self.start_time]


    # Set the signal value at the given time index.
    def set_value_at_time(self, t, value):
        if t < self.start_time or t > self.end_time:
            print("Index out of range!!!")
            return

        self.x[t - self.start_time] = value


    # Return a shifted copy of the signal.
    def shift(self, k):
        sig = DiscreteSignal(self.start_time + k, self.end_time + k)
        
        for i, val in enumerate(self.x):
            sig.set_value_at_time(self.start_time + i + k, val)
        return sig


    # Return the sum of this signal and another signal.
    def add(self, other):
        start_time = min(self.start_time, other.start_time)
        end_time = max(self.end_time, other.end_time)
        
        result = DiscreteSignal(start_time, end_time)
        for t in result.times():
            new_val = self.get_value_at_time(t) + other.get_value_at_time(t)
            result.set_value_at_time(t, new_val)
        
        return result


    # Return a scaled copy of the signal.
    def multiply(self, scalar):
        result = DiscreteSignal(self.start_time, self.end_time)
        for t in result.times():
            new_val = self.get_value_at_time(t) * scalar
            result.set_value_at_time(t, new_val)
        return result


    # Return the nonzero samples of the signal.
    def nonzero_samples(self, tolerance=1e-12):
        result = []
        for i, t in enumerate(self.times()):
            if abs(self.x[i]) > tolerance:
                result.append((t, self.x[i]))

        return result


    def plot(self, title, save_path=None, ax=None):
        import matplotlib.pyplot as plt

        if ax is None:
            _, ax = plt.subplots()

        time_values = list(self.times())
        markerline, stemlines, baseline = ax.stem(time_values, self.x) # i used 'x' instead of 'values'
        markerline.set_markersize(6)
        baseline.set_color("black")
        baseline.set_linewidth(1)

        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("n")
        ax.set_ylabel("value")
        ax.grid(True, alpha=0.35)
        ax.set_xticks(readable_time_ticks(time_values))
        ax.tick_params(axis="x", labelsize=9)

        if save_path is not None:
            plt.savefig(save_path, bbox_inches="tight", dpi=150)

        return ax

    ######## defined by me ###########
    @property
    def end_time(self):
        return self.start_time + len(self.x) - 1

    @property
    def values(self):
        return self.x

    def reverse(self):
        result = DiscreteSignal(-self.end_time, -self.start_time)
        for t in self.times():
            val = self.get_value_at_time(t)
            result.set_value_at_time(-t, val)

        return result



class LTISystem:
    """Discrete-time LTI system described by a finite impulse response."""

    # Store the impulse response that defines the LTI system.
    def __init__(self, impulse_response):
        self.h = impulse_response


    # Return the output time range for the convolution result.
    def output_range(self, x): # renamed input_signal to x
        # time range of h
        h_start = self.h.start_time
        h_end = self.h.end_time

        # output time range
        y_start = x.start_time + h_start
        y_end   = x.end_time + h_end

        return [y_start, y_end]


    # Return all shifted and scaled impulse-response components for the input.
    def get_response_components(self, x):
        components = []
        for k, x_k in x.nonzero_samples():
            shifted_h = self.h.shift(k) # h[n-k]
            scaled_h = shifted_h.multiply(x_k) # x[k] * h[n-k]
            components.append(scaled_h)
        
        return components


    # Return the system output using superposition of response components.
    def output_by_superposition(self, x):
        components = self.get_response_components(x)

        y_start = self.output_range(x)[0]
        y_end = self.output_range(x)[1]
        y = DiscreteSignal(y_start, y_end)

        for c in components:
            y = y.add(c) # y = sum x[k] * h[n-k]
        return y
        

    # Return the nonzero product terms that contribute to one output sample.
    def get_contributions_at_time(self, x, n):
        result = []
        for k, x_k in x.nonzero_samples():
            product = x_k * self.h.get_value_at_time(n - k)
            if abs(product) > 1e-12:
                result.append((k, product))
        
        return result


    # Return one output sample of the LTI system.
    def output_at_time(self, x, n):
        result = 0.0
        for k, x_k in x.nonzero_samples():
            product = x_k * self.h.get_value_at_time(n - k) # x[k] * h[n-k]
            if abs(product) > 1e-12:
                result += product
        
        return result


    # Return the complete output signal of the LTI system.
    def output(self, x):
        reversed_h = self.h.reverse()

        y_start = self.output_range(x)[0]
        y_end = self.output_range(x)[1]
        y = DiscreteSignal(y_start, y_end)

        for n in y.times():
            shifted_h = reversed_h.shift(n) # bcz h's last index will start multiplying with x's first index
            
            total = 0.0
            for k, x_k in x.nonzero_samples():
                product = x_k * shifted_h.get_value_at_time(k) 
                if abs(product) > 1e-12:
                    total += product

            y.set_value_at_time(n, total)

        return y
 