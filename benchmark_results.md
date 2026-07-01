==========================================================================
  BENCHMARK RESULT: vulnerable_app.py

==========================================================================
Code: vulnerable_app.py (8 lines, ~500 chars)

  Comparison Summary

==========================================================================
  Metric                         Single-Agent     Multi-Agent      Change    
--------------------------------------------------------------------------
  Total findings                 12               127               +958.3%
  Categories covered             6/6              6/6                 +0.0%
  Avg severity score (1-4)       2.83             2.82                -0.4%
  Execution time                 26.4s            97.4s             +268.9%
  Est. cost (USD)                $0.0171          $0.2318          +1255.6%
--------------------------------------------------------------------------
  Overlap Analysis

Single-agent findings ALSO found by multi-agent: 12/12 (100.0%)
Findings UNIQUE to single-agent: 0
Findings UNIQUE to multi-agent: 115

  Severity Distribution

  Severity     Single-Agent     Multi-Agent     
--------------------------------------------------------------------------
  Critical       3 ███                     31 ████████████████████
  High           4 ████                    47 ████████████████████
  Medium         5 █████                   44 ████████████████████
  Low            0                          5 █████

  Category Coverage

  Architecture            Single: ✅  Multi: ✅
  Performance             Single: ✅  Multi: ✅
  Quality                 Single: ✅  Multi: ✅
  Security                Single: ✅  Multi: ✅
  UX / Accessibility      Single: ✅  Multi: ✅
  Visual / UI             Single: ✅  Multi: ✅

  Multi-Agent Unique Findings (not found by generalist)

  1. [Critical] God object pattern violates single responsibility principle with massive coupling
  2. [Critical] SQL injection vulnerability allows arbitrary database queries
  3. [Critical] Hardcoded API secret exposed in source code
  4. [Critical] Cross-site scripting vulnerability reflects user input without sanitization
  5. [High] N+1 query problem causes performance degradation
  6. [High] Global mutable state creates tight coupling and testing difficulties
  7. [High] O(n²) algorithmic complexity causes exponential performance degradation
  8. [Medium] Dead code increases maintenance burden and confusion
  9. [Critical] Hardcoded API secret exposed in source code
  10. [Critical] SQL injection vulnerability allowing arbitrary database queries
  ... and 105 more

  Conclusion

  ✅ Multi-agent finds 10.6x more findings
  ✅ Multi-agent covers 100.0% of generalist findings, plus 115 additional findings

==========================================================================