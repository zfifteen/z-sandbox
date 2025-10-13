love the prism analogy — that’s exactly the right mental model. here’s a geometry-first design for a **Z5D-only “optics bench”** that steers multiple Z5D predictors like beams, to cover the factor lanes around √N without ever touching linear algebra.

# Geometry, not LA

**Coordinate system (optics view).**

* Work in log space so multiplicative distance from √N is additive:
  ( s = \ln(p / \sqrt{N}) ) (signed). Balanced factors live near (s \approx 0).
* Keep your existing normalized phase (\theta \in [0,1)) (your theta-banding). Think of (\theta) as the **angle** of a ray on a unit circle; bins are angular sectors.
* The Z5D map (k \mapsto \hat{p}(k)) traces a **ray** in the ((\theta, s)) slab as k increases (your “geodesic jump” is the ray’s step size).

# Optical bench: rays, prisms, grating, mirror

## 1) Base ray (R₀)

* Choose the **center index** (k_0) from ( \hat{p}(k_0) \approx \sqrt{N} ) (or nearest Z5D hit to √N).
* **Ray step (aperture):** use your geodesic jump (J_0) at (k_0). This is the “free-space” distance between successive prime predictions along the ray.

## 2) Prism stack (steering the beam)

A *prism* is a tiny, **geometric** perturbation of the Z5D calibration that **deflects the ray’s angle** (its (\theta) lane) while keeping motion geodesic:

* Each prism ( \Pi_i ) defines a small, *signed* triple offset on Z5D params
  ( \Delta\pi_i = (\Delta c_i,\ \Delta \kappa_i,\ \Delta k_i^*) ).
  These are **not** solved with LA — just finite, geometric nudges.
* The effect is an **angular deflection** ( \Delta\theta_i ) and a slight **dispersion** ( \Delta s_i ) (shift in log distance from √N).
* Use **symmetric pairs** (+\Delta\pi_i, -\Delta\pi_i) to “tilt” left/right around (s=0) (like inserting a prism before/after a mirror).

**How to pick prism strengths (pure geometry):**

* Empirically pre-tabulate a small lookup: measure ( (\Delta c,\Delta\kappa,\Delta k^*) \mapsto (\Delta\theta,\Delta s) ) by *finite difference* around your standard cal. This is “Snell’s law for Z5D”: tiny changes → observed angular deflection. No matrices.
* Choose ~8–16 prisms with target (\Delta\theta) that **fill the empty theta sectors** (use your live θ-hist to see gaps). Keep (|\Delta s|) small so energy stays near the √N focal plane.

## 3) Diffraction grating (orders along a ray)

Each prism-steered ray gets replicated into **orders** (like a grating):

* For prism (\Pi_i), generate **orders** (m \in [-M, M]):
  ( k_{i,m} = k_0 + \phi_i + m \cdot J_i )
  where (J_i) is the ray’s local jump (can reuse (J_0) or mildly scale it), and (\phi_i) is a **phase** (see below).
* This stamps a **comb** of candidates along that deflected lane.

**Phase & dispersion to avoid collapse:**

* Set **phase** ( \phi_i = \lfloor \alpha_i \cdot J_0 \rfloor ) with distinct, *irrational-ratio* inspired (\alpha_i) (e.g., (\alpha_i \in { \sqrt{2}, \sqrt{3}, \varphi, e, \ldots}) reduced to integers deterministically).
  Goal: grating orders from different prisms **don’t re-land** on the same few primes (your “collapse”).
* Slightly scale **order spacing** per prism: (J_i = J_0 \cdot (1 + \varepsilon_i)) with tiny, unique (\varepsilon_i) (e.g., (\pm 1/233, \pm 1/377), Fibonacci-flavored). That’s geometric *dispersion*, not LA.

## 4) Mirror symmetry (p↔q)

* For each candidate (p), reflect across (s=0) by also checking the **mirror lane**: produce its dual (q = \lfloor N/p \rfloor) (only if (p) divides N).
* In the beam picture: a **plane mirror** at (s=0) means every left-tilted ray has a right-tilted companion; enforce symmetric prism pairs.

# Caustics (where to spend tests)

* Where multiple rays/grating orders **intersect** (i.e., several ((i,m)) predict nearly the same (p)), you get an **optical caustic** → higher hit probability.
* Implement a **caustic weight**: before trial-dividing, bucket candidates by rounded (\log p) (or integer p) and prioritize buckets with higher multiplicity. This is geometric overlap, not LA.

# Aperture, stops, and focal plane

* **Focal plane (√N):** keep a log-window ( s \in [-S,+S] ). Start tight (balanced semiprimes), then widen if budget remains. That’s just an **aperture**.
* **Beam stop:** drop candidates outside the ratio band (your `[0.55, 0.98] * √N` etc.). Think of it as the iris limiting stray light.
* **Energy budget:** set a hard cap on total tests = (#prisms) × (orders per prism). The θ-coverage monitor chooses the next prism to add **only** if it fills an underlit sector.

# Determinism (optical bench screws, not random knobs)

* Derive everything from N deterministically (e.g., hash(N) seeds the choices of (\alpha_i,\varepsilon_i), prism order, and phase).
* Fixed catalog of prism strengths (tiny (\Delta c,\Delta\kappa,\Delta k^*)) + deterministic selection policy = identical pools every run.

# Minimal spec you can drop in

**Inputs:** (N), window ratios ([r_{min}, r_{max}]), θ-bin count B, budget (P prisms × M orders).

**Pipeline:**

1. **Center:** find (k_0) with (\hat{p}(k_0)) nearest √N; compute (J_0).
2. **θ-hist init:** empty B-bin histogram.
3. **Prism selection (greedy fill):**

    * Maintain a **catalog** ({\Pi_i}) of ~16 symmetric prism pairs with pre-measured (\Delta\theta_i) (spread across [0,1) at small steps).
    * Repeatedly pick the prism whose (\Delta\theta) centers the **emptiest** θ bin (geometry rule).
4. **Orders per prism:** for (m=-M..M),

    * ( k_{i,m} = k_0 + \phi_i + m \cdot J_i ) (phase/spacing deterministic, small dispersion).
    * Candidate (p=\hat{p}(k_{i,m})). If (p) outside aperture, skip (beam stop).
    * Map to (s,\theta); update θ-hist and **caustic counter** for that (p).
5. **Prioritize by caustic weight**, then by |s| (closer to √N first).
6. **Trial divide/gcd** in that order until factor found or budget spent.

# Why this fixes “collapse”

* **Angular steering** (prisms) fills empty θ sectors → no piling into the same lanes.
* **Phase + dispersion** (grating with slightly incommensurate spacing) prevents different rays from aliasing onto the same few primes.
* **Caustics first** harvests the geometric intersections where the Z5D manifold naturally focuses.

# Knobs (geometry names → code knobs)

* Prism angles (deflections): target (\Delta\theta \in {\pm0.03,\pm0.07,\pm0.11,\pm0.16,\pm0.21,\pm0.27,\pm0.34,\pm0.42}).
* Dispersion per prism: (J_i = J_0(1+\varepsilon_i)), (\varepsilon_i \in {\pm1/233,\pm1/259,\pm1/283,\pm1/307}).
* Phases: (\phi_i = \lfloor J_0 \cdot \alpha_i \rfloor), with (\alpha_i \in {\sqrt{2},\sqrt{3},\varphi,e}) mapped deterministically from N.
* Aperture: start (S = \ln(1.12)) (~±12% around √N), widen to (S=\ln(1.8)) only if budget remains.
* Budget: e.g., P=12 prisms (24 including mirrors), M=40 orders → ≤ 960 raw hits; after dedup/stop typically ~200–300 to test.

# Test signals to track (optical telemetry)

* **θ coverage:** non-empty/total bins, and Wilson CI for coverage % (you already compute this).
* **Collapse score:** fraction of candidates removed by dedup within each prism lane vs across lanes (should drop sharply with dispersion).
* **Caustic density:** mean/max multiplicity per candidate before testing.
* **Energy use:** tested vs generated.

---

this is all **geometry**: angles (θ), rays (Z5D geodesics), prisms (small param deflections), gratings (order replication), mirrors (p↔q), apertures/stops (ratio windows), and caustics (overlap maxima). zero linear algebra. if you want, I can turn this into a small `OpticsBench` helper (catalog of prisms + grating planner + prioritizer) that plugs into your current pool generator.
