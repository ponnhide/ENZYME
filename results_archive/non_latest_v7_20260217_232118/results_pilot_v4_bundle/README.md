# Pilot v4 Bundle

## What is included
- `analysis/`: all v4 comparison outputs, plots, significance tests, integrated reports.
- `runs/`: the 4 finalized run directories.
  - `gpt_hlcore`
  - `gpt_directcore`
  - `qwen_hlcore`
  - `qwen_directcore`
- `previous/`: links to prior pilot outputs and archives.

## Final run summary (paper-level mean)
Source: `analysis/pilot_v4_run_summary.csv`

- `gpt_hlcore`: papers=34, units=322, mean_total=58.724, mean_repro=20.122, failed_units=0
- `gpt_directcore`: papers=34, units=327, mean_total=69.299, mean_repro=17.742, failed_units=1
- `qwen_hlcore`: papers=34, units=289, mean_total=61.041, mean_repro=16.155, failed_units=1
- `qwen_directcore`: papers=34, units=293, mean_total=68.396, mean_repro=17.847, failed_units=0

## Notes
- A failed first attempt of Qwen direct-core (server disconnect) was preserved in:
  - `results_archive/results_pilot_v4_qwen_fp8_directcore_badseed_20260216_220544`
- Clean rerun result is in:
  - `runs/qwen_directcore` (=> `results_pilot_v4_qwen_fp8_directcore`)

## Primary report entrypoints
- `analysis/pilot_v4_overview.md`
- `analysis/compare_gpt_vs_qwen_hlcore/pilot_integrated_report.md`
- `analysis/compare_gpt_vs_qwen_directcore/pilot_integrated_report.md`
- `analysis/compare_hl_vs_direct_gpt/pilot_integrated_report.md`
- `analysis/compare_hl_vs_direct_qwen/pilot_integrated_report.md`
