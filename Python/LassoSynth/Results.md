# Summary table

| Model | Pre RMSE | Pre R2 | Donors | Monthly per 100k | Percent | Cumulative per 100k | 95% CI | Total Thefts |
|---|---|---|---|---|---|---|---|---|
| Fake null | 4.85 | 0.913 | 27 | 0.1 | 0.0% | 3 | -88 to 87 | 108 |
| Fake increase | 4.55 | 0.924 | 31 | 25.0 | 23.2% | 1,199 | 1,091 to 1,313 | 46,470 |
| Fake decrease | 5.88 | 0.872 | 22 | -32.1 | -19.5% | -1,540 | -1,640 to -1,442 | -59,662 |
| Honest | 3.52 | 0.954 | 16 | 20.2 | 18.0% | 972 | 900 to 1,041 | 37,644 |

# Weights, Fake null (top 10 of 27 nonzero)

| City | Weight |
|---|---|
| Intercept | 37.1923 |
| Alpharetta, GA | 0.0780 |
| Hayward, CA | 0.0672 |
| Miami, FL | 0.0629 |
| Baltimore, MD | 0.0531 |
| Vacaville, CA | 0.0439 |
| Paterson, NJ | 0.0439 |
| Wayne Township, NJ | 0.0397 |
| Baldwin Park, CA | 0.0350 |
| Detroit, MI | 0.0328 |
| Porterville, CA | 0.0237 |

# Weights, Fake increase (top 10 of 31 nonzero)

| City | Weight |
|---|---|
| Intercept | 6.6812 |
| Laredo, TX | 0.1313 |
| Vacaville, CA | 0.0542 |
| Hayward, CA | 0.0541 |
| Novato, CA | 0.0449 |
| Antioch, CA | 0.0432 |
| Baltimore, MD | 0.0369 |
| Aiken Cnty, SC | 0.0364 |
| McAllen, TX | 0.0362 |
| Harlingen, TX | 0.0360 |
| Baldwin Park, CA | 0.0337 |

# Weights, Fake decrease (top 10 of 22 nonzero)

| City | Weight |
|---|---|
| Intercept | 19.0633 |
| Vallejo, CA | 0.1618 |
| Gardena, CA | 0.0962 |
| Arcadia, CA | 0.0891 |
| Paterson, NJ | 0.0882 |
| Alpharetta, GA | 0.0625 |
| Miami, FL | 0.0467 |
| Hayward, CA | 0.0418 |
| Baltimore, MD | 0.0391 |
| Frisco, TX | 0.0380 |
| Folsom, CA | 0.0340 |

# Weights, Honest (top 10 of 16 nonzero)

| City | Weight |
|---|---|
| Intercept | 22.2752 |
| Laredo, TX | 0.0965 |
| Tucson, AZ | 0.0928 |
| Concord, CA | 0.0782 |
| Fairfield, CA | 0.0726 |
| Rock Hill, SC | 0.0327 |
| Baltimore, MD | 0.0249 |
| Portsmouth, VA | 0.0238 |
| Bakersfield, CA | 0.0217 |
| Santa Clara, CA | 0.0179 |
| Schaumburg, IL | 0.0177 |

# Sensitivity, honest model

| Spec | Donors | Percent | Cumulative per 100k | Total Thefts |
|---|---|---|---|---|
| Rates, all donors, alpha=5 | 38 | 15.0% | 832 | 32,237 |
| Rates, all donors, alpha=10 | 29 | 16.7% | 912 | 35,321 |
| Rates, all donors, alpha=20 | 22 | 18.1% | 975 | 37,784 |
| Rates, all donors, alpha=30 | 16 | 18.0% | 972 | 37,644 |
| Rates, all donors, alpha=50 | 12 | 15.8% | 870 | 33,709 |
| Rates, all donors, alpha=80 | 11 | 12.6% | 710 | 27,524 |
| Rates, 250k+ donors, alpha=10 | 13 | 9.7% | 561 | 21,731 |
| Rates, 250k+ donors, alpha=30 | 9 | 11.2% | 643 | 24,911 |
| Counts, all donors, alpha=30 | 43 | 5.3% | n/a | 12,381 |
| Placebo Dec 2018 (12 mo), alpha=30 | 9 | -3.9% | -69 | -2,690 |

# Pre-period fit, honest vs faked increase

| alpha | Honest RMSE | Honest R2 | Faked RMSE | Faked R2 | Faked Percent |
|---|---|---|---|---|---|
| 1 | 0.55 | 0.999 | 2.71 | 0.973 | 24.5% |
| 5 | 1.57 | 0.991 | 3.27 | 0.961 | 24.2% |
| 10 | 2.09 | 0.984 | 3.76 | 0.948 | 23.9% |
| 20 | 2.92 | 0.969 | 4.22 | 0.934 | 23.5% |
| 30 | 3.52 | 0.954 | 4.55 | 0.924 | 23.2% |
