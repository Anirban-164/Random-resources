"""
Practice online A1 -- product of THREE big integers with one inverse transform.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python a1_triple_product.py --input inputs/3.txt --third-digits 2000 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from bigmul import from_limbs, to_limbs
from io_utils import random_decimal, read_operands, write_report, write_text
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)

# A coefficient of a triple product is a sum of about n^2/2 products of THREE
# limbs, so it can reach (n^2/2)(B-1)^3. With B = 10^4 that leaves the 2^53
# mantissa for the provided inputs; B = 10^2 keeps every coefficient exact.
TRIPLE_BASE_DIGITS = 2


def choose_transform_length(len_a, len_b, len_c, engine):
    """Return the transform length for the linear convolution of three limb arrays."""
    # TODO 1 (student): a product of three polynomials with n, q and r
    # coefficients has n + q + r - 2 coefficients. The radix-2 engine needs a
    # power of two; the arbitrary engine can use the exact length.
    need = len_a+len_b+len_c-2
    if engine.name == "arbitrary":
        return need
    return next_power_of_two(need)


def multiply_three_transform(a, b, c, engine):
    """Return (un-carried coefficients of a*b*c, transform length N)."""
    # TODO 2 (student): zero-pad the three limb arrays to N, transform each one
    # once, multiply the three spectra pointwise, inverse-transform exactly
    # once, keep the real part, crop to the linear length and round to int64.
    need = len(a)+len(b)+len(c)-2
    N = choose_transform_length(len(a), len(b), len(c), engine)
    fa = np.zeros(N, dtype=np.complex128); fa[:len(a)] = a
    fb = np.zeros(N, dtype=np.complex128); fb[:len(b)] = b
    fc = np.zeros(N, dtype=np.complex128); fc[:len(c)] = c
    spectrum = engine.transform(fa)*engine.transform(fb)*engine.transform(fc)
    coeffs = engine.inverse(spectrum).real[:need]
    return np.rint(coeffs).astype(np.int64), N


def multiply_three(text_a, text_b, text_c, method):
    """Return (product string, N, (limbs_a, limbs_b, limbs_c))."""
    # TODO 3 (student): convert every operand with TRIPLE_BASE_DIGITS, keep the
    # signs aside, convolve, carry with the SAME base and re-attach the sign.
    sign_a, la = to_limbs(text_a, TRIPLE_BASE_DIGITS)
    sign_b, lb = to_limbs(text_b, TRIPLE_BASE_DIGITS)
    sign_c, lc = to_limbs(text_c, TRIPLE_BASE_DIGITS)
    coeffs, N = multiply_three_transform(la, lb, lc, _make_engine(method))
    product = from_limbs(sign_a*sign_b*sign_c, coeffs, TRIPLE_BASE_DIGITS)
    return product, N, (len(la), len(lb), len(lc))


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as inputs/3.txt are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(input_path, third_digits, engine_name, out_dir):
    """Provided runner: multiply, verify with Python's integers, write outputs."""
    text_a, text_b = read_operands(_resolve(input_path))
    text_c = random_decimal(third_digits, seed=third_digits)
    product, N, limbs = multiply_three(text_a, text_b, text_c, engine_name)

    expected = str(int(text_a)*int(text_b)*int(text_c))   # the ONLY big-int use
    verdict = "MATCH" if product == expected else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    write_text(os.path.join(out_dir, "product.txt"), product)
    digits = tuple(len(t.lstrip("+-")) for t in (text_a, text_b, text_c))
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice A1 -- triple product by spectral convolution",
        "input file           : %s" % input_path,
        "engine               : %s" % engine_name,
        "digits of A / B / C  : %d / %d / %d" % digits,
        "base                 : 10^%d" % TRIPLE_BASE_DIGITS,
        "limbs of A / B / C   : %d / %d / %d" % limbs,
        "transform length N   : %d" % N,
        "digits of product    : %d" % len(product.lstrip("-")),
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("triple product did not match the reference")
    return product


def main():
    parser = argparse.ArgumentParser(description="Product of three big integers")
    parser.add_argument("--input", default="inputs/3.txt")
    parser.add_argument("--third-digits", type=int, default=2000)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "a1"))
    args = parser.parse_args()
    run(args.input, args.third_digits, args.engine, args.out_dir)


if __name__ == "__main__":
    main()






"""
Practice online A2 -- a*b + c*d with exactly ONE inverse transform (linearity).

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python a2_sum_of_products.py --digits 1500 --seed 11 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from bigmul import BASE_DIGITS, from_limbs, to_limbs
from io_utils import random_decimal, write_report, write_text
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)


def choose_transform_length(len_a, len_b, len_c, len_d, engine):
    """Return one transform length that holds BOTH linear products."""
    # TODO 1 (student): a*b needs len_a + len_b - 1 slots and c*d needs
    # len_c + len_d - 1; one N must hold the longer of the two. Power of two
    # for the radix-2 engine, exact length for the arbitrary engine.
    need = max(len_a+len_b-1, len_c+len_d-1)
    if engine.name == "arbitrary":
        return need
    return next_power_of_two(need)


def sum_of_products_transform(a, b, c, d, engine):
    """Return (un-carried coefficients of a*b + c*d, transform length N)."""
    # TODO 2 (student): zero-pad all four limb arrays to N and transform each
    # once. Form A*B + C*D in the frequency domain (the DFT is linear, so the
    # sum of two products comes back from ONE inverse transform). Keep the
    # real part, crop to the longer linear length, round to int64.
    need = max(len(a)+len(b)-1, len(c)+len(d)-1)
    N = choose_transform_length(len(a), len(b), len(c), len(d), engine)
    spectra = []
    for limbs in (a, b, c, d):
        padded = np.zeros(N, dtype=np.complex128); padded[:len(limbs)] = limbs
        spectra.append(engine.transform(padded))
    A, B, C, D = spectra
    coeffs = engine.inverse(A*B + C*D).real[:need]
    return np.rint(coeffs).astype(np.int64), N


def sum_of_products(text_a, text_b, text_c, text_d, method):
    """Return (result string, N, limb counts) for four NON-NEGATIVE decimals."""
    # TODO 3 (student): convert all four with to_limbs; raise ValueError if any
    # sign is negative (a signed sum cannot be carried by from_limbs); convolve;
    # carry with a positive sign.
    limbs = []
    for text in (text_a, text_b, text_c, text_d):
        sign, arr = to_limbs(text)
        if sign < 0:
            raise ValueError("operands must be non-negative")
        limbs.append(arr)
    coeffs, N = sum_of_products_transform(*limbs, _make_engine(method))
    return from_limbs(1, coeffs), N, tuple(len(arr) for arr in limbs)


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def run(digits, seed, engine_name, out_dir):
    """Provided runner: four reproducible operands, verify, write outputs."""
    texts = [random_decimal(digits, seed=seed+i) for i in range(4)]
    result, N, limbs = sum_of_products(*texts, engine_name)

    a, b, c, d = (int(t) for t in texts)                  # the ONLY big-int use
    expected = str(a*b + c*d)
    verdict = "MATCH" if result == expected else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    write_text(os.path.join(out_dir, "result.txt"), result)
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice A2 -- a*b + c*d with one inverse transform",
        "digits per operand   : %d" % digits,
        "engine               : %s" % engine_name,
        "base                 : 10^%d" % BASE_DIGITS,
        "limbs of A/B/C/D     : %d / %d / %d / %d" % limbs,
        "transform length N   : %d" % N,
        "digits of result     : %d" % len(result),
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("sum of products did not match the reference")
    return result


def main():
    parser = argparse.ArgumentParser(description="a*b + c*d through one inverse transform")
    parser.add_argument("--digits", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "a2"))
    args = parser.parse_args()
    run(args.digits, args.seed, args.engine, args.out_dir)


if __name__ == "__main__":
    main()






"""
Practice online A3 -- circular convolution and the wraparound it causes.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python a3_circular_wraparound.py --digits 120 --seed 5 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from bigmul import from_limbs, multiply_transform, to_limbs
from io_utils import random_decimal, write_report
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)


def short_length(len_a, len_b, engine):
    """Return a length that holds both inputs but NOT their full product."""
    # TODO 1 (student): max(len_a, len_b) is enough room for either input and
    # deliberately too little for the len_a + len_b - 1 product coefficients.
    # Round up to a power of two for the radix-2 engine; the arbitrary engine
    # can use it as is.
    N = max(len_a, len_b)
    if engine.name == "arbitrary":
        return N
    return next_power_of_two(N)


def circular_convolve(a, b, N, engine):
    """Return the length-N CIRCULAR convolution of a and b as int64."""
    # TODO 2 (student): zero-pad both arrays to exactly N (no further),
    # transform, multiply pointwise, inverse-transform, keep the real part and
    # round. Nothing is cropped: all N slots are the answer.
    fa = np.zeros(N, dtype=np.complex128); fa[:len(a)] = a
    fb = np.zeros(N, dtype=np.complex128); fb[:len(b)] = b
    circular = engine.inverse(engine.transform(fa)*engine.transform(fb)).real
    return np.rint(circular).astype(np.int64)


def fold(linear, N):
    """Wrap a linear convolution onto N slots: out[m mod N] += linear[m]."""
    # TODO 3 (student): every coefficient past slot N-1 is added back onto
    # slot m mod N. Return an int64 array of length N.
    out = np.zeros(N, dtype=np.int64)
    for m in range(len(linear)):
        out[m % N] += linear[m]
    return out


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def run(digits, seed, engine_name, out_dir):
    """Provided runner: compare the short transform with the folded padded one."""
    engine = _make_engine(engine_name)
    text_a = random_decimal(digits, seed=seed)
    text_b = random_decimal(digits, seed=seed+1)
    _, la = to_limbs(text_a)
    _, lb = to_limbs(text_b)

    N_short = short_length(len(la), len(lb), engine)
    circular = circular_convolve(la, lb, N_short, engine)
    linear, N_full = multiply_transform(la, lb, engine)     # the offline's padded route
    folded = fold(linear, N_short)

    error = int(np.max(np.abs(circular - folded)))
    wrapped_number = from_limbs(1, circular)
    correct_number = from_limbs(1, linear)
    exact = str(int(text_a)*int(text_b))                     # the ONLY big-int use
    verdict = "MATCH" if error == 0 and correct_number == exact else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice A3 -- circular convolution and wraparound",
        "digits per operand   : %d" % digits,
        "engine               : %s" % engine_name,
        "limbs of A / B       : %d / %d" % (len(la), len(lb)),
        "product needs        : %d coefficients" % len(linear),
        "short transform N    : %d  (too small -> wraps)" % N_short,
        "padded transform N   : %d" % N_full,
        "max |circular - folded linear| : %d" % error,
        "digits, correct product        : %d" % len(correct_number),
        "digits, wrapped 'product'      : %d" % len(wrapped_number),
        "wrapped 'product' starts with  : %s..." % wrapped_number[:24],
        "correct product starts with    : %s..." % correct_number[:24],
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(max |circular - folded| = %d)" % error)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("circular convolution did not equal the folded linear one")


def main():
    parser = argparse.ArgumentParser(description="Circular convolution and wraparound")
    parser.add_argument("--digits", type=int, default=120)
    parser.add_argument("--seed", type=int, default=5)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "a3"))
    args = parser.parse_args()
    run(args.digits, args.seed, args.engine, args.out_dir)


if __name__ == "__main__":
    main()






"""
Practice online A4 -- cross-correlation through the spectrum: find a shift.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python a4_shift_correlation.py --digits 400 --shift 7 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from bigmul import BASE_DIGITS, to_limbs
from io_utils import random_decimal, write_report
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)


def choose_transform_length(len_a, len_b, engine):
    """Return a transform length in which every lag has its own slot."""
    # TODO 1 (student): the lags run from -(len_a - 1) to len_b - 1, which is
    # len_a + len_b - 1 values -- the same rule as linear convolution. Power of
    # two for the radix-2 engine, exact for the arbitrary engine.
    need = len_a+len_b-1
    if engine.name == "arbitrary":
        return need
    return next_power_of_two(need)


def cross_correlate(a, b, engine):
    """Return (c, N): c[k] = sum_i a[i] * b[i + k], lag k stored at index k mod N."""
    # TODO 2 (student): zero-pad both arrays to N and transform. Correlation is
    # convolution with a time-reversed a, and for a real sequence reversal is
    # conjugation in the frequency domain: multiply conj(A) by B, inverse-
    # transform ONCE, keep the real part and round to int64.
    N = choose_transform_length(len(a), len(b), engine)
    fa = np.zeros(N, dtype=np.complex128); fa[:len(a)] = a
    fb = np.zeros(N, dtype=np.complex128); fb[:len(b)] = b
    spectrum = np.conj(engine.transform(fa))*engine.transform(fb)
    c = engine.inverse(spectrum).real
    return np.rint(c).astype(np.int64), N


def find_shift(text_a, text_b, method):
    """Return (shift, peak, N): the lag with the largest correlation."""
    # TODO 3 (student): use the limb magnitudes only, correlate, take the
    # index of the maximum, and unwrap it: an index above N // 2 is really a
    # negative lag (index - N). The peak value is the correlation at that lag.
    _, la = to_limbs(text_a)
    _, lb = to_limbs(text_b)
    c, N = cross_correlate(la, lb, _make_engine(method))
    k = int(np.argmax(c))
    if k > N//2:
        k -= N
    return k, int(c.max()), N


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def run(digits, shift, engine_name, out_dir):
    """Provided runner: b = a * BASE^shift, so b's limbs are a's moved up by shift."""
    text_a = random_decimal(digits, seed=digits)
    text_b = text_a + "0"*(BASE_DIGITS*shift)
    found, peak, N = find_shift(text_a, text_b, engine_name)

    # Independent oracle: the defining double loop over every lag.
    _, la = to_limbs(text_a)
    _, lb = to_limbs(text_b)
    spectral, _ = cross_correlate(la, lb, _make_engine(engine_name))
    error = 0
    for k in range(-(len(la)-1), len(lb)):
        direct = 0
        for i in range(len(la)):
            j = i + k
            if 0 <= j < len(lb):
                direct += int(la[i])*int(lb[j])
        error = max(error, abs(int(spectral[k % N]) - direct))
    energy = int(np.sum(la.astype(np.int64)**2))
    verdict = "MATCH" if error == 0 and found == shift and peak == energy else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice A4 -- shift detection by spectral cross-correlation",
        "digits of A          : %d" % digits,
        "engine               : %s" % engine_name,
        "limbs of A / B       : %d / %d" % (len(la), len(lb)),
        "transform length N   : %d" % N,
        "true shift (limbs)   : %d" % shift,
        "detected shift       : %d" % found,
        "peak correlation     : %d  (energy of A = %d)" % (peak, energy),
        "max |spectral - direct| over all lags : %d" % error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(detected shift %d, expected %d)" % (found, shift))
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("cross-correlation did not match the reference")


def main():
    parser = argparse.ArgumentParser(description="Shift detection by cross-correlation")
    parser.add_argument("--digits", type=int, default=400)
    parser.add_argument("--shift", type=int, default=7)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "a4"))
    args = parser.parse_args()
    run(args.digits, args.shift, args.engine, args.out_dir)


if __name__ == "__main__":
    main()






"""
Practice online A5 -- a^4 by squaring twice, one forward transform per square.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python a5_fourth_power.py --input inputs/3.txt --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from bigmul import BASE_DIGITS, from_limbs, to_limbs
from io_utils import read_operands, write_report, write_text
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)


def square_length(n, engine):
    """Return the transform length for squaring an n-limb number."""
    # TODO 1 (student): a square has 2n - 1 coefficients. Power of two for
    # the radix-2 engine, exact for the arbitrary engine.
    need = 2*n-1
    if engine.name == "arbitrary":
        return need
    return next_power_of_two(need)


def square_transform(a, engine):
    """Return (un-carried coefficients of a*a, N) using ONE forward transform."""
    # TODO 2 (student): zero-pad to N, transform once, multiply the spectrum
    # by itself, inverse-transform, keep the real part, crop to 2n - 1 and
    # round to int64. Two forward transforms here is wrong: it is one.
    need = 2*len(a)-1
    N = square_length(len(a), engine)
    fa = np.zeros(N, dtype=np.complex128); fa[:len(a)] = a
    A = engine.transform(fa)
    coeffs = engine.inverse(A*A).real[:need]
    return np.rint(coeffs).astype(np.int64), N


def fourth_power(text, method):
    """Return (a^4 as a string, (N1, N2), (limbs of a, limbs of a^2))."""
    # TODO 3 (student): square the limbs, then CARRY the result into a proper
    # number (from_limbs) and split it into limbs again (to_limbs) BEFORE the
    # second squaring -- un-carried coefficients are far bigger than the base
    # and squaring them would overflow the double mantissa. An even power is
    # never negative, so the sign is +1 throughout.
    _, limbs = to_limbs(text)
    engine = _make_engine(method)
    square, N1 = square_transform(limbs, engine)
    _, reduced = to_limbs(from_limbs(1, square))
    fourth, N2 = square_transform(reduced, engine)
    return from_limbs(1, fourth), (N1, N2), (len(limbs), len(reduced))


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as inputs/3.txt are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(input_path, engine_name, out_dir):
    """Provided runner: fourth power of the first operand, verified exactly."""
    text, _ = read_operands(_resolve(input_path))
    result, (N1, N2), (limbs1, limbs2) = fourth_power(text, engine_name)

    expected = str(int(text)**4)                             # the ONLY big-int use
    verdict = "MATCH" if result == expected else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    write_text(os.path.join(out_dir, "result.txt"), result)
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice A5 -- fourth power by repeated squaring",
        "input file           : %s (first operand)" % input_path,
        "engine               : %s" % engine_name,
        "digits of A          : %d" % len(text.lstrip("+-")),
        "base                 : 10^%d" % BASE_DIGITS,
        "limbs of A / A^2     : %d / %d" % (limbs1, limbs2),
        "transform lengths    : %d then %d" % (N1, N2),
        "digits of A^4        : %d" % len(result),
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("fourth power did not match the reference")
    return result


def main():
    parser = argparse.ArgumentParser(description="Fourth power by repeated squaring")
    parser.add_argument("--input", default="inputs/3.txt")
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "a5"))
    args = parser.parse_args()
    run(args.input, args.engine, args.out_dir)


if __name__ == "__main__":
    main()








"""
Practice online B1 -- shift an image by multiplying its spectrum by a phase ramp.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python b1_spectral_shift.py --image images/skyline256.png --rows 37 --cols -21 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from image_conv import inverse_2d, transform_2d
from image_utils import load_image, save_comparison, save_image
from io_utils import write_report
from transforms import ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer


def phase_ramp(shape, shift_rows, shift_cols):
    """Return the spectrum multiplier that delays a plane by (shift_rows, shift_cols)."""
    # TODO 1 (student): delaying x[n] by s multiplies X[u] by exp(-2 pi j u s / N).
    # In 2D the exponent adds: exp(-2 pi j (u*shift_rows/H + v*shift_cols/W))
    # with u = 0..H-1 down the rows and v = 0..W-1 along the columns.
    height, width = shape
    u = np.arange(height, dtype=np.float64)[:, np.newaxis]
    v = np.arange(width, dtype=np.float64)[np.newaxis, :]
    return np.exp(-2j*np.pi*(u*shift_rows/height + v*shift_cols/width))


def shift_plane(plane, shift_rows, shift_cols, engine):
    """Circularly shift one plane through the frequency domain."""
    # TODO 2 (student): transform the plane (no padding: the shift is meant to
    # wrap), multiply by the ramp, inverse-transform ONCE, keep the real part.
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)*phase_ramp(plane.shape, shift_rows, shift_cols)
    return inverse_2d(spectrum, engine).real


def shift_image(image, shift_rows, shift_cols, engine):
    """Apply shift_plane to a grayscale or RGB image, preserving its shape."""
    # TODO 3 (student): one plane for grayscale; three planes stacked back
    # along the last axis for RGB.
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return shift_plane(image, shift_rows, shift_cols, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [shift_plane(image[:, :, c], shift_rows, shift_cols, engine)
                  for c in range(image.shape[2])]
        return np.stack(planes, axis=-1)
    raise ValueError("images must be grayscale or RGB")


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as images/skyline256.png are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(image_path, shift_rows, shift_cols, engine_name, out_dir, color=False):
    """Provided runner: compare the spectral shift with np.roll."""
    engine = _make_engine(engine_name)
    image = load_image(_resolve(image_path), as_gray=not color)
    result = shift_image(image, shift_rows, shift_cols, engine)

    reference = np.roll(image, (shift_rows, shift_cols), axis=(0, 1))   # the oracle
    maximum_error = float(np.max(np.abs(result - reference)))
    verdict = "MATCH" if maximum_error <= 1e-9 else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    save_image(result, os.path.join(out_dir, "shifted.png"))
    save_comparison(
        [image, result, reference],
        ["original", "spectral shift (%d, %d)" % (shift_rows, shift_cols), "np.roll reference"],
        os.path.join(out_dir, "comparison.png"),
        suptitle="Shift through the frequency domain, engine=%s" % engine_name,
    )
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice B1 -- shift by a spectral phase ramp",
        "image                : %s" % image_path,
        "image shape          : %s" % (image.shape,),
        "shift (rows, cols)   : (%d, %d)" % (shift_rows, shift_cols),
        "engine               : %s" % engine_name,
        "max |spectral - np.roll| : %.3e" % maximum_error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(max error %.3e)" % maximum_error)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("spectral shift did not match np.roll")
    return result


def main():
    parser = argparse.ArgumentParser(description="Shift an image through its spectrum")
    parser.add_argument("--image", default="images/skyline256.png")
    parser.add_argument("--rows", type=int, default=37)
    parser.add_argument("--cols", type=int, default=-21)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--color", action="store_true")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "b1"))
    args = parser.parse_args()
    run(args.image, args.rows, args.cols, args.engine, args.out_dir, color=args.color)


if __name__ == "__main__":
    main()








"""
Practice online B2 -- unsharp masking (sharpening) in the frequency domain.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python b2_unsharp_mask.py --image images/skyline256.png --kernel-size 21 --amount 1.5 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from image_conv import convolve_image, inverse_2d, transform_2d
from image_utils import load_image, make_kernel, save_comparison, save_image
from io_utils import write_report
from transforms import (ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer,
                        next_power_of_two)


def choose_transform_shape(image_shape, kernel_shape, engine):
    """Return the padded 2D linear-convolution transform shape."""
    # TODO 1 (student): full convolution size per axis, then a power of two
    # per axis for the radix-2 engine only.
    rows, cols = image_shape
    krows, kcols = kernel_shape
    full_height, full_width = rows+krows-1, cols+kcols-1
    if engine.name == "fft":
        full_height, full_width = next_power_of_two(full_height), next_power_of_two(full_width)
    return full_height, full_width


def centred_delta_spectrum(transform_shape, kernel_shape):
    """Provided helper: DFT of an impulse placed at the kernel's centre."""
    height, width = transform_shape
    centre_row = kernel_shape[0] // 2
    centre_column = kernel_shape[1] // 2
    vertical = np.arange(height, dtype=np.float64)[:, np.newaxis]
    horizontal = np.arange(width, dtype=np.float64)[np.newaxis, :]
    phase = vertical * centre_row / height + horizontal * centre_column / width
    return np.exp(-2j * np.pi * phase)


def _pad_top_left(array, shape):
    """Provided helper: place a 2D array at the origin of a complex array."""
    result = np.zeros(shape, dtype=np.complex128)
    result[:array.shape[0], :array.shape[1]] = array
    return result


def sharpen_plane(plane, kernel, amount, engine):
    """Return plane + amount * (plane - blur(plane)) built in the frequency domain."""
    # TODO 2 (student): pad the plane and the kernel, transform both, take the
    # centred delta, form P * (delta + amount * (delta - G)), inverse-transform
    # ONCE, keep the real part and crop the usual linear-convolution window.
    plane = np.asarray(plane, dtype=np.float64)
    shape = choose_transform_shape(plane.shape, kernel.shape, engine)
    plane_spectrum = transform_2d(_pad_top_left(plane, shape), engine)
    kernel_spectrum = transform_2d(_pad_top_left(kernel, shape), engine)
    delta_spectrum = centred_delta_spectrum(shape, kernel.shape)
    combined = plane_spectrum*(delta_spectrum + amount*(delta_spectrum - kernel_spectrum))
    full = inverse_2d(combined, engine).real
    row, column = kernel.shape[0] // 2, kernel.shape[1] // 2
    return full[row:row + plane.shape[0], column:column + plane.shape[1]]


def sharpen_image(image, kernel, amount, engine):
    """Apply sharpen_plane to a grayscale or RGB image, preserving its shape."""
    # TODO 3 (student): one plane for grayscale; three planes stacked back
    # along the last axis for RGB.
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return sharpen_plane(image, kernel, amount, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        planes = [sharpen_plane(image[:, :, c], kernel, amount, engine)
                  for c in range(image.shape[2])]
        return np.stack(planes, axis=-1)
    raise ValueError("images must be grayscale or RGB")


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as images/skyline256.png are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(image_path, kernel_size, amount, engine_name, out_dir, color=False):
    """Provided runner: compare against the spatial-domain unsharp mask."""
    if kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError("kernel size must be a positive odd integer")
    engine = _make_engine(engine_name)
    image = load_image(_resolve(image_path), as_gray=not color)
    kernel = make_kernel("gaussian", size=kernel_size)
    result = sharpen_image(image, kernel, amount, engine)

    blurred = convolve_image(image, kernel, engine)                 # the oracle route
    reference = image + amount * (image - blurred)
    maximum_error = float(np.max(np.abs(result - reference)))
    verdict = "MATCH" if maximum_error <= 1e-9 else "MISMATCH"

    os.makedirs(out_dir, exist_ok=True)
    save_image(result, os.path.join(out_dir, "sharpened.png"))
    save_image(np.clip(0.5 + 2.0 * (image - blurred), 0.0, 1.0),
               os.path.join(out_dir, "detail.png"))
    save_comparison(
        [image, blurred, result],
        ["original", "Gaussian blur", "sharpened (amount %.2f)" % amount],
        os.path.join(out_dir, "comparison.png"),
        suptitle="Unsharp mask: Gaussian %dx%d, engine=%s" % (kernel_size, kernel_size, engine_name),
    )
    transform_shape = choose_transform_shape(image.shape[:2], kernel.shape, engine)
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice B2 -- unsharp masking in the frequency domain",
        "image                : %s" % image_path,
        "image shape          : %s" % (image.shape,),
        "kernel               : Gaussian %d x %d" % kernel.shape,
        "amount               : %.3f" % amount,
        "engine               : %s" % engine_name,
        "transform shape      : %d x %d" % transform_shape,
        "max |spectral - spatial| : %.3e" % maximum_error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(max error %.3e)" % maximum_error)
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("sharpened result did not match the reference")
    return result


def main():
    parser = argparse.ArgumentParser(description="Unsharp masking through the spectrum")
    parser.add_argument("--image", default="images/skyline256.png")
    parser.add_argument("--kernel-size", type=int, default=21)
    parser.add_argument("--amount", type=float, default=1.5)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--color", action="store_true")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "b2"))
    args = parser.parse_args()
    run(args.image, args.kernel_size, args.amount, args.engine, args.out_dir, color=args.color)


if __name__ == "__main__":
    main()






"""
Practice online B3 -- deblurring by inverse filtering (spectral division).

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python b3_deblur.py --image images/skyline256.png --kernel-size 5 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from image_conv import convolve_image, inverse_2d, transform_2d
from image_utils import load_image, make_kernel, save_comparison, save_image
from io_utils import write_report
from transforms import ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer


def wrapped_kernel_spectrum(kernel, shape, engine):
    """Return the spectrum of the kernel wrapped around the origin of ``shape``."""
    # TODO 1 (student): embed the kernel at the top-left of a zero array of
    # the plane's shape, roll it by (-(kh//2), -(kw//2)) so its centre tap sits
    # at index (0, 0) -- exactly the circular path of convolve_plane -- and
    # transform it.
    krows, kcols = kernel.shape
    padded = np.zeros(shape, dtype=np.float64)
    padded[:krows, :kcols] = kernel
    padded = np.roll(padded, (-(krows // 2), -(kcols // 2)), axis=(0, 1))
    return transform_2d(padded, engine)


def deblur_plane(blurred, kernel, engine, epsilon=1e-12):
    """Undo a circular blur: divide the blurred spectrum by the kernel spectrum."""
    # TODO 2 (student): Y = spectrum of the blurred plane, G = wrapped kernel
    # spectrum. Where |G| > epsilon set X = Y / G; everywhere else set X = 0
    # (never divide by a vanishing bin). Inverse-transform ONCE, keep the real part.
    blurred = np.asarray(blurred, dtype=np.float64)
    blurred_spectrum = transform_2d(blurred, engine)
    kernel_spectrum = wrapped_kernel_spectrum(kernel, blurred.shape, engine)
    restored = np.zeros_like(blurred_spectrum)
    reliable = np.abs(kernel_spectrum) > epsilon
    restored[reliable] = blurred_spectrum[reliable] / kernel_spectrum[reliable]
    return inverse_2d(restored, engine).real


def deblur_image(blurred, kernel, engine):
    """Apply deblur_plane to a grayscale or RGB image, preserving its shape."""
    # TODO 3 (student): one plane for grayscale; three planes stacked back
    # along the last axis for RGB.
    blurred = np.asarray(blurred, dtype=np.float64)
    if blurred.ndim == 2:
        return deblur_plane(blurred, kernel, engine)
    if blurred.ndim == 3 and blurred.shape[2] == 3:
        planes = [deblur_plane(blurred[:, :, c], kernel, engine)
                  for c in range(blurred.shape[2])]
        return np.stack(planes, axis=-1)
    raise ValueError("images must be grayscale or RGB")


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as images/skyline256.png are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(image_path, kernel_size, engine_name, out_dir, color=False):
    """Provided runner: blur circularly with the offline, deblur, compare with the original."""
    if kernel_size < 1 or kernel_size % 2 == 0:
        raise ValueError("kernel size must be a positive odd integer")
    engine = _make_engine(engine_name)
    original = load_image(_resolve(image_path), as_gray=not color)
    kernel = make_kernel("gaussian", size=kernel_size)

    blurred = convolve_image(original, kernel, engine, circular=True)   # what the student receives
    restored = deblur_image(blurred, kernel, engine)

    maximum_error = float(np.max(np.abs(restored - original)))          # the oracle is the original
    verdict = "MATCH" if maximum_error <= 1e-9 else "MISMATCH"
    smallest_bin = float(np.min(np.abs(wrapped_kernel_spectrum(kernel, original.shape[:2], engine))))

    os.makedirs(out_dir, exist_ok=True)
    save_image(blurred, os.path.join(out_dir, "blurred.png"))
    save_image(restored, os.path.join(out_dir, "restored.png"))
    save_comparison(
        [original, blurred, restored],
        ["original", "circular Gaussian blur", "restored by spectral division"],
        os.path.join(out_dir, "comparison.png"),
        suptitle="Inverse filtering: Gaussian %dx%d, engine=%s" % (kernel_size, kernel_size, engine_name),
    )
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice B3 -- deblurring by inverse filtering",
        "image                : %s" % image_path,
        "image shape          : %s" % (original.shape,),
        "kernel               : Gaussian %d x %d" % kernel.shape,
        "engine               : %s" % engine_name,
        "smallest |G| bin     : %.3e  (rounding noise is amplified by 1/this)" % smallest_bin,
        "max |restored - original| : %.3e" % maximum_error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(max error %.3e, smallest |G| %.3e)" % (maximum_error, smallest_bin))
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("restored image did not match the original")
    return restored


def main():
    parser = argparse.ArgumentParser(description="Deblur by spectral division")
    parser.add_argument("--image", default="images/skyline256.png")
    parser.add_argument("--kernel-size", type=int, default=5)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--color", action="store_true")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "b3"))
    args = parser.parse_args()
    run(args.image, args.kernel_size, args.engine, args.out_dir, color=args.color)


if __name__ == "__main__":
    main()








"""
Practice online B4 -- phase correlation: find how far one image was shifted.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python b4_phase_correlation.py --image images/skyline256.png --rows 37 --cols -21 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from image_conv import inverse_2d, transform_2d
from image_utils import load_image, save_comparison, save_image
from io_utils import write_report
from transforms import ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer


def unit_cross_power(spectrum_a, spectrum_b, epsilon=1e-12):
    """Return conj(A) * B normalised to unit magnitude, bin by bin."""
    # TODO 1 (student): cross = conj(A) * B. Where |cross| > epsilon divide by
    # |cross| so only the phase difference survives; every other bin becomes 0.
    # Never divide by a vanishing magnitude.
    cross = np.conj(spectrum_a) * spectrum_b
    magnitude = np.abs(cross)
    result = np.zeros_like(cross)
    reliable = magnitude > epsilon
    result[reliable] = cross[reliable] / magnitude[reliable]
    return result


def correlation_surface(plane_a, plane_b, engine):
    """Return the phase-correlation surface of two planes (a peak marks the shift)."""
    # TODO 2 (student): transform both planes (no padding: the shift wraps),
    # take the unit cross-power spectrum, inverse-transform ONCE, keep the
    # real part.
    spectrum_a = transform_2d(np.asarray(plane_a, dtype=np.float64), engine)
    spectrum_b = transform_2d(np.asarray(plane_b, dtype=np.float64), engine)
    return inverse_2d(unit_cross_power(spectrum_a, spectrum_b), engine).real


def find_shift(image_a, image_b, engine):
    """Return (shift_rows, shift_cols, surface) such that image_b = roll(image_a, shift)."""
    # TODO 3 (student): grayscale -> one surface; RGB -> the SUM of the three
    # channel surfaces. The peak's (row, col) is the shift; an index above
    # H//2 (or W//2) is really negative: subtract H (or W).
    image_a = np.asarray(image_a, dtype=np.float64)
    image_b = np.asarray(image_b, dtype=np.float64)
    if image_a.shape != image_b.shape:
        raise ValueError("the two images must have the same shape")
    if image_a.ndim == 2:
        surface = correlation_surface(image_a, image_b, engine)
    elif image_a.ndim == 3 and image_a.shape[2] == 3:
        surface = sum(correlation_surface(image_a[:, :, c], image_b[:, :, c], engine)
                      for c in range(image_a.shape[2]))
    else:
        raise ValueError("images must be grayscale or RGB")
    height, width = surface.shape
    row, col = np.unravel_index(int(np.argmax(surface)), surface.shape)
    row, col = int(row), int(col)
    if row > height // 2:
        row -= height
    if col > width // 2:
        col -= width
    return row, col, surface


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as images/skyline256.png are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def run(image_path, shift_rows, shift_cols, engine_name, out_dir, color=False):
    """Provided runner: shift with np.roll, recover the shift, check the peak."""
    engine = _make_engine(engine_name)
    image_a = load_image(_resolve(image_path), as_gray=not color)
    image_b = np.roll(image_a, (shift_rows, shift_cols), axis=(0, 1))
    found_rows, found_cols, surface = find_shift(image_a, image_b, engine)

    planes = 1 if image_a.ndim == 2 else image_a.shape[2]
    height, width = surface.shape
    ideal = np.zeros((height, width))                       # an exact shift gives a unit impulse
    ideal[shift_rows % height, shift_cols % width] = 1.0
    maximum_error = float(np.max(np.abs(surface / planes - ideal)))
    verdict = ("MATCH" if (found_rows, found_cols) == (shift_rows, shift_cols)
               and maximum_error <= 1e-9 else "MISMATCH")

    os.makedirs(out_dir, exist_ok=True)
    peak_view = np.clip(surface / planes, 0.0, 1.0)
    save_image(peak_view, os.path.join(out_dir, "correlation_surface.png"))
    save_comparison(
        [image_a, image_b, peak_view],
        ["image A", "image B = roll(A, (%d, %d))" % (shift_rows, shift_cols),
         "phase correlation (peak at shift)"],
        os.path.join(out_dir, "comparison.png"),
        suptitle="Phase correlation, engine=%s" % engine_name,
    )
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice B4 -- shift recovery by phase correlation",
        "image                : %s" % image_path,
        "image shape          : %s" % (image_a.shape,),
        "true shift           : (%d, %d)" % (shift_rows, shift_cols),
        "detected shift       : (%d, %d)" % (found_rows, found_cols),
        "peak height          : %.6f  (1.0 for an exact circular shift)" % (float(surface.max()) / planes),
        "engine               : %s" % engine_name,
        "max |surface - unit impulse| : %.3e" % maximum_error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(detected (%d, %d), expected (%d, %d))"
          % (found_rows, found_cols, shift_rows, shift_cols))
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("phase correlation did not recover the shift")
    return found_rows, found_cols


def main():
    parser = argparse.ArgumentParser(description="Recover an image shift by phase correlation")
    parser.add_argument("--image", default="images/skyline256.png")
    parser.add_argument("--rows", type=int, default=37)
    parser.add_argument("--cols", type=int, default=-21)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--color", action="store_true")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "b4"))
    args = parser.parse_args()
    run(args.image, args.rows, args.cols, args.engine, args.out_dir, color=args.color)


if __name__ == "__main__":
    main()









"""
Practice online B5 -- ideal low-pass / high-pass split of an image spectrum.

Complete TODO 1--3. Do not modify the original offline files.

Run:

    python b5_ideal_filter.py --image images/skyline256.png --radius 20 --engine fft
"""

import argparse
import os
import sys

import numpy as np

PRACTICE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFLINE_DIR = os.path.dirname(PRACTICE_DIR)
sys.path.insert(0, OFFLINE_DIR)   # practice only: a real online sits next to the offline files

from image_conv import inverse_2d, transform_2d
from image_utils import load_image, save_comparison, save_image
from io_utils import write_report
from transforms import ArbitraryLengthFFT, DFTAnalyzer, FFTTransformer


def radial_mask(shape, radius):
    """Return a float mask that is 1 on bins within ``radius`` of zero frequency."""
    # TODO 1 (student): bin u of an H-point DFT has frequency min(u, H - u)
    # (the top half of the array holds the negative frequencies). Use that
    # wrapped distance on both axes, take the Euclidean distance and keep the
    # bins where it is <= radius. Return float64, not bool.
    height, width = shape
    u = np.arange(height)
    v = np.arange(width)
    freq_rows = np.minimum(u, height - u).astype(np.float64)[:, np.newaxis]
    freq_cols = np.minimum(v, width - v).astype(np.float64)[np.newaxis, :]
    distance = np.sqrt(freq_rows**2 + freq_cols**2)
    return (distance <= radius).astype(np.float64)


def split_plane(plane, radius, engine):
    """Return (low, high): the ideal low-pass and high-pass parts of one plane."""
    # TODO 2 (student): transform once, multiply the spectrum by the mask and by
    # (1 - mask), inverse-transform each product, keep the real parts.
    plane = np.asarray(plane, dtype=np.float64)
    spectrum = transform_2d(plane, engine)
    mask = radial_mask(plane.shape, radius)
    low = inverse_2d(spectrum * mask, engine).real
    high = inverse_2d(spectrum * (1.0 - mask), engine).real
    return low, high


def split_image(image, radius, engine):
    """Apply split_plane to a grayscale or RGB image; return (low, high) with the original shape."""
    # TODO 3 (student): grayscale -> return the pair directly. RGB -> one pair
    # per channel; stack the three lows along the last axis, and the three
    # highs likewise, then return the two stacked arrays.
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 2:
        return split_plane(image, radius, engine)
    if image.ndim == 3 and image.shape[2] == 3:
        pairs = [split_plane(image[:, :, c], radius, engine) for c in range(image.shape[2])]
        low = np.stack([pair[0] for pair in pairs], axis=-1)
        high = np.stack([pair[1] for pair in pairs], axis=-1)
        return low, high
    raise ValueError("images must be grayscale or RGB")


def _make_engine(name):
    """Provided command-line engine selection."""
    if name == "dft":
        return DFTAnalyzer()
    if name == "fft":
        return FFTTransformer()
    if name == "arbitrary":
        return ArbitraryLengthFFT()
    raise ValueError("unknown engine: %r" % name)


def _resolve(path):
    """Provided: paths such as images/skyline256.png are relative to the offline folder."""
    return path if os.path.isabs(path) else os.path.join(OFFLINE_DIR, path)


def _reference_low(plane, radius, engine):
    """Provided oracle: the same low-pass built from a centred mask that is rolled back."""
    height, width = plane.shape
    rows = (np.arange(height) - height // 2)[:, np.newaxis]
    cols = (np.arange(width) - width // 2)[np.newaxis, :]
    centred = (np.sqrt(rows.astype(np.float64)**2 + cols.astype(np.float64)**2) <= radius)
    mask = np.roll(centred.astype(np.float64), (-(height // 2), -(width // 2)), axis=(0, 1))
    return inverse_2d(transform_2d(plane, engine) * mask, engine).real


def run(image_path, radius, engine_name, out_dir, color=False):
    """Provided runner: complementarity, an independent mask, and Parseval."""
    engine = _make_engine(engine_name)
    image = load_image(_resolve(image_path), as_gray=not color)
    low, high = split_image(image, radius, engine)

    complement_error = float(np.max(np.abs(low + high - image)))
    if image.ndim == 2:
        reference = _reference_low(image, radius, engine)
    else:
        reference = np.stack([_reference_low(image[:, :, c], radius, engine)
                              for c in range(image.shape[2])], axis=-1)
    mask_error = float(np.max(np.abs(low - reference)))
    # Parseval: the energy fraction kept must be the same in both domains.
    first = image if image.ndim == 2 else image[:, :, 0]
    spectrum = transform_2d(first, engine)
    kept = radial_mask(first.shape, radius)
    fraction_space = float(np.sum(split_plane(first, radius, engine)[0]**2) / np.sum(first**2))
    fraction_freq = float(np.sum(np.abs(spectrum * kept)**2) / np.sum(np.abs(spectrum)**2))
    parseval_error = abs(fraction_space - fraction_freq)
    verdict = ("MATCH" if max(complement_error, mask_error, parseval_error) <= 1e-9
               else "MISMATCH")

    os.makedirs(out_dir, exist_ok=True)
    save_image(low, os.path.join(out_dir, "low_pass.png"))
    save_image(np.clip(0.5 + 2.0 * high, 0.0, 1.0), os.path.join(out_dir, "high_pass.png"))
    save_comparison(
        [image, low, np.clip(0.5 + 2.0 * high, 0.0, 1.0)],
        ["original", "ideal low-pass (r = %d)" % radius, "ideal high-pass (rest)"],
        os.path.join(out_dir, "comparison.png"),
        suptitle="Ideal frequency split, engine=%s" % engine_name,
    )
    write_report(os.path.join(out_dir, "report.txt"), [
        "Practice B5 -- ideal low-pass / high-pass split",
        "image                : %s" % image_path,
        "image shape          : %s" % (image.shape,),
        "radius (bins)        : %d" % radius,
        "engine               : %s" % engine_name,
        "energy kept, spatial : %.6f" % fraction_space,
        "energy kept, spectral: %.6f  (Parseval)" % fraction_freq,
        "max |low + high - image| : %.3e" % complement_error,
        "max |low - reference low| : %.3e" % mask_error,
        "verification         : %s" % verdict,
    ])
    print("verification:", verdict, "(complement %.3e, mask %.3e, parseval %.3e)"
          % (complement_error, mask_error, parseval_error))
    print("wrote outputs to", out_dir)
    if verdict != "MATCH":
        raise RuntimeError("ideal filter split failed verification")
    return low, high


def main():
    parser = argparse.ArgumentParser(description="Ideal low-pass / high-pass split")
    parser.add_argument("--image", default="images/skyline256.png")
    parser.add_argument("--radius", type=int, default=20)
    parser.add_argument("--engine", choices=["dft", "fft", "arbitrary"], default="fft")
    parser.add_argument("--color", action="store_true")
    parser.add_argument("--out-dir", default=os.path.join(PRACTICE_DIR, "outputs", "b5"))
    args = parser.parse_args()
    run(args.image, args.radius, args.engine, args.out_dir, color=args.color)


if __name__ == "__main__":
    main()
