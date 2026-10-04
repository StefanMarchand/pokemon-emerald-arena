# Feedback regression tests (0.13.0)

These are real mGBA button-input tests, not simulated combat. After reconstructing
the source and preparing the pinned emulator runner described by `BUILD.md`,
build the separate laboratory ROM with `tools/arena/dev.sh build`.

From that reconstructed checkout:

```sh
python3 tests/arena/test_matheus_six.py
python3 tests/arena/test_matheus_dash.py
python3 tests/arena/test_matheus_feedback.py
python3 tests/arena/test_matheus_trainers.py
python3 tests/arena/test_matheus_bide.py
python3 tests/arena/test_matheus_intro.py
python3 tests/arena/test_stability_pp.py
python3 tests/arena/test_menu_persistence.py
python3 tests/arena/test_stability.py
PYTHONPATH=tests/arena python3 tools/arena/stability_suite.py test_moves test_hybrid
```

Tests prepare disposable fixtures with native CreateMon/SetMonData. Fighting,
healing, PP consumption, XP and victory use native menus/buttons. Source for the
local-only runner and harness is included; no reporter save or emulator state is
distributed. The private older-save and shipping-checkpoint tests require those
private fixtures and are intentionally not bundled as runnable public tests.

The current SELECT contract is the party menu, not manual entry into classic
battle. `test_hybrid.py` was updated accordingly; unsupported item transitions
remain covered separately by `test_stability.py`. Three-frame key pulses avoid
one-frame input samples being missed during a multi-frame rendering callback.

The harness publishes immutable build-cache files atomically. Starting a second
disposable core must not truncate the ROM already mapped by the first one.

Results and important limitations: [0.13.0 notes](../release-0.13.0.md).
