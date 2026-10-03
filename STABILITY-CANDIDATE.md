# 0.12.1-rc1 — not yet promoted

Integrated stability follow-up on 0.12.0. No public release or announcement has
been made for this candidate. The README download still points to stable 0.12.0.

## Changes

- Preserve Substitute HP, smoke, Double Team, Protect and screen timers through
  native menu reconstruction. Rebind visual objects without refreshing effects.
- Sleep/freeze immobilization and recovery; native toxic escalation; Effect Spore.
- Native Natural Cure switch handling and Marvel Scale damage compatibility.
- Blizzard, Dragon Breath, Rock Slide and Shadow Punch profiles with native PP,
  damage and secondary effects.
- 25 pinned PMDCollab sprite sets, 187 species total. Large Milotic frames use an
  explicit 3/4 ratio; no implicit cropping. Original asset credits in payload.
- Compact symmetric navigation caches; unchanged geometry tested with sanitizers.
- Build dependencies include every arena effect include file.

## Verification

Lab SHA-256: `d3c18a22c5340d8edf272c813dac151af0389835adf09182f9e15449fffced91`.
Shipping SHA-256: `16f0610b3948e58a413c222ba5564a4bc711843ab31b1589e5c63f145b5f3933`.

Core mGBA suite: 207 checks. Additional targeted gates: 24 menu-persistence,
18 extended-status, 15 faint/replacement, 16 story-move and 5 original Wally
tutorial checks. Existing stability, PP, Synchronize and trainer suites passed.
Evolution/cancel/Everstone and Protect absorption acceptance passed. Native
sprite decoder verified 68,168 frames. Navigation: 1,770 routes and 128 destruction
masks with sanitizers. Installer: 17 checks plus exact shipping reconstruction
from 668 hash-verified pinned PNG inputs. Source patch passes against the pinned
base. Shipping opens a COPY of the reporter save; original remains untouched.

## Open gates — do not call this fully stable

- Four bounded performance workloads achieved 96.83%, 95.44%, 84.92%, 92.86%
  update cadence, below the 97% target. No sprite upload overflow or real
  projectile allocation failure. These are emulator frame timings, not hardware
  FPS or proof of a new regression. Busy-scene profiling is still required.
- The actual Aqua/MyBoy reporter saves are unavailable. The available Aqua
  checkpoint and original Wally tutorial pass; a full story playthrough does not
  follow from those checks.
- MyBoy, PizzaBoy, gpSP and physical hardware remain unverified.
- Not all 386 species have directional sprites. Whiscash, Meditite and Medicham
  have new sprites but the tested native movesets still fall back safely.
- Revive/all item paths, rare status interactions and prolonged human balance
  testing remain incomplete. PR #6 iPhone helper is not merged.

EWRAM: 259,960 bytes shipping, including the existing 112 KiB heap reservation.
ROM: 33,490,436 bytes. Small linker headroom is not the same as free heap size.

Thanks to @MatheusLynar for playtesting and a private save, @TyGuy044 and
@CammyGbr for switching feedback, and the Discord testers. No private messages,
saves, original ROM or unlicensed source sprite sheets are included here.
