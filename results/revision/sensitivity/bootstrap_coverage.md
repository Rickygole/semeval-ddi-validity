# Two-way cluster bootstrap coverage

Simulation on the real pair structure. 300 replicates per scenario, 1000 bootstrap draws per replicate, seed 1.

Model A: score = signal * y + partner effect + drug effect + noise. Model B: per-drug random slope on y (mean mu, SD tau) + partner effect + drug effect + noise, with the two-way and the one-way (drugs only) bootstrap.

| cohort | model | scenario | bootstrap | true value | SD | 90% half-width | half-width / SD | coverage 90% | coverage 95% | 90% inside 0.40 to 0.60 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| novel | A | null, no partner effect | two-way | 0.500 | 0.036 | 0.112 | 3.108 | 1.000 | 1.000 | 0.000 |
| novel | A | null, partner effect | two-way | 0.499 | 0.030 | 0.109 | 3.655 | 1.000 | 1.000 | 0.003 |
| novel | A | signal 0.37, partner effect | two-way | 0.575 | 0.032 | 0.107 | 3.319 | 1.000 | 1.000 | 0.000 |
| novel | B | random slopes, null mean, partner effect | two-way | 0.500 | 0.036 | 0.114 | 3.174 | 0.997 | 1.000 | 0.000 |
| novel | B | random slopes, null mean, partner effect | one-way drug | 0.500 | 0.036 | 0.064 | 1.794 | 0.917 | 0.970 | 0.687 |
| novel | B | random slopes, mean 0.37, partner effect | two-way | 0.571 | 0.037 | 0.112 | 3.040 | 0.997 | 1.000 | 0.000 |
| novel | B | random slopes, mean 0.37, partner effect | one-way drug | 0.571 | 0.037 | 0.063 | 1.721 | 0.907 | 0.937 | 0.177 |
| novel | B | random slopes, null mean, no partner effect | two-way | 0.499 | 0.042 | 0.121 | 2.893 | 1.000 | 1.000 | 0.000 |
| novel | B | random slopes, null mean, no partner effect | one-way drug | 0.499 | 0.042 | 0.069 | 1.646 | 0.887 | 0.947 | 0.537 |
| older_clean | A | null, no partner effect | two-way | 0.501 | 0.019 | 0.052 | 2.822 | 1.000 | 1.000 | 0.997 |
| older_clean | A | null, partner effect | two-way | 0.499 | 0.013 | 0.050 | 3.751 | 1.000 | 1.000 | 1.000 |
| older_clean | A | signal 0.37, partner effect | two-way | 0.573 | 0.014 | 0.049 | 3.530 | 1.000 | 1.000 | 0.060 |
| older_clean | B | random slopes, null mean, partner effect | two-way | 0.499 | 0.019 | 0.055 | 2.928 | 0.993 | 1.000 | 0.987 |
| older_clean | B | random slopes, null mean, partner effect | one-way drug | 0.499 | 0.019 | 0.034 | 1.820 | 0.920 | 0.953 | 1.000 |
| older_clean | B | random slopes, mean 0.37, partner effect | two-way | 0.571 | 0.018 | 0.054 | 2.995 | 1.000 | 1.000 | 0.083 |
| older_clean | B | random slopes, mean 0.37, partner effect | one-way drug | 0.571 | 0.018 | 0.034 | 1.857 | 0.940 | 0.963 | 0.413 |
| older_clean | B | random slopes, null mean, no partner effect | two-way | 0.501 | 0.024 | 0.060 | 2.521 | 0.990 | 0.997 | 0.927 |
| older_clean | B | random slopes, null mean, no partner effect | one-way drug | 0.501 | 0.024 | 0.038 | 1.608 | 0.897 | 0.947 | 0.997 |

Two-way bootstrap over all scenarios: 90% coverage [0.990, 1.000], 95% coverage [0.997, 1.000], 90% half-width [2.521, 3.751] times the SD of the estimate (a calibrated interval gives 1.645).

Share of drawn drugs that drop out of a bootstrap draw because the partner resampling leaves them one class:

* novel: mean 0.194, max 0.483 over 1000 draws
* older_clean: mean 0.123, max 0.282 over 1000 draws
