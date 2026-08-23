# Seva Aug 22 Workshop Revision

## Scope

- Main text: raw confidence context, isotonic ipTM, fixed-ranking yield, and AFDB.
- Appendix only: all iPAE metrics and large Ab--Ag/General tables.
- Excluded: MLP, CASP16, iPAE figures, iPAE-ranked yield, and reliability operating curves.

## Fair coverage

Raw ipTM and isotonic ipTM are monotone-equivalent within Ab--Ag. Any matched-precision coverage difference is due to isotonic plateaus/ties, not new ranking information.

| q | Raw coverage | Iso coverage | Raw precision | Iso precision |
| ---: | ---: | ---: | ---: | ---: |
| 0.50 | 0.791 | 0.651 | 0.440 | 0.523 |
| 0.60 | 0.589 | 0.441 | 0.573 | 0.724 |
| 0.70 | 0.479 | 0.409 | 0.679 | 0.765 |
| 0.80 | 0.384 | 0.367 | 0.799 | 0.820 |
| 0.85 | 0.343 | 0.339 | 0.847 | 0.851 |
| 0.90 | 0.255 | 0.255 | 0.911 | 0.911 |
| 0.95 | 0.000 | 0.000 | nan | nan |

## Yield outputs

- Result rows: 12
- Per-target rows: `analysis/workshop_yield_per_target.csv`
- Summary: `analysis/workshop_yield_simplified.csv`
