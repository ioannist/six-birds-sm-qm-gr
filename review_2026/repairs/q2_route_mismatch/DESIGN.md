# Q2-REPAIR-1 design

## Endomorphisms and defect

A completion is a 16-by-16 rational row-stochastic matrix `E` acting on any state table `T` by `T -> E T`. Conditional means average uniformly over partition fibers. A deterministic constrained projection is represented by the pullback matrix of an idempotent carrier retraction. Idempotence is tested exactly as `E^2 == E` using rational arithmetic.

For a pair `(E1,E2)`, the exact defect matrix is `[E1,E2] = E1 E2 - E2 E1`. The finite defect set contains precisely those carrier rows whose commutator row is nonzero. The reported primary magnitude is the spectral norm of this matrix; normalized Hilbert--Schmidt norm is supplied as a second invariant diagnostic.

## Invariance

The operator norm does not use numeric state labels, so affine recoding 0/1 to plus/minus one leaves it unchanged. Coordinate permutations induce a permutation matrix `S` and transform every completion as `E -> S E S^-1`; spectral and Hilbert--Schmidt norms and defect cardinality are conjugacy invariant. The implementation checks every one of the 24 coordinate permutations, exact idempotence after conjugation, and both encodings.

## Physical typing

The Step48 Boolean mode carrier and conditional-mean implementation and the Step26 stress-energy machinery are imported under literal SHA-256 pins. The nonlinear constraint uses Step26's two source types but declares its Boolean threshold as an imported finite discretization. The nonfactorizing partitions are motivated coarse access structures but remain an ansatz. These declarations prevent computed non-commutativity from being silently promoted to a continuum quantum-gravity theorem.
