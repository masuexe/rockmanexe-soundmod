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
