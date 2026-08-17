"""
═══════════════════════════════════════════════════════════════════════
CSE 220 — Online 3 Lab Template (Task 2: 2D CFT / Image Filtering)
═══════════════════════════════════════════════════════════════════════
All problem patterns from practice sessions, ready to copy-paste.
Requires cft_edge_detector.py (ContinuousImage, CFT2D, InverseCFT2D,
FrequencyFilter classes) in the same folder.

Covered problems:
  From B Online:
    — Band-pass filter (retain r_low < d <= r_high)
    — Band-stop filter (zero  r_low < d <= r_high)
    — Complementarity verification (I_bp + I_bs ≈ I_original)
    — Brightness shift (add to DC component)

  From Practice (Claude):
    Q7  — Low-pass filter (keep d <= cutoff, zero the rest)
    Q8  — HP + LP complementarity (I_hp + I_lp ≈ I_original)
    Q9  — Ring / annular band-pass filter (same as band_pass)
    Q10 — Radial energy profile (energy in concentric rings)
    Q11 — Cross-shaped mask (zero horizontal + vertical freqs)
    Q12 — DC component extraction / removal (a0)
    Q13 — Spectrum rotation (np.rot90 → rotates image)
    Q14 — Spectrum scaling (contrast enhancement, skip DC)
    Q15 — Spectral energy thresholding (denoising)
"""

import numpy as np
import matplotlib.pyplot as plt

from cft_edge_detector import ContinuousImage, CFT2D, InverseCFT2D, FrequencyFilter, ReconstructionValidator


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — UTILITY / HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def load_and_transform(image_path='pikachu.png'):
    """Load image, compute 2D CFT, return everything needed."""
    img = ContinuousImage(image_path)
    cft2d = CFT2D(img)
    real, imag = cft2d.compute_cft()
    return img, cft2d, real, imag


def reconstruct_image(real, imag, cft2d, img):
    """Shorthand for inverse CFT reconstruction."""
    icft2d = InverseCFT2D(real, imag, cft2d.u, cft2d.v, img.x, img.y)
    return icft2d.reconstruct()


def save_edge_map(image_data, output_path, invert=True):
    """Save as edge map: normalize, optionally invert (edges=black)."""
    edge_map = np.abs(image_data)
    if edge_map.max() > 0:
        edge_map /= edge_map.max()
    if invert:
        edge_map = 1 - edge_map
    plt.imsave(output_path, edge_map, cmap='gray')


def save_clipped_image(image_data, output_path):
    """Save reconstructed image clipped to [0, 1]."""
    clipped = np.clip(image_data, 0, 1)
    plt.imsave(output_path, clipped, cmap='gray')


def spectral_energy(real, imag):
    """Total energy in the spectrum: sum(real^2 + imag^2)."""
    return np.sum(real**2 + imag**2)


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — FrequencyFilter EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════

class ExtendedFrequencyFilter(FrequencyFilter):
    """FrequencyFilter with all extra methods from practice problems."""

    # ── Q7: Low-pass filter ──────────────────────────────────────────
    def low_pass(self, real, imag, cutoff):
        """Keep only frequencies within the cutoff radius (d <= cutoff)."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        real = real.copy()
        imag = imag.copy()
        for i in range(rows):
            for j in range(cols):
                if np.sqrt((i - cx)**2 + (j - cy)**2) > cutoff:
                    real[i, j] = 0
                    imag[i, j] = 0
        return real, imag

    # ── Q9: Ring / annular band-pass filter ──────────────────────────
    # Note: This is identical to band_pass from B Online!
    def ring_filter(self, real, imag, r_inner, r_outer):
        """Keep only entries in the annular ring r_inner < d <= r_outer."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        real = real.copy()
        imag = imag.copy()
        for i in range(rows):
            for j in range(cols):
                d = np.sqrt((i - cx)**2 + (j - cy)**2)
                if not (r_inner < d <= r_outer):
                    real[i, j] = 0
                    imag[i, j] = 0
        return real, imag

    # ── Q11: Cross-shaped mask ───────────────────────────────────────
    def cross_mask(self, real, imag, width):
        """Zero out a cross-shaped region at center of spectrum.
        Removes pure horizontal and vertical frequencies.
        Diagonal edges survive."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        real = real.copy()
        imag = imag.copy()
        for i in range(rows):
            for j in range(cols):
                if abs(i - cx) <= width or abs(j - cy) <= width:
                    real[i, j] = 0
                    imag[i, j] = 0
        return real, imag

    # ── Q12: DC component extraction / removal ───────────────────────
    # DC = a0 = the center pixel = average brightness of the image
    def extract_dc(self, real, imag):
        """Return the DC component value (center pixel)."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        return real[cx, cy], imag[cx, cy]

    def remove_dc(self, real, imag):
        """Return spectrum with DC component set to zero."""
        real = real.copy()
        imag = imag.copy()
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        real[cx, cy] = 0
        imag[cx, cy] = 0
        return real, imag

    # ── Q13: Spectrum rotation ───────────────────────────────────────
    # Rotating frequency spectrum by 90° rotates the spatial image by 90°
    # np.rot90 only does multiples of 90°; for arbitrary angles use scipy.ndimage.rotate
    def rotate_spectrum_90(self, real, imag):
        """Rotate the spectrum 90 degrees counterclockwise."""
        return np.rot90(real.copy()), np.rot90(imag.copy())

    # ── Q14: Spectrum scaling (contrast enhancement) ─────────────────
    def scale_spectrum(self, real, imag, factor):
        """Scale all non-DC frequency components by factor.
        Trick: save DC → multiply everything → restore DC."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2
        real = real.copy()
        imag = imag.copy()

        # Save DC
        dc_r, dc_i = real[cx, cy], imag[cx, cy]
        # Scale everything
        real *= factor
        imag *= factor
        # Restore DC
        real[cx, cy] = dc_r
        imag[cx, cy] = dc_i

        return real, imag

    # ── Q15: Spectral energy thresholding (denoising) ────────────────
    def threshold_spectrum(self, real, imag, threshold):
        """Zero out entries where energy (real^2 + imag^2) < threshold."""
        rows, cols = real.shape
        real = real.copy()
        imag = imag.copy()
        for i in range(rows):
            for j in range(cols):
                if real[i, j]**2 + imag[i, j]**2 < threshold:
                    real[i, j] = 0
                    imag[i, j] = 0
        return real, imag


# ═══════════════════════════════════════════════════════════════════════
# SECTION 3 — CFT2D EXTENSIONS
# ═══════════════════════════════════════════════════════════════════════

class ExtendedCFT2D(CFT2D):
    """CFT2D with extra analysis methods."""

    # ── Q10: Radial energy profile ───────────────────────────────────
    def radial_energy_profile(self, real, imag, num_bins=50):
        """Compute energy in concentric annular rings."""
        rows, cols = real.shape
        cx, cy = rows // 2, cols // 2  # integer division for center index

        max_dist = np.sqrt(cx**2 + cy**2)
        bin_width = max_dist / num_bins

        radii = np.zeros(num_bins)
        energies = np.zeros(num_bins)

        for i in range(rows):
            for j in range(cols):
                d = np.sqrt((i - cx)**2 + (j - cy)**2)
                bin_idx = int(d / bin_width)
                if bin_idx >= num_bins:
                    bin_idx = num_bins - 1
                energies[bin_idx] += real[i, j]**2 + imag[i, j]**2

        for b in range(num_bins):
            radii[b] = (b + 0.5) * bin_width  # center of each bin

        return radii, energies


# ═══════════════════════════════════════════════════════════════════════
# SECTION 4 — VERIFICATION HELPERS
# ═══════════════════════════════════════════════════════════════════════

class ExtendedValidator(ReconstructionValidator):
    """Extended validator with HP+LP complementarity check."""

    # ── Q8: HP + LP complementarity ──────────────────────────────────
    def verify_hp_lp_complementarity(self, I_original, I_hp, I_lp):
        """Check that I_hp + I_lp ≈ I_original."""
        delta = np.max(np.abs(I_original - (I_hp + I_lp)))
        is_valid = bool(delta < 1e-9)
        return is_valid, delta


# ═══════════════════════════════════════════════════════════════════════
# MAIN — Skeleton (fill in per question)
# ═══════════════════════════════════════════════════════════════════════

def main():
    # ── 0. Load image and compute 2D CFT ─────────────────────────────
    # img, cft2d, real, imag = load_and_transform('pikachu.png')
    # filt = ExtendedFrequencyFilter()

    # ── 1. High-pass filter (given, edge detection) ──────────────────
    # real_hp, imag_hp = filt.high_pass(real, imag, cutoff=15)
    # edges = reconstruct_image(real_hp, imag_hp, cft2d, img)
    # save_edge_map(edges, "pikachu_edges.png")

    # ── 2. Low-pass filter (Q7 — blurring) ──────────────────────────
    # real_lp, imag_lp = filt.low_pass(real, imag, cutoff=15)
    # blurred = reconstruct_image(real_lp, imag_lp, cft2d, img)
    # save_clipped_image(blurred, "pikachu_lowpass.png")

    # ── 3. HP + LP complementarity (Q8) ──────────────────────────────
    # I_orig = reconstruct_image(real, imag, cft2d, img)
    # I_hp = reconstruct_image(real_hp, imag_hp, cft2d, img)
    # I_lp = reconstruct_image(real_lp, imag_lp, cft2d, img)
    # validator = ExtendedValidator()
    # is_valid, delta = validator.verify_hp_lp_complementarity(I_orig, I_hp, I_lp)
    # print(f"Complementarity: {is_valid}, delta: {delta:.2e}")

    # ── 4. Band-pass / ring filter (Q9 — same as B Online) ──────────
    # for r_inner, r_outer in [(0, 10), (10, 30), (30, 50)]:
    #     real_r, imag_r = filt.ring_filter(real, imag, r_inner, r_outer)
    #     fraction = spectral_energy(real_r, imag_r) / spectral_energy(real, imag)
    #     print(f"Ring ({r_inner}, {r_outer}]: energy = {fraction:.4f}")
    #     I_ring = reconstruct_image(real_r, imag_r, cft2d, img)
    #     save_edge_map(I_ring, f"pikachu_ring_{r_inner}_{r_outer}.png")

    # ── 5. Radial energy profile (Q10) ───────────────────────────────
    # ext_cft = ExtendedCFT2D(img)
    # radii, energies = ext_cft.radial_energy_profile(real, imag)
    # plt.bar(radii, energies, width=radii[1] - radii[0])
    # plt.xlabel("Radius from center")
    # plt.ylabel("Total energy")
    # plt.title("Radial Energy Profile")
    # plt.savefig("pikachu_radial_energy.png")
    # plt.show()

    # ── 6. Cross mask (Q11) ──────────────────────────────────────────
    # real_c, imag_c = filt.cross_mask(real, imag, width=3)
    # I_cross = reconstruct_image(real_c, imag_c, cft2d, img)
    # save_edge_map(I_cross, "pikachu_cross_masked.png")

    # ── 7. DC component (Q12 — a0 / average brightness) ─────────────
    # dc_real, dc_imag = filt.extract_dc(real, imag)
    # print(f"DC component: real={dc_real:.4f}, imag={dc_imag:.4f}")
    # real_nodc, imag_nodc = filt.remove_dc(real, imag)
    # I_nodc = reconstruct_image(real_nodc, imag_nodc, cft2d, img)
    # plt.imsave("pikachu_no_dc.png", I_nodc, cmap='gray')

    # ── 8. Spectrum rotation (Q13) ───────────────────────────────────
    # real_r, imag_r = filt.rotate_spectrum_90(real, imag)
    # I_rotated = reconstruct_image(real_r, imag_r, cft2d, img)
    # save_clipped_image(I_rotated, "pikachu_rotated_spectrum.png")

    # ── 9. Spectrum scaling / contrast (Q14) ─────────────────────────
    # real_s, imag_s = filt.scale_spectrum(real, imag, factor=2.0)
    # I_enhanced = reconstruct_image(real_s, imag_s, cft2d, img)
    # save_clipped_image(I_enhanced, "pikachu_enhanced.png")

    # ── 10. Spectral thresholding / denoising (Q15) ──────────────────
    # real_t, imag_t = filt.threshold_spectrum(real, imag, threshold=0.01)
    # I_denoised = reconstruct_image(real_t, imag_t, cft2d, img)
    # save_clipped_image(I_denoised, "pikachu_denoised.png")

    # ── 11. Band-pass / Band-stop (B Online) ─────────────────────────
    # real_bp, imag_bp = filt.band_pass(real, imag, r_low=5, r_high=20)
    # real_bs, imag_bs = filt.band_stop(real, imag, r_low=5, r_high=20)
    # I_bp = reconstruct_image(real_bp, imag_bp, cft2d, img)
    # I_bs = reconstruct_image(real_bs, imag_bs, cft2d, img)
    # I_recon = reconstruct_image(real, imag, cft2d, img)
    # validator = ReconstructionValidator()
    # is_valid, delta = validator.verify_complementarity(I_recon, I_bp, I_bs)
    # print(f"BP + BS complementarity: {is_valid}, delta: {delta:.2e}")

    # ── 12. Brightness shift (B Online) ──────────────────────────────
    # real_bright, imag_bright = filt.shift_brightness(real, imag, shift_amount=0.5)
    # I_bright = reconstruct_image(real_bright, imag_bright, cft2d, img)
    # save_clipped_image(I_bright, "pikachu_brighter.png")

    pass


if __name__ == "__main__":
    main()
