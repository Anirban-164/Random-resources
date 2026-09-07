# Practice Onlines: DFT & FFT

**Ten problems** in the format of Online 4 (A1/A2, B1/B2)

- **Task A:** five problems on big-integer multiplication
- **Task B:** five problems on image convolution

## How to Use This Set

- Templates are in `practice/problems/`; full solutions are in `practice/solutions/`.
- Each template has exactly three `TODO` blocks and a provided runner with an independent oracle that prints `verification: MATCH` or `MISMATCH`, exactly like the real sheets.
- Run a template unmodified first and watch which `TODO` it stops at. Then fill the three blocks.
- Then run it, and for Task B run it again with `--color`.
- Every file imports your own `transforms.py`, `bigmul.py`, and `image_conv.py`. The only difference from a real online is the two `sys.path` lines at the top, so the files can run from the `practice/` folder instead of being copied next to the offline files.
- The real sheet's command is `python3 ...`; on your machine it is `python ...`.
- Outputs land in `practice/outputs/<problem>/`.
- Every report must end with `verification: MATCH`; an error above \(10^{-9}\) means a bug.
- Rules are as in the real onlines: NumPy array arithmetic and the functions the template imports only; `numpy.fft`, SciPy transforms, and library convolution routines are prohibited; Python big integers only in the verification line.
- Suggested order: fill **TODO 3 (dispatch/glue)** first, then **TODO 1 (helper)**, then **TODO 2 (the core)**.
- **Time yourself: 40 minutes each.**

> Solutions in plain language begin on page 12.


## Problem A1 — Product of Three Integers

**Subsections:** A1, A2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `a1_triple_product.py`

The convolution theorem does not care how many factors there are. The digit array of \(a\cdot b\cdot c\) is the linear convolution \(a*b*c\), and in the frequency domain that is the pointwise product of three spectra.

Three forward transforms, one triple product, one inverse transform.

You are given two operands from an offline input file and a third reproducible operand in `a1_triple_product.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify `transforms.py`, `bigmul.py`, or any other offline file.

### Mathematical Model

Let \(a,b,c\) be little-endian limb arrays of lengths \(n,q,r\) in base \(B\), with spectra \(A,B,C\) at a common length \(N\).

Their product has \(n+q+r-2\) coefficients:

\[
P[k]=A[k]B[k]C[k],\qquad p=\operatorname{IDFT}\{P\},
\]

with

\[
N\ge n+q+r-2.
\]

A coefficient of a triple product is a sum of roughly \(n^2/2\) products of three limbs, so it can reach approximately

\[
rac{n^2}{2}(B-1)^3.
\]

With \(B=10^4\), that exceeds the \(2^{53}\) mantissa bound for the provided inputs. The template therefore fixes `TRIPLE_BASE_DIGITS = 2`, i.e. \(B=10^2\).

Pass that base to both `to_limbs` and `from_limbs`. Signs stay outside the transform and multiply.

### Tasks

#### 1. Complete Choose Transform Length — 2 Marks

Return the minimum linear length for three factors, rounded to what the selected engine supports.

#### 2. Complete Multiply Three Transform — 5 Marks

Zero-pad, transform each operand once, multiply the three spectra, perform exactly one inverse transform, keep the real part, crop, and round to `int64`.

#### 3. Complete Multiply Three — 3 Marks

Convert with the triple base, combine the signs, carry with the same base, and return the product string.

### Running and Verification

```bash
python a1_triple_product.py --input inputs/3.txt --third-digits 2000 --engine fft
```

The runner writes `product.txt` and `report.txt` and compares against `int(a) * int(b) * int(c)` — the only permitted use of Python's big integers.

The report must show:

```text
verification: MATCH
```

Negative operands (`inputs/1.txt`) must also work.

---


## Problem A2 — \(ab+cd\) With One Inverse Transform

**Subsections:** A1, A2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `a2_sum_of_products.py`

The DFT is linear: \(\operatorname{DFT}\{x+y\}=X+Y\). The sum of two products therefore needs four forward transforms but only one inverse transform — add the two product spectra first, then invert once.

You are given four reproducible non-negative operands in `a2_sum_of_products.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

For limb arrays \(a,b,c,d\) with spectra \(A,B,C,D\) at a common length \(N\),

\[
S[k]=A[k]B[k]+C[k]D[k],\qquad
s=\operatorname{IDFT}\{S\},
\]

with

\[
N\ge \max(n_a+n_b-1,\;n_c+n_d-1).
\]

The coefficients of \(s\) are the un-carried digits of \(ab+cd\); one carry sweep turns them into the decimal answer.

All operands are non-negative. A signed sum can produce negative coefficients, which the offline's `from_limbs` cannot carry, so a negative operand must raise `ValueError`.

### Tasks

#### 1. Complete Choose Transform Length — 2 Marks

One length must hold the longer of the two products; round to what the engine supports.

#### 2. Complete Sum of Products Transform — 5 Marks

Pad and transform all four arrays, form \(AB+CD\), perform exactly one inverse transform, keep the real part, crop to the longer linear length, and round.

#### 3. Complete Sum of Products — 3 Marks

Convert, reject negatives, convolve, carry, and return the decimal string.

### Running and Verification

```bash
python a2_sum_of_products.py --digits 1500 --seed 11 --engine fft
```

The runner compares against `int(a)*int(b) + int(c)*int(d)`.

The report must show `verification: MATCH`.

> Two inverse transforms is a wrong implementation even if it matches.

---


## Problem A3 — Circular Convolution and Wraparound

**Subsections:** A1, A2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `a3_circular_wraparound.py`

A length-\(N\) transform never computes linear convolution. It computes circular convolution of period \(N\): anything that would land past slot \(N-1\) is added back onto slot \(mmod N\). The padding rule exists only to make the two coincide.

In this problem you compute the wrong thing on purpose and prove exactly how it is wrong.

You are given two reproducible operands in `a3_circular_wraparound.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

With linear convolution \(\ell=a*b\) of length \(n+q-1\) and any \(N\ge\max(n,q)\),

\[
(a\circledast_N b)[m]
=
\sum_{k\equiv m\pmod N}\ell[k],
\qquad m=0,\ldots,N-1.
\]

The left side is what a length-\(N\) transform returns; the right side is the linear result folded onto \(N\) slots. They must agree exactly, integer for integer.

### Tasks

#### 1. Complete Short Length — 2 Marks

Return \(\max(n,q)\) rounded to what the engine supports — enough room for either input, deliberately too little for the product.

#### 2. Complete Circular Convolve — 4 Marks

Pad both arrays to exactly \(N\), transform, multiply, inverse-transform, keep the real part, round, and return all \(N\) slots.

#### 3. Complete Fold — 4 Marks

Wrap a linear result onto \(N\) slots: `out[m % N] += linear[m]`.

### Running and Verification

```bash
python a3_circular_wraparound.py --digits 120 --seed 5 --engine fft
```

The runner checks \(\max_m |circular[m]-folded[m]|=0\) and that the padded route still equals `int(a) * int(b)`.

The report also prints the plausible-looking wrong number the short transform produces next to the correct one. It must show `verification: MATCH`.

---


## Problem A4 — Shift Detection by Cross-Correlation

**Subsections:** A1, A2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `a4_shift_correlation.py`

Correlation slides one sequence past another and measures how well they line up at each offset. It is convolution with a time-reversed sequence, and reversing a real sequence conjugates its spectrum — so correlation costs the same three transforms as multiplication, with one conjugate.

You are given a number \(a\) and \(b=a\cdot B^s\) (the same limbs moved up by \(s\) positions) in `a4_shift_correlation.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

For limb arrays \(a\) (length \(n\)) and \(b\) (length \(q\)) the cross-correlation at lag \(k\) is

\[
c[k]=\sum_i a[i]b[i+k].
\]

With the conjugate convention used by the template, the spectral product is

\[
A^st B,
\qquad N\ge n+q-1.
\]

Lag \(k\) is stored at index \(kmod N\); negative lags sit at the end of the array.

Because \(b\) is shifted by \(s\), the largest correlation occurs at \(k=s\) and equals

\[
\sum_i a[i]^2,
\]

the energy of \(a\).

### Tasks

#### 1. Complete Choose Transform Length — 2 Marks

Every lag needs its own slot: the linear-convolution rule applies unchanged.

#### 2. Complete Cross Correlate — 5 Marks

Pad, transform both, multiply \(A^st\) by \(B\), perform one inverse transform, keep the real part, round to `int64`, and return the full length-\(N\) array and \(N\).

#### 3. Complete Find Shift — 3 Marks

Correlate the limb magnitudes, locate the maximum, unwrap an index above \(N/2\) to a negative lag, and return the lag, peak value, and \(N\).

### Running and Verification

```bash
python a4_shift_correlation.py --digits 400 --shift 7 --engine fft
```

The runner recomputes every lag with the defining double loop, checks the detected shift, and checks that the peak equals the energy of \(a\).

The report must show `verification: MATCH`.

---


## Problem A5 — Fourth Power by Repeated Squaring

**Subsections:** A1, A2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `a5_fourth_power.py`

Squaring is multiplication with one operand, so it needs only one forward transform: \(A\cdot A\). A fourth power is a square of a square.

The catch is that between the two squarings, the coefficients that come back from the first are not digits yet, and squaring un-carried coefficients breaks the mantissa bound.

You are given the first operand of an offline input file in `a5_fourth_power.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

For an \(n\)-limb array \(a\) with spectrum \(A\),

\[
a^2=\operatorname{IDFT}\{A\cdot A\}
\]

with \(2n-1\) coefficients, and

\[
a^4=\left(\operatorname{carry}(a^2)ight)^2.
\]

The un-carried coefficients of \(a^2\) can reach roughly

\[
n(B-1)^2pprox10^{11}.
\]

Squaring them directly would produce sums near \(10^{25}\), far past \(2^{53}\). Carrying first and re-splitting into limbs restores values below \(B\), making the second squaring safe.

An even power is never negative.

### Tasks

#### 1. Complete Square Length — 2 Marks

A square has \(2n-1\) coefficients; round to what the engine supports.

#### 2. Complete Square Transform — 4 Marks

One forward transform, square the spectrum, one inverse, real part, crop, and round. Two forward transforms is wrong.

#### 3. Complete Fourth Power — 4 Marks

Square, carry into a proper number, re-split into limbs, square again, carry, and return the string together with both transform lengths and both limb counts.

### Running and Verification

```bash
python a5_fourth_power.py --input inputs/3.txt --engine fft
```

The runner compares against `int(a) ** 4`. The report must show `verification: MATCH`.

---


## Problem B1 — Shifting an Image With a Phase Ramp

**Subsections:** B1, B2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `b1_spectral_shift.py`

Delaying a signal does not change how much of each frequency it contains, only where each oscillation sits — its phase. The shift theorem makes that exact: a delay of \(s\) samples multiplies the spectrum by a linear phase ramp. In two dimensions the row and column ramps simply add in the exponent.

You are given an image and a shift in `b1_spectral_shift.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify `transforms.py`, `image_conv.py`, or any other offline file.

### Mathematical Model

For an \(H	imes W\) plane with spectrum \(F[u,v]\) and integer shifts \((d_r,d_c)\),

\[
F_{	ext{shifted}}[u,v]
=
F[u,v]e^{-2\pi j\left(rac{u\,d_r}{H}+rac{v\,d_c}{W}ight)},
\]

for \(u=0,\ldots,H-1,\;v=0,\ldots,W-1\).

No padding is used, so the shift wraps around the edges: the result is a circular shift, exactly what `np.roll` computes. Negative shifts are allowed.

### Tasks

#### 1. Complete Phase Ramp — 3 Marks

Build the \(H	imes W\) complex multiplier from the two index vectors.

#### 2. Complete Shift Plane — 4 Marks

Transform the plane, multiply by the ramp, perform exactly one inverse 2D transform, and keep the real part.

#### 3. Complete Shift Image — 3 Marks

One plane for grayscale, three planes independently for RGB, with the original shape preserved.

### Running and Verification

```bash
python b1_spectral_shift.py --image images/skyline256.png --rows 37 --cols -21 --engine fft
python b1_spectral_shift.py --color
```

The runner compares against

```python
np.roll(image, (rows, cols), axis=(0, 1))
```

and writes `shifted.png`, `comparison.png`, and `report.txt`.

The report must show `verification: MATCH`.

Both grayscale and RGB inputs must work.

---


## Problem B2 — Unsharp Masking in the Frequency Domain

**Subsections:** B1, B2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `b2_unsharp_mask.py`

A blur removes detail; subtracting the blur from the original isolates that detail; adding some of it back sharpens the picture. That is unsharp masking, and every step of it is a convolution or a sum, so the whole thing is one expression in the frequency domain.

You are given an image and a Gaussian kernel in `b2_unsharp_mask.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

With the padded spectra \(P\) (image) and \(G\) (kernel), the centred impulse spectrum \(\Delta\) and a sharpening amount \(\lambda\),

\[
y=x+\lambda(x-x*g)
\]

and

\[
Y=P\Delta+\lambda(P\Delta-PG)
=P\left(\Delta+\lambda(\Delta-G)ight).
\]

Use one inverse transform and the usual linear-convolution crop starting at

\[
\left(\left\lfloorrac{K_r}{2}ightfloor,\left\lfloorrac{K_c}{2}ightflooright).
\]

An \(R	imes C\) image and a \(K_r	imes K_c\) kernel need at least

\[
(R+K_r-1)	imes(C+K_c-1)
\]

samples. A radix-2 FFT needs each dimension raised to the next power of two.

### Tasks

#### 1. Complete Choose Transform Shape — 2 Marks

Determine the minimum linear-convolution dimensions, then apply the engine's restriction.

#### 2. Complete Sharpen Plane — 5 Marks

Pad plane and kernel, transform, form \(Y\), perform exactly one inverse 2D transform, keep the real part, and crop.

#### 3. Complete Sharpen Image — 3 Marks

Support grayscale or RGB dispatch while preserving the original shape.

### Running and Verification

```bash
python b2_unsharp_mask.py --image images/skyline256.png --kernel-size 21 --amount 1.5 --engine fft
python b2_unsharp_mask.py --color
```

The runner computes

\[
	ext{image}+	ext{amount}\cdot
(	ext{image}-\operatorname{convolve}(	ext{image},	ext{kernel}))
\]

as an independent oracle. The report must show `verification: MATCH`.

---


## Problem B3 — Deblurring by Inverse Filtering

**Subsections:** B1, B2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `b3_deblur.py`

If a blur is a pointwise multiplication in the frequency domain, undoing it is a pointwise division — as long as nothing is divided by zero.

A circular blur by a small Gaussian can be undone exactly; the same idea applied to a large kernel amplifies rounding noise into garbage, and you will see why.

You are given a circularly blurred image and the kernel that blurred it in `b3_deblur.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

The offline's circular path computes

\[
Y=X\cdot G_w,
\]

where \(G_w\) is the spectrum of the kernel wrapped around the origin (centre tap at \((0,0)\)).

Then

\[
X[u,v]=
egin{cases}
Y[u,v]/G_w[u,v], & |G_w[u,v]|>arepsilon,\
0, & 	ext{otherwise},
\end{cases}
\]

and

\[
x=\operatorname{Re}\operatorname{IDFT}\{X\}.
\]

Rounding noise of size \(10^{-16}\) in \(Y\) becomes \(10^{-16}/|G_w|\) in \(X\).

A \(5	imes5\) Gaussian keeps \(|G_w|\ge4	imes10^{-3}\), while a \(31	imes31\) Gaussian has bins near \(10^{-50}\).

### Tasks

#### 1. Complete Wrapped Kernel Spectrum — 3 Marks

Embed the kernel at the origin of a zero array of the plane's shape, roll by \((-\lfloor K_r/2floor,-\lfloor K_c/2floor)\), then transform.

#### 2. Complete Deblur Plane — 4 Marks

Divide only where \(|G_w|>arepsilon\), zero elsewhere, perform one inverse transform, and keep the real part. Never divide by a vanishing bin.

#### 3. Complete Deblur Image — 3 Marks

Support grayscale or RGB dispatch while preserving the original shape.

### Running and Verification

```bash
python b3_deblur.py --image images/skyline256.png --kernel-size 5 --engine fft
python b3_deblur.py --color
```

The runner blurs with `convolve_image(..., circular=True)`, calls your deblur, and compares with the original image.

The report must show `verification: MATCH`.

Afterwards try:

```bash
python b3_deblur.py --image images/skyline256.png --kernel-size 31 --engine fft
```

and read the `smallest |G| bin` line of the report.

---


## Problem B4 — Phase Correlation

**Subsections:** B1, B2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `b4_phase_correlation.py`

Online B showed that phase carries the structure of an image. Phase correlation uses that: if two images differ only by a shift, their spectra differ only by a phase ramp, and dividing that ramp out of the cross-power spectrum leaves a pure impulse whose position is the shift.

You are given an image and its shifted copy in `b4_phase_correlation.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

For planes \(a\) and \(b=\operatorname{roll}(a,(d_r,d_c))\) with spectra \(A\) and \(B\), form the cross-power spectrum by normalising

\[
A^st B
\]

to unit magnitude at reliable bins.

Equivalently, for reliable bins,

\[
R[u,v]
=
rac{A^st[u,v]B[u,v]}
{|A[u,v]B[u,v]|}
=
e^{-2\pi j\left(rac{u\,d_r}{H}+rac{v\,d_c}{W}ight)}.
\]

Then

\[
r=\operatorname{Re}\operatorname{IDFT}\{R\}
=
\delta[m-d_r,n-d_c].
\]

Bins with \(|AB|\learepsilon\) must be set to zero and never divided.

The peak of \(r\) at \((m,n)\) gives the shift. An index above \(H/2\) (or \(W/2\)) represents a negative shift. For RGB, sum the three channel surfaces before locating the peak.

### Tasks

#### 1. Complete Unit Cross Power — 3 Marks

Form \(A^st B\), normalise reliable bins to unit magnitude, zero the rest, and never divide by zero.

#### 2. Complete Correlation Surface — 4 Marks

Transform both planes, take the unit cross-power spectrum, perform one inverse transform, and keep the real part.

#### 3. Complete Find Shift — 3 Marks

Support grayscale or RGB dispatch, locate the peak, unwrap it, and return `(rows, cols, surface)`.

### Running and Verification

```bash
python b4_phase_correlation.py --image images/skyline256.png --rows 37 --cols -21 --engine fft
python b4_phase_correlation.py --color
```

The runner shifts with `np.roll`, checks the detected shift, and checks that the surface is a unit impulse to \(10^{-9}\).

The report must show `verification: MATCH`.

---


## Problem B5 — Ideal Low-Pass / High-Pass Split

**Subsections:** B1, B2  
**Total Marks:** 10  
**Total Time:** 40 Minutes  
**Template:** `b5_ideal_filter.py`

Low frequencies describe broad, slow variation; high frequencies describe edges and texture.

An ideal filter keeps every bin inside a radius of zero frequency and discards the rest — but in a DFT array zero frequency is at index 0 and the negative frequencies live at the top of the array, so the distance must be measured with wrapped indices.

You are given an image and a radius in `b5_ideal_filter.py`.

> **Important:** Complete only the three blocks marked `TODO`. Do not modify any offline file.

### Mathematical Model

Bin \(u\) of an \(H\)-point DFT has frequency

\[
f_u=\min(u,H-u),
\]

and similarly

\[
f_v=\min(v,W-v).
\]

Define

\[
M[u,v]=
egin{cases}
1, & \sqrt{f_u^2+f_v^2}\le r,\
0, & 	ext{otherwise}.
\end{cases}
\]

Then

\[
x_{	ext{low}}=\operatorname{Re}\operatorname{IDFT}\{FM\},
\]

\[
x_{	ext{high}}=\operatorname{Re}\operatorname{IDFT}\{F(1-M)\}.
\]

Linearity gives

\[
x_{	ext{low}}+x_{	ext{high}}=x,
\]

and Parseval's theorem says the fraction of energy kept is the same whether measured on pixels or on spectrum bins.

### Tasks

#### 1. Complete Radial Mask — 3 Marks

Use wrapped frequency distance on both axes, apply the Euclidean radius test, and return `float64`.

#### 2. Complete Split Plane — 4 Marks

One forward transform, two masked inverse transforms, real parts, and return `(low, high)`.

#### 3. Complete Split Image — 3 Marks

Grayscale returns the pair directly. RGB splits each channel, stacks the three lows and the three highs separately, and returns both.

### Running and Verification

```bash
python b5_ideal_filter.py --image images/skyline256.png --radius 20 --engine fft
python b5_ideal_filter.py --color
```

The runner checks

\[
\max |x_{	ext{low}}+x_{	ext{high}}-x|,
\]

compares the low-pass result with one built from an independently constructed centred-then-rolled mask, and checks Parseval.

The report must show `verification: MATCH`.

---


# Solutions in Plain Language

Every problem here is the same five-step pipeline you already wrote in the offline:

\[
oxed{	ext{pad}ightarrow	ext{transform}ightarrow
	ext{do something simple to the spectrum}ightarrow
	ext{inverse transform once}ightarrow
	ext{real part, crop, round}}
\]

What changes is only the “something simple”.

Full code is in `practice/solutions/`; below is the idea behind each, written for a first-time reader.

---

## The Three Facts Everything Rests On

### 1. Convolution Becomes Multiplication

The DFT rewrites a signal as a sum of complex exponentials. Convolution scales each exponential and never mixes it with its neighbours, so after the transform the tangled sum turns into \(N\) independent multiplications.

Hence

\[
a*b\leftrightarrow A\cdot B
\]

and with more factors

\[
a*b*c\leftrightarrow A\cdot B\cdot C.
\]

### 2. The DFT Is Linear

\[
\operatorname{DFT}\{x+y\}=X+Y
\]

and

\[
\operatorname{DFT}\{\lambda x\}=\lambda X.
\]

So any expression built from sums and convolutions can be assembled entirely in the frequency domain and brought back with a single inverse transform.

### 3. A Shift Is a Phase Ramp

Delaying \(x[n]\) by \(s\) samples turns \(X[u]\) into

\[
X[u]e^{-2\pi jus/N}.
\]

The same magnitudes remain, but phases rotate.

Reversing a real sequence in time conjugates its spectrum.

### Engineering Rule

A length-\(N\) transform computes circular convolution, so pad to at least the linear length or the tail wraps onto the head.

---

## A1 — Product of Three Integers

### Idea

Use Fact 1 with three factors: transform \(a,b,c\) once each, multiply the three spectra bin by bin, and invert once.

### Why the Base Drops to \(10^2\)

Every coefficient comes back as a floating-point number that you round. Rounding only recovers the correct integer if that integer is representable.

Doubles hold integers exactly up to

\[
2^{53}pprox9	imes10^{15}.
\]

A coefficient of \(abc\) can reach roughly

\[
rac{n^2}{2}(B-1)^3.
\]

With \(B=10^4\) and a thousand limbs this is around \(10^{18}\), too large. With \(B=10^2\) it is around \(10^{12}\), which is safe.

### Steps

**TODO 1:** `need = n + q + r - 2`, rounded to a power of two unless the engine is arbitrary.

**TODO 2:** Three zero-padded arrays, three `engine.transform` calls, one product, one `engine.inverse`, `.real`, crop to `need`, `np.rint`.

**TODO 3:** `to_limbs(text, 2)` three times, multiply the signs, then `from_limbs(sign, coeffs, 2)`.

### Pitfall

Forgetting the base in `from_limbs` makes the carry sweep use \(10^4\) on base-\(10^2\) limbs and prints a wrong number with the right length.

---

## A2 — \(ab+cd\) With One Inverse

### Idea

By linearity,

\[
\operatorname{DFT}\{a*b+c*d\}=AB+CD.
\]

So use four forward transforms, one addition, and one inverse.

Doing two inverses and adding the results also gives the right number, but it misses the point and is marked wrong.

### Why One \(N\) Is Enough

Both products must fit without wrapping, so \(N\) must be at least the longer linear length. Padding the shorter product with zeros costs nothing.

### Why Non-Negative Only

Both \(ab\) and \(cd\) are non-negative, so their sum's coefficients are non-negative and the carry sweep works. A negative operand could produce negative coefficients, which causes the offline `from_limbs` to fail, hence `ValueError`.

### Steps

**TODO 1:** `max(la + lb - 1, lc + ld - 1)`, then engine rounding.

**TODO 2:** Pad four arrays, transform four, form `A*B + C*D`, and inverse once.

**TODO 3:** Convert, check signs, convolve, then `from_limbs(1, coeffs)`.

---

## A3 — Circular Convolution and Wraparound

### Idea

A length-\(N\) transform treats the world as a circle of \(N\) slots. A coefficient that should land in slot \(m\ge N\) instead lands at `m % N`.

This is exact arithmetic, but of the wrong quantity.

### Steps

**TODO 1:** `max(la, lb)`, rounded by the engine — enough room for the inputs but not for the product.

**TODO 2:** Same transform/multiply/inverse route as multiplication, except \(N\) is deliberately short and nothing is cropped.

**TODO 3:** Loop over the linear result and add into `out[m % N]`.

### What to Notice

The wrapped product has fewer digits and a completely different start. Nothing crashes and no warning appears.

This is the silent failure the padding rule prevents.

---

## A4 — Shift Detection by Cross-Correlation

### Idea

Correlation

\[
c[k]=\sum_i a[i]b[i+k]
\]

asks how well \(b\) matches \(a\) when slid by \(k\).

It is convolution with a reversed sequence. Reversing a real sequence conjugates its spectrum, so one conjugate is the key difference from ordinary multiplication.

### Why the Peak Is at \(s\)

Appending \(4s\) decimal zeros multiplies by \(10^{4s}=B^s\), which moves every limb up by \(s\) positions.

At shift \(s\), every limb lines up with itself, so the sum of squares is maximal. Every other lag mixes different limbs and is smaller.

### Negative Lags

Lag \(k\ge0\) sits at index \(k\). Lag \(k<0\) sits at index \(N+k\).

If the peak index is above \(N/2\), it is a negative lag, so subtract \(N\).

### Steps

**TODO 1:** `la + lb - 1`, then engine rounding.

**TODO 2:**

```python
np.conj(engine.transform(fa)) * engine.transform(fb)
```

then inverse, `.real`, `np.rint`.

**TODO 3:** `np.argmax`, unwrap, return.

---

## A5 — Fourth Power by Repeated Squaring

### Idea

\[
a^2=\operatorname{IDFT}\{A\cdot A\}
\]

needs one forward transform, not two.

Then

\[
a^4=(a^2)^2.
\]

### Why Carry in Between

After the first squaring, coefficients can be around

\[
n(B-1)^2pprox10^{11}.
\]

They are correct, but they are not proper base-\(B\) limbs. Squaring them again could produce coefficients around \(10^{25}\), beyond the mantissa.

Carry first and re-split into limbs. The second squaring is then safe.

### Steps

**TODO 1:** `2*n - 1`, rounded by the engine.

**TODO 2:** One `engine.transform`, `A*A`, one inverse, crop, round.

**TODO 3:** Square, carry into a proper number, convert back to limbs, square again, carry.

---

## B1 — Shifting an Image With a Phase Ramp

### Idea

Moving the picture down by \(d_r\) rows and right by \(d_c\) columns multiplies bin \((u,v)\) by

\[
e^{-2\pi j(ud_r/H+vd_c/W)}.
\]

Magnitudes are untouched; only phases change.

### Why It Wraps

The DFT treats the image as periodic, so content pushed off the bottom re-enters at the top. That is exactly `np.roll`, which is why it is the oracle.

### Steps

**TODO 1:** Two index vectors `u[:, None]` and `v[None, :]`, then one `np.exp`.

**TODO 2:** Transform 2D, multiply, inverse 2D, `.real`.

**TODO 3:** Standard grayscale/RGB dispatch.

### Pitfall

A plus sign in the exponent shifts the other way; the oracle catches it immediately.

---

## B2 — Unsharp Masking

### Idea

Detail is

\[
x-x*g,
\]

and sharpened is

\[
x+\lambda(x-x*g).
\]

In the frequency domain, the blur is \(PG\) and the unblurred image is \(P\Delta\), where \(\Delta\) is the spectrum of an impulse sitting at the kernel centre.

Thus

\[
Y=P\Delta+\lambda(P\Delta-PG)
=P(\Delta+\lambda(\Delta-G)).
\]

### Steps

**TODO 1:** Exactly the transform-shape logic from the hybrid-image problem.

**TODO 2:** Pad plane and kernel, transform both, form the formula, inverse once, `.real`, crop at `(kh//2, kw//2)`.

**TODO 3:** Standard dispatch.

### Pitfall

Using `1` instead of \(\Delta\) for the original image puts the impulse at the corner instead of the kernel centre, displacing the output.

---

## B3 — Deblurring by Inverse Filtering

### Idea

A circular blur is

\[
Y=XG_w
\]

bin by bin, so

\[
X=Y/G_w.
\]

Division is only allowed where \(G_w\) is not numerically zero.

### Why the Kernel Must Be Wrapped

The circular path puts the kernel centre at index \((0,0)\) with `np.roll`. The spectrum used for deblurring must use the identical placement, or the result is shifted by about half the kernel.

### Why Big Kernels Cannot Be Inverted

A blur kills high frequencies, making \(|G_w|\) tiny there. Dividing by a tiny number amplifies rounding noise.

For a \(5	imes5\) Gaussian, the smallest bin is about \(4	imes10^{-3}\), so noise grows only about 250x.

For a \(31	imes31\) Gaussian, some bins are around \(10^{-50}\); bins near the threshold can amplify noise enormously.

### Steps

**TODO 1:** zeros of the plane's shape, kernel at top-left, `np.roll` by `(-(kh//2), -(kw//2))`, transform 2D.

**TODO 2:** Mask `|Gw| > eps`, divide only there, zeros elsewhere, one inverse, `.real`.

**TODO 3:** Standard dispatch.

---

## B4 — Phase Correlation

### Idea

If \(b\) is shifted, then its spectrum differs from \(a\)'s by a phase ramp.

The cross-power spectrum divides out the magnitude and leaves only the ramp. The inverse transform becomes a single impulse at the shift.

### Why Normalise

Without normalisation the surface is the autocorrelation, a broad blob that is still peaked correctly. Keeping only phase produces the sharp impulse.

### Steps

**TODO 1:** Apply the unit-phase pattern to `np.conj(A) * B`, using zeros — not ones — for unreliable bins.

**TODO 2:** Two transforms, TODO 1, one inverse 2D transform, `.real`.

**TODO 3:** For RGB, sum the channel surfaces, then `np.argmax` + `np.unravel_index`, and unwrap indices above half.

### Pitfall

Using \(AB^st\) instead of \(A^st B\) puts the peak at \((-d_r,-d_c)\).

---

## B5 — Ideal Low-Pass / High-Pass Split

### Idea

Multiply the spectrum by a mask that is 1 near zero frequency and 0 far from it.

- \(M\): low-pass
- \(1-M\): high-pass

Because

\[
FM+F(1-M)=F,
\]

the two parts add back to the original exactly.

### Why Wrapped Distances

For an \(H\)-point DFT, bin \(0\) is zero frequency, bin \(1\) is the slowest positive oscillation, and bin \(H-1\) is the slowest in the other direction.

Thus the distance is

\[
\min(u,H-u),
\]

not simply \(u\).

### Why Parseval Holds

The DFT is an orthogonal change of basis up to a normalisation factor, so

\[
\sum|x|^2=rac{1}{N}\sum|X|^2.
\]

The fraction of energy kept is therefore the same in pixel and frequency space.

### Steps

**TODO 1:** `np.minimum(u, H - u)`, same for columns, Euclidean distance, `<= radius`, `.astype(float64)`.

**TODO 2:** One forward transform, two masked inverse transforms, `.real` on both.

**TODO 3:** For grayscale, return the pair. For RGB, collect `(low, high)` per channel, then stack lows and highs separately.

### Pitfall

Returning a Boolean mask makes `1 - mask` behave differently from a numeric complement. Cast to `float64`.

---

# The Dispatch You Will Write Every Time

For a function returning a single image:

```python
if image.ndim == 2:
    return f(image, ...)

if image.ndim == 3 and image.shape[2] == 3:
    planes = [f(image[:, :, c], ...) for c in range(image.shape[2])]
    return np.stack(planes, axis=-1)

raise ValueError("images must be grayscale or RGB")
```

When `f` returns a pair:

```python
if image.ndim == 2:
    return f(image, ...)

if image.ndim == 3 and image.shape[2] == 3:
    pairs = [f(image[:, :, c], ...) for c in range(image.shape[2])]
    firsts, seconds = zip(*pairs)
    return (
        np.stack(firsts, axis=-1),
        np.stack(seconds, axis=-1),
    )

raise ValueError("images must be grayscale or RGB")
```

> Type this from memory before the online starts.

