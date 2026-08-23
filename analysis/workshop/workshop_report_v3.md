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

## Macro versus global yield

Macro fixed-K rows weight targets equally. Global rows pool all finite models and weight targets by their model count. ``Const.'' is the Ab--Ag training prevalence for Ab--Ag and the pooled General OOF prevalence for General, applied to every model.

| Dataset | DockQ | Macro K=5 observed/raw/iso/const | Global all observed/raw/iso/const |
| --- | ---: | --- | --- |
| Ab-Ag | 0.23 | 0.411 / 0.548 / 0.439 / 0.448 | 0.355 / 0.478 / 0.360 / 0.448 |
| Ab-Ag | 0.49 | 0.348 / 0.548 / 0.354 / 0.368 | 0.288 / 0.478 / 0.283 / 0.368 |
| Ab-Ag | 0.80 | 0.179 / 0.548 / 0.195 / 0.212 | 0.145 / 0.478 / 0.149 / 0.212 |
| General | 0.23 | 0.498 / 0.539 / 0.471 / 0.586 | 0.586 / 0.625 / 0.587 / 0.586 |
| General | 0.49 | 0.349 / 0.539 / 0.317 / 0.433 | 0.433 / 0.625 / 0.434 / 0.433 |
| General | 0.80 | 0.161 / 0.539 / 0.136 / 0.182 | 0.182 / 0.625 / 0.182 / 0.182 |

## K=5 difficulty stratification

Target difficulty is defined by observed fixed-K success fraction: hard <0.2, medium 0.2--0.6, easy >0.6. Signed errors are prediction minus observation.

| Dataset | DockQ | Stratum | Targets | Raw error | Iso error |
| --- | ---: | --- | ---: | ---: | ---: |
| Ab-Ag | 0.23 | hard | 705 | +0.372 | +0.197 |
| Ab-Ag | 0.23 | medium | 50 | +0.151 | -0.002 |
| Ab-Ag | 0.23 | easy | 502 | -0.194 | -0.208 |
| Ab-Ag | 0.49 | hard | 800 | +0.401 | +0.152 |
| Ab-Ag | 0.49 | medium | 26 | +0.137 | -0.083 |
| Ab-Ag | 0.49 | easy | 431 | -0.169 | -0.260 |
| Ab-Ag | 0.80 | hard | 1001 | +0.470 | +0.115 |
| Ab-Ag | 0.80 | medium | 42 | +0.435 | +0.035 |
| Ab-Ag | 0.80 | easy | 214 | -0.115 | -0.448 |
| General | 0.23 | hard | 77 | +0.319 | +0.179 |
| General | 0.23 | medium | 30 | +0.066 | -0.057 |
| General | 0.23 | easy | 86 | -0.217 | -0.202 |
| General | 0.49 | hard | 114 | +0.365 | +0.075 |
| General | 0.49 | medium | 19 | +0.214 | -0.060 |
| General | 0.49 | easy | 60 | -0.150 | -0.228 |
| General | 0.80 | hard | 155 | +0.458 | +0.056 |
| General | 0.80 | medium | 11 | +0.393 | -0.130 |
| General | 0.80 | easy | 27 | -0.082 | -0.446 |

## Constant-prevalence control

The constant contains no model-specific information. It uses Ab--Ag training prevalence for Ab--Ag and pooled General OOF prevalence for General.

| Dataset | DockQ | K | MAE Iso. | MAE Const. | Iso. wins |
| --- | ---: | ---: | ---: | ---: | --- |
| Ab-Ag | 0.23 | 5 | 0.205 | 0.478 | yes |
| Ab-Ag | 0.23 | 10 | 0.196 | 0.463 | yes |
| Ab-Ag | 0.23 | 20 | 0.185 | 0.452 | yes |
| Ab-Ag | 0.49 | 5 | 0.193 | 0.452 | yes |
| Ab-Ag | 0.49 | 10 | 0.183 | 0.440 | yes |
| Ab-Ag | 0.49 | 20 | 0.172 | 0.425 | yes |
| Ab-Ag | 0.80 | 5 | 0.175 | 0.305 | yes |
| Ab-Ag | 0.80 | 10 | 0.164 | 0.299 | yes |
| Ab-Ag | 0.80 | 20 | 0.153 | 0.289 | yes |
| General | 0.23 | 5 | 0.192 | 0.447 | yes |
| General | 0.49 | 5 | 0.131 | 0.446 | yes |
| General | 0.80 | 5 | 0.121 | 0.271 | yes |

## Yield outputs

- Macro/global rows: 18
- Constant-prevalence rows: `analysis/workshop_constant_prevalence_baseline.csv`
- Full macro/global/stratified output: `analysis/workshop_yield_macro_vs_global.csv`
- Per-target fixed-K rows: `analysis/workshop_yield_per_target.csv`
- Main-table summary: `analysis/workshop_yield_simplified.csv`
