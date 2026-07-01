==========================================================================
  BENCHMARK RESULT: vulnerable_app.py
==========================================================================
Code: vulnerable_app.py (192 lines, intentional bugs across 6 categories)

  Comparison Summary
==========================================================================
  Metric                         Single-Agent     Multi-Agent      Change    
--------------------------------------------------------------------------
  Total findings                 8                18               +125.0%
  Categories covered             3/6              6/6              +100.0%
  Avg severity score (1-4)       2.75             3.11             +13.1%
  Execution time                 8.2s             32.5s            +296.3%
  Est. cost (USD)                $0.004           $0.028           +600.0%
--------------------------------------------------------------------------
  Overlap Analysis

Single-agent findings ALSO found by multi-agent: 6/8 (75.0%)
Findings UNIQUE to single-agent: 2
Findings UNIQUE to multi-agent: 10

  Severity Distribution

  Severity     Single-Agent     Multi-Agent     
--------------------------------------------------------------------------
  Critical       2 ██                      5 █████
  High           3 ███                     6 ██████
  Medium         2 ██                      5 █████
  Low            1 █                       2 ██

  Category Coverage

  Coordinator/Orchestration   Single: ❌  Multi: ✅
  Analysis/Patterns           Single: ✅  Multi: ✅
  Architecture                Single: ❌  Multi: ✅
  Engineering/Fixes           Single: ✅  Multi: ✅
  Critique/Validation         Single: ❌  Multi: ✅
  Research/Documentation      Single: ✅  Multi: ✅

  Conclusion

  ✅ Multi-agent finds 2.25x more findings (18 vs 8)
  ✅ Multi-agent covers 100% more categories (6/6 vs 3/6)
  ✅ Multi-agent detects 13% higher-severity issues (3.11 vs 2.75)
  ✅ Multi-agent covers 75% of generalist findings, plus 10 additional findings
  ⚠️ Multi-agent costs 7x more API calls and 4x more time

==========================================================================
