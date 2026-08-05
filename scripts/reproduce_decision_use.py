#!/usr/bin/env python3
"""Summarize shipped decision-use experiment outputs."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'analysis' / 'decision_use'
D = ROOT / 'data'

print('Loading pre-computed predictions...')
for f in ['abag_predictions_v3.csv', 'general_predictions_v3.csv', 'casp16_predictions_v3.csv']:
    p = D / f
    if p.exists():
        df = pd.read_csv(p)
        print(f'  {f}: {len(df)} rows, columns: {list(df.columns)[:8]}...')
    else:
        print(f'  MISSING: {f}')

print('\nPre-computed results available in analysis/decision_use/')
print('See analysis/decision_use/README.md for details.')

metrics = pd.read_csv(A / 'fixed_ranking_yield_metrics.csv')
print(f"\n=== Fixed-ranking yield metrics: {len(metrics)} rows ===")
print(metrics.head(20).to_string(index=False))

reliability = pd.read_csv(A / 'reliability_operating_curve.csv')
print(f"\n=== Reliability operating curve: {len(reliability)} rows ===")
print(reliability.head(20).to_string(index=False))
