# Collimator simulation with lower activity zones

We were tasked with simulating collimator for GP3 machine with lower activity zones

## Setup

Long source and collimator got GP3 machine. Assumed normal activity 4500Ci. Four cases were simulated:
- One with closest to isocenter half of the source replaced with lower activity pellets (3000Ci).
- One with furthest from isocenter half of the source replaced with lower activity pellets (3000Ci).
- One with closest to isocenter 1/3 of the source replaced with lower activity pellets (3000Ci).
- One with furthest from isocenter 1/3 of the source replaced with lower activity pellets (3000Ci).

Total photon yield at the collimator exit plane was computed and compared.

## Results

We assume original photon yield  at the collimator exit plane in the GP3 machine to be equal to 1.
Thus, results are provided as dimensionless ratios.

|--------|---------|------------|------------|------------|------------|
|        |  GP3    | First Half |  Last Half | First Third| Last Third |
|--------|---------|------------|------------|------------|------------|
| C25    |  1.0    |    0.79    |   0.877    |   0.872    |  0.925     |
|--------|---------|------------|------------|------------|------------|
| C15    |  1.0    |    0.79    |   0.876    |   0.871    |  0.924     |
|--------|---------|------------|------------|------------|------------|

## Conclusion

Total photon fluence shows that likely half or more of the source is of reduced activity.
It might be useful to compare fluence only energetic (f.e. E>0.5MeV) photons.

