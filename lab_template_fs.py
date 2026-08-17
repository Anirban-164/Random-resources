"""
═══════════════════════════════════════════════════════════════════════
CSE 220 — Online 3 Lab Template (Task 1: Fourier Series / Epicycles)
═══════════════════════════════════════════════════════════════════════
All problem patterns from practice sessions, ready to copy-paste.
Requires fs_redrawer.py (FourierEpicycles class) in the same folder,
along with svg_utils.py and epicycle_animation.py.

Covered problems:
  From A Online:
    — Energy-based harmonic pruning (prune_harmonics_by_energy)
    — Reconstruction error evaluation (evaluate_reconstruction_error)

  From Practice (Claude):
    Q1  — Low-pass harmonic truncation (set |n| > max_n to zero)
    Q2  — Phase scrambling (keep magnitude, randomize phase)
    Q3  — Conjugate symmetry check (c_{-n} == conj(c_n)?)
    Q4  — Energy spectrum plot + cumulative energy ratio
    Q5  — Derivative of Fourier Series (f'(t) = sum c_n * jnω * e^{jnωt})
    Q6  — Time-shifted reconstruction (start drawing from different point)
"""

import numpy as np
import matplotlib.pyplot as plt

from svg_utils import load_svg_path
from epicycle_animation import save_outputs
from fs_redrawer import FourierEpicycles


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — UTILITY / HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def load_and_compute(svg_path='svgs/heart.svg', num_points=1000, n_harmonics=150):
    """Load an SVG, create FourierEpicycles, compute all coefficients."""
    t, z = load_svg_path(svg_path, num_points=num_points)
    fs = FourierEpicycles(t, z, n_harmonics=n_harmonics)
    fs.calculate_all_coefficients()
    return t, z, fs


def compute_mse(original_signal, reconstructed_signal):
    """MSE = mean(|f(t) - f_hat(t)|^2)"""
    return np.mean(np.abs(original_signal - reconstructed_signal)**2)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — FourierEpicycles EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════

class ExtendedFourierEpicycles(FourierEpicycles):
    """FourierEpicycles with all extra methods from practice problems."""

    # ── A Online: Energy-based pruning ────────────────────────────────
    def prune_harmonics_by_energy(self, threshold):
        """
        Sort coefficients by |c_n|^2 descending.
        Keep adding harmonics until cumulative energy >= threshold * total_energy.
        Returns the pruned dict of coefficients.
        """
        total_energy = sum(abs(cn)**2 for cn in self.coeffs.values())
        energy_limit = total_energy * threshold

        sorted_coeffs = sorted(self.coeffs.items(), key=lambda x: abs(x[1]), reverse=True)

        new_coeffs = {}
        running_sum = 0
        for (n, cn) in sorted_coeffs:
            new_coeffs[n] = cn
            running_sum += abs(cn)**2
            if running_sum >= energy_limit:
                break
        return new_coeffs

    # ── A Online: Reconstruction error ────────────────────────────────
    def evaluate_reconstruction_error(self):
        """MSE between original signal and current approximation."""
        return compute_mse(self.signal, self.approximate(self.t))

    # ── Q1: Low-pass harmonic truncation ─────────────────────────────
    def truncate_harmonics(self, max_n):
        """Set to zero all coefficients c_n where |n| > max_n."""
        for n in list(self.coeffs.keys()):
            if abs(n) > max_n:
                self.coeffs[n] = 0

    # ── Q2: Phase scrambling ─────────────────────────────────────────
    def scramble_phases(self, seed=42):
        """Keep magnitudes, randomize phases with uniform [0, 2π)."""
        rng = np.random.default_rng(seed)
        for n in self.coeffs:
            magnitude = abs(self.coeffs[n])
            random_angle = rng.uniform(0, 2 * np.pi)
            self.coeffs[n] = magnitude * np.exp(1j * random_angle)

    # ── Q3: Conjugate symmetry check ─────────────────────────────────
    def check_conjugate_symmetry(self, tol=1e-9):
        """
        Check if c_{-n} == conj(c_n) for all n.
        Returns (is_symmetric, max_delta).
        For complex-valued signals (SVGs), this should NOT hold.
        """
        max_delta = 0
        for n in range(1, self.N + 1):
            c_neg = self.coeffs.get(-n, 0)
            c_pos_conj = np.conj(self.coeffs.get(n, 0))
            delta = abs(c_neg - c_pos_conj)
            if delta > max_delta:
                max_delta = delta
        is_symmetric = (max_delta < tol)
        return is_symmetric, max_delta

    # ── Q4: Energy spectrum plot ─────────────────────────────────────
    def plot_energy_spectrum(self, save_path="energy_spectrum.png"):
        """Bar chart of |c_n|^2 vs n."""
        ns = sorted(self.coeffs.keys())
        energies = [abs(self.coeffs[n])**2 for n in ns]
        plt.figure()
        plt.bar(ns, energies)
        plt.xlabel("Harmonic n")
        plt.ylabel("|c_n|²")
        plt.title("Energy Spectrum")
        plt.savefig(save_path)
        plt.show()

    # ── Q4: Cumulative energy ratio (same as A Online pruning) ───────
    def cumulative_energy_ratio(self):
        """
        Sort harmonics by energy descending.
        Return list of (count, ratio) tuples.
        """
        total = sum(abs(cn)**2 for cn in self.coeffs.values())
        sorted_energies = sorted(self.coeffs.values(), key=lambda cn: abs(cn)**2, reverse=True)

        result = []
        running = 0
        for i, cn in enumerate(sorted_energies):
            running += abs(cn)**2
            result.append((i + 1, running / total))
        return result

    # ── Q5: Derivative of Fourier Series ─────────────────────────────
    def approximate_derivative(self, t):
        """
        f'(t) = sum c_n * (j*n*omega) * exp(j*n*omega*t)
        Each coefficient gets multiplied by jnω.
        Works with t as scalar or array (NumPy broadcasting).
        """
        derivatives = np.zeros_like(t, dtype=np.complex128)
        for (n, c_n) in self.coeffs.items():
            derivatives += c_n * (1j * n * self.omega) * np.exp(1j * n * self.omega * t)
        return derivatives

    # ── Q6: Time-shifted reconstruction ──────────────────────────────
    def approximate_shifted(self, t, t_shift):
        """
        Reconstruct the signal shifted by t_shift:
            f_shifted(t) = sum c_n * exp(j*n*omega*(t - t_shift))
        This starts drawing the shape from a different point on the curve.
        The shape itself doesn't change.
        """
        result = np.zeros_like(t, dtype=complex)
        for n, cn in self.coeffs.items():
            result += cn * np.exp(1j * n * self.omega * (t - t_shift))
        return result


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3 — PLOTTING HELPERS
# ═══════════════════════════════════════════════════════════════════════

def plot_reconstruction(original_z, reconstructed, title="Reconstruction", save_path=None):
    """Plot original vs reconstructed complex signal in 2D."""
    plt.figure()
    plt.plot(original_z.real, original_z.imag, 'gray', alpha=0.5, label='Original')
    plt.plot(reconstructed.real, reconstructed.imag, 'r-', label='Reconstructed')
    plt.axis('equal')
    plt.title(title)
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plot_speed(t, derivative, save_path=None):
    """Plot |f'(t)| — the pen speed — vs time."""
    speed = np.abs(derivative)
    plt.figure()
    plt.plot(t, speed)
    plt.xlabel("t")
    plt.ylabel("|f'(t)| (pen speed)")
    plt.title("Speed of the Drawing Pen")
    if save_path:
        plt.savefig(save_path)
    plt.show()


# ═══════════════════════════════════════════════════════════════════════
# MAIN — Skeleton (fill in per question)
# ═══════════════════════════════════════════════════════════════════════

def main():
    # ── 0. Load signal and compute coefficients ──────────────────────
    # t, z, fs = load_and_compute('svgs/heart.svg', n_harmonics=150)
    # -- or create ExtendedFourierEpicycles directly: --
    # t, z = load_svg_path('svgs/heart.svg', num_points=1000)
    # fs = ExtendedFourierEpicycles(t, z, n_harmonics=150)
    # fs.calculate_all_coefficients()

    # ── 1. Truncate harmonics (Q1 — low-pass) ───────────────────────
    # fs.truncate_harmonics(max_n=15)
    # mse = compute_mse(z, fs.approximate(t))
    # save_outputs(fs, z, "heart_truncated_15.png", "heart_truncated_15.gif", num_frames=1)

    # ── 2. Scramble phases (Q2) ──────────────────────────────────────
    # fs.scramble_phases(seed=42)
    # mse = compute_mse(z, fs.approximate(t))
    # save_outputs(fs, z, "heart_scrambled.png", "heart_scrambled.gif", num_frames=1)

    # ── 3. Conjugate symmetry (Q3) ───────────────────────────────────
    # is_sym, delta = fs.check_conjugate_symmetry()
    # print(f"symmetric={is_sym}, max_delta={delta:.2e}")

    # ── 4. Energy spectrum + cumulative ratio (Q4) ───────────────────
    # fs.plot_energy_spectrum()
    # cumulative = fs.cumulative_energy_ratio()
    # for target in [0.90, 0.95, 0.99, 0.999]:
    #     for count, ratio in cumulative:
    #         if ratio >= target:
    #             print(f"{target*100:.1f}% energy needs {count} harmonics")
    #             break

    # ── 5. Derivative / pen speed (Q5) ───────────────────────────────
    # derivative = fs.approximate_derivative(t)
    # plot_speed(t, derivative, save_path="heart_derivative.png")

    # ── 6. Time-shifted reconstruction (Q6) ──────────────────────────
    # for i, frac in enumerate([0, 0.25, 0.5, 0.75]):
    #     t_shift = frac * fs.T
    #     shifted = fs.approximate_shifted(t, t_shift)
    #     plot_reconstruction(z, shifted, title=f"Shifted by {frac}T",
    #                         save_path=f"heart_shifted_{i}.png")

    # ── 7. Energy-based pruning (A Online) ───────────────────────────
    # original_coeffs = fs.coeffs.copy()
    # for ratio in [0.96, 0.98, 0.99, 1.00]:
    #     fs.coeffs = original_coeffs.copy()
    #     pruned = fs.prune_harmonics_by_energy(ratio)
    #     fs.coeffs = pruned
    #     mse = fs.evaluate_reconstruction_error()
    #     print(f"ratio={ratio:.2f}, retained={len(pruned)}, MSE={mse.real:.4f}")

    pass


if __name__ == "__main__":
    main()
