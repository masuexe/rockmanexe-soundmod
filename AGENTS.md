# Project workflow

When the user reports that an experimental ROM passes its requested manual
checks, record acceptance for that exact ROM fingerprint, then commit and push
the completed source, tests and documentation without asking again. This is
the user's standing preference. Keep ROMs, source game assets and ignored local
research outputs out of Git; preserve the recorded limits of test coverage.

For an approved capability experiment, implement and iterate through automated
reference, native-runtime and regression checks without waiting for approval
after each intermediate step. Request one final manual listening/gameplay
check when the complete experimental ROM is ready. Keep automated verification
and user-reported manual acceptance distinct.

When the user authorizes a continuing research loop, advance through suitable
source investigations and automated experiments without intermediate approval
requests. Stop and notify the user when a new exact ROM needs manual listening
or gameplay acceptance. A silent environment defers those manual checks;
automated success does not replace them.

For each new manual-listening delivery, overwrite
`/mnt/d/Trill/patches/_exe6_test/v0.0.0/BR5J_00.bps`
(Windows: `D:\Trill\patches\_exe6_test\v0.0.0\BR5J_00.bps`) with that exact
experiment's final `unified.bps`. Verify the destination SHA-256 matches the
validated patch and record the delivery. If the destination is unavailable,
report that the copy could not be completed; do not claim it was delivered.
