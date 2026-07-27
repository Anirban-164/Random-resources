"""
═══════════════════════════════════════════════════════════════════════
CSE 220 — Online 2 Lab Template
═══════════════════════════════════════════════════════════════════════
All problem patterns from practice sessions, ready to copy-paste.
Just import signal_lti.py (must be in the same folder) and use.

Covered problems:
  Set 1 (claaude):
    Q1 — Energy & L2 norm
    Q2 — Signal subtraction
    Q3 — Causality check
    Q4 — Verify linearity (LTISystem method)
    Q5 — Verify time-invariance (LTISystem method)
    Q6 — Cross-correlation
    Q7 — Step response & first-difference check

  Set 2 (claude 2.0):
    Q1 — Parallel LTI systems
    Q2 — Commutativity of convolution
    Q3 — Even/odd decomposition
    Q4 — Matched filter & peak detection
    Q5 — Generic linearity & time-invariance tests (callable-based, non-LTI)
"""

from signal_lti import *
import numpy as np
import matplotlib.pyplot as plt


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — UTILITY / HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def make_signal(start, end, values):
    """Create a DiscreteSignal from a list of values."""
    sig = DiscreteSignal(start, end)
    for i, v in enumerate(values):
        sig.set_value_at_time(start + i, v)
    return sig


def max_absolute_difference_in_range(a, b, start, end):
    """Max |a[n] - b[n]| over n = start..end."""
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))


def max_diff(a, b):
    """Max |a[n] - b[n]| over the union of both time ranges."""
    start = min(a.start_time, b.start_time)
    end   = max(a.end_time,   b.end_time)
    return max(abs(a.get_value_at_time(n) - b.get_value_at_time(n))
               for n in range(start, end + 1))


def find_peak(signal, start, end):
    """Return the time index of the maximum value over [start, end]."""
    peak_n, peak_val = start, signal.get_value_at_time(start)
    for n in range(start, end + 1):
        val = signal.get_value_at_time(n)
        if val > peak_val:
            peak_val = val
            peak_n = n
    return peak_n


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — DiscreteSignal EXTENSIONS  (subclass or monkey-patch)
# ═══════════════════════════════════════════════════════════════════════

class ExtendedSignal(DiscreteSignal):
    """DiscreteSignal with all extra methods from practice problems."""

    # ── Q1 (Set 1): Energy & L2 norm ──────────────────────────────────
    def energy(self):
        """E = Σ_n |x[n]|²"""
        return np.sum(self.values ** 2)

    def l2_norm(self):
        """L₂ = √E"""
        return np.sqrt(self.energy())

    # ── Q2 (Set 1): Subtraction ───────────────────────────────────────
    def subtract(self, other):
        """z[n] = x[n] - y[n] over the union of both time ranges."""
        start_time = min(self.start_time, other.start_time)
        end_time   = max(self.end_time,   other.end_time)
        result = DiscreteSignal(start_time, end_time)
        for t in result.times():
            result.set_value_at_time(t,
                self.get_value_at_time(t) - other.get_value_at_time(t))
        return result

    # ── Q3 (Set 1): Causality check ──────────────────────────────────
    def is_causal(self):
        """Causal ⟺ h[n] = 0 for all n < 0."""
        if self.start_time >= 0:
            return True
        for t, x in self.nonzero_samples():
            if t >= 0:
                return True
            if np.abs(x) > 0:
                return False
        return True          # all-zero signal is causal

    # ── Q6 (Set 1): Cross-correlation ────────────────────────────────
    def cross_correlate(self, other):
        """
        R_xy[m] = Σ_k x[k] · y[k+m]
        Key identity: R_xy[m] = (x[−n] * y[n])[m]
        """
        x_reversed = self.reverse()
        sys = LTISystem(x_reversed)
        return sys.output(other)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3 — LTISystem EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════

class ExtendedLTI(LTISystem):
    """LTISystem with all extra methods from practice problems."""

    # ── Q4 (Set 1): Verify linearity ─────────────────────────────────
    def verify_linearity(self, x1, x2, a, b):
        """
        LHS = T{ a·x₁ + b·x₂ }
        RHS = a·T{x₁} + b·T{x₂}
        Returns max_n |LHS[n] − RHS[n]|
        """
        lhs = self.output(x1.multiply(a).add(x2.multiply(b)))
        rhs = self.output(x1).multiply(a).add(self.output(x2).multiply(b))
        return max_diff(lhs, rhs)

    # ── Q5 (Set 1): Verify time-invariance ───────────────────────────
    def verify_time_invariance(self, x, k):
        """
        x[n] → y[n]  ⟹  x[n−k] → y[n−k]
        Returns max_n |T{x[n−k]} − y[n−k]|
        """
        y_shifted = self.output(x).shift(k)
        y2        = self.output(x.shift(k))
        return max_diff(y_shifted, y2)

    # ── Q7 (Set 1): Step response ────────────────────────────────────
    def step_response(self, n_start, n_end):
        """
        Build u[n] = 1 for n ≥ 0, else 0 over [n_start, n_end].
        Return s = T{u} and print the first-difference check.
        """
        u = DiscreteSignal(n_start, n_end)
        for n in range(max(0, n_start), n_end + 1):
            u.set_value_at_time(n, 1.0)

        s = self.output(u)

        # Verify: s[n] − s[n−1] = h[n] for n in h's range
        max_err = 0.0
        for n in self.h.times():
            first_diff = s.get_value_at_time(n) - s.get_value_at_time(n - 1)
            err = abs(first_diff - self.h.get_value_at_time(n))
            max_err = max(max_err, err)

        print(f"First-difference check: max |s[n]-s[n-1]-h[n]| = {max_err:.2e}")
        return s


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4 — STANDALONE FUNCTIONS (Set 2 problems)
# ═══════════════════════════════════════════════════════════════════════

# ── Q1 (Set 2): Parallel LTI systems ────────────────────────────────
def parallel(sys1, sys2, input_signal):
    """
    y_parallel = T₁{x} + T₂{x}
    Returns (y1, y2, y_parallel).
    """
    y1 = sys1.output(input_signal)
    y2 = sys2.output(input_signal)
    y_parallel = y1.add(y2)
    return y1, y2, y_parallel


# ── Q2 (Set 2): Commutativity verification ───────────────────────────
def convolve_signals(a, b):
    """Convolution using LTISystem: (a * b)[n] = LTISystem(a).output(b)."""
    return LTISystem(a).output(b)


# ── Q3 (Set 2): Even / Odd decomposition ────────────────────────────
def even_part(x):
    """x_e[n] = (x[n] + x[−n]) / 2"""
    return x.add(x.reverse()).multiply(0.5)


def odd_part(x):
    """x_o[n] = (x[n] − x[−n]) / 2"""
    return x.add(x.reverse().multiply(-1)).multiply(0.5)


# ── Q4 (Set 2): Matched filter ──────────────────────────────────────
def matched_filter(template):
    """h[n] = s[−n].  Returns an LTISystem."""
    return LTISystem(template.reverse())


# ═══════════════════════════════════════════════════════════════════════
# SECTION 5 — GENERIC (CALLABLE-BASED) LINEARITY / TI TESTS
#              (for non-LTI systems, Set 2 Q5)
# ═══════════════════════════════════════════════════════════════════════

def test_linearity(apply_system, x1, x2, a, b):
    """
    Works with ANY callable apply_system(x) -> DiscreteSignal.
    Returns max |T{ax₁ + bx₂} − (aT{x₁} + bT{x₂})|.
    """
    lhs = apply_system(x1.multiply(a).add(x2.multiply(b)))
    rhs = apply_system(x1).multiply(a).add(apply_system(x2).multiply(b))
    return max_diff(lhs, rhs)


def test_time_invariance(apply_system, x, k):
    """
    Works with ANY callable apply_system(x) -> DiscreteSignal.
    Returns max |T{x[n−k]} − y[n−k]|.
    """
    y_shifted = apply_system(x).shift(k)
    y2        = apply_system(x.shift(k))
    return max_diff(y_shifted, y2)


# Example non-LTI systems ─────────────────────────────────────────────
def system_squarer(x):
    """y[n] = x[n]²  — time-invariant, but NONlinear."""
    result = DiscreteSignal(x.start_time, x.end_time)
    for t in x.times():
        result.set_value_at_time(t, x.get_value_at_time(t) ** 2)
    return result


def system_time_varying(x):
    """y[n] = x[n] · cos(πn/4)  — linear, but time-VARYING."""
    result = DiscreteSignal(x.start_time, x.end_time)
    for t in x.times():
        result.set_value_at_time(t, x.get_value_at_time(t) * np.cos(np.pi * t / 4))
    return result


# ═══════════════════════════════════════════════════════════════════════
# SECTION 6 — PLOTTING HELPERS
# ═══════════════════════════════════════════════════════════════════════

def stem_plot(signals, titles, suptitle="", obs_start=None, obs_end=None,
              save_path=None):
    """
    Quick multi-panel stem plot.
    signals : list of DiscreteSignal
    titles  : list of str (same length)
    """
    n_plots = len(signals)
    fig, axes = plt.subplots(n_plots, 1, figsize=(10, 3 * n_plots),
                             constrained_layout=True)
    if n_plots == 1:
        axes = [axes]

    for ax, sig, title in zip(axes, signals, titles):
        s = obs_start if obs_start is not None else sig.start_time
        e = obs_end   if obs_end   is not None else sig.end_time
        ns = list(range(s, e + 1))
        vals = [sig.get_value_at_time(n) for n in ns]
        ax.stem(ns, vals)
        ax.set_title(title)
        ax.set_xlabel("n")
        ax.grid(True, alpha=0.35)

    if suptitle:
        fig.suptitle(suptitle, fontsize=14, fontweight='bold')
    if save_path:
        fig.savefig(save_path, dpi=150)
    plt.show()


def print_samples(signals, headers, obs_start, obs_end):
    """
    Print a side-by-side table of signal values.
    signals : list of DiscreteSignal
    headers : list of str  (e.g. ["x[n]", "y[n]"])
    """
    hdr = f"{'n':>4}" + "".join(f"  {h:>14}" for h in headers)
    print(hdr)
    print("-" * len(hdr))
    for n in range(obs_start, obs_end + 1):
        row = f"{n:4d}"
        for sig in signals:
            row += f"  {sig.get_value_at_time(n):14.4f}"
        print(row)


# ═══════════════════════════════════════════════════════════════════════
# MAIN — Skeleton (fill in per question)
# ═══════════════════════════════════════════════════════════════════════

def main():
    # ── 1. Build your signals ─────────────────────────────────────────
    # x = make_signal(start, end, [v0, v1, ...])
    # h = make_signal(start, end, [v0, v1, ...])

    # ── 2. Build system(s) ────────────────────────────────────────────
    # sys = ExtendedLTI(h)          # if you need verify_linearity, etc.
    # sys = LTISystem(h)            # plain convolution

    # ── 3. Compute outputs ────────────────────────────────────────────
    # y = sys.output(x)

    # ── 4. Print samples ─────────────────────────────────────────────
    # print_samples([x, y], ["x[n]", "y[n]"], obs_start, obs_end)

    # ── 5. Verify properties ─────────────────────────────────────────
    # diff = sys.verify_linearity(x1, x2, a, b)
    # diff = sys.verify_time_invariance(x, k)
    # diff = test_linearity(some_callable, x1, x2, a, b)
    # diff = test_time_invariance(some_callable, x, k)

    # ── 6. Plot ───────────────────────────────────────────────────────
    # stem_plot([x, y], ["Input x[n]", "Output y[n]"])

    pass


if __name__ == "__main__":
    main()
