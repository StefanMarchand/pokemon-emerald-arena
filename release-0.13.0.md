# Emerald Arena 0.13.0 — Matheus's feedback update

Six practical improvements, plus the previously tested stability follow-up.
Thanks to **@MatheusLynar** for playing successive builds and reporting concrete
reproduction steps. Thanks also to the Discord testers, @TyGuy044 and @CammyGbr
for the earlier switching feedback, and PMDCollab contributors for their sprites.

## The six improvements

1. **START now opens Pokémon / Bag / Moves / Resume.** Up/down and A are explicit;
   no hidden L/R tabs are required. Native healing, party selection, cancellation
   and resuming keep the encounter intact. The move view retains directional
   selection. SELECT remains a shortcut to the native party menu.
2. **More original trainer teams stay in real time.** Splash-only Magikarp gets
   the arena fallback; Bide is adapted for Seedot and other users. Ivan's three
   Magikarp and Billy's Zigzagoon/Seedot were fought through using ordinary
   inputs, then native XP, field return, save and reload were checked.
3. **These newly supported encounters skip the classic introduction.** Native
   entry effects still run: Intimidate lowers Attack and Drizzle sets weather.
   This extends the existing direct-entry path rather than removing ability
   effects or disabling the safe fallback for unsupported encounters.
4. **Results while walking.** XP is attributed to each participant; a level-up
   toast adds the native level-up fanfare. Caught messages appear after returning
   to the map, including party/PC destination. These notices do not lock movement.
5. **Struggle without a dead end.** When no adapted damaging move has PP, a
   temporary Struggle becomes selectable. Native learned moves and their PP
   remain untouched. Arena Struggle is unlimited and has **no recoil**; other
   moves retain normal PP. This is an explicit real-time balance adaptation.
6. **Dodge checks the landing.** If the landing is clear, B + direction can burst
   across a solid prop or opponent. Occupied destinations retain normal swept
   collision; open-ground dashes remain continuous. The crossing is instantaneous
   so a paused/status-affected Pokémon cannot be stranded inside a rock.

Wally's catching tutorial was explicitly excluded and remains unchanged.

### Bide adaptation

Bide costs one native PP and stores incoming HP damage during 180 active arena
updates. It then attempts to deal twice the stored damage at close range, subject
to walls, dodging, immunities and protection. Pausing freezes the charge. It is
not a claim of identical turn timing to the original game.

## Included stability follow-up

- Substitute, smoke, Double Team, Protect and screens retain their state through
  native menu reconstruction instead of disappearing or refreshing their timers.
- Sleep, freezing, toxic escalation, Effect Spore, Natural Cure and Marvel Scale
  support from the integrated candidate.
- Blizzard, Dragon Breath, Rock Slide and Shadow Punch profiles.
- 25 additional pinned PMD sets: **187 animated species** in total. Animation
  availability does not imply support for every moveset, held item or ability.

## Verification and limits

Final build: **150 core assertions**, a visual HUD gate, **128 focused assertions**,
and **7 checks in the shipping build with no test mailbox**. The public installer
passes 17 tests. The installer reconstructed the exact shipping hash from 668
pinned PNG inputs; the full BPS patch was independently applied and matched it.
All six recorded takes replayed to matching native state.

- Real mGBA input tests, not fabricated HP/XP or mock battles: pause, Bag/Potion,
  switching, moves, cancellation, PP exhaustion, Struggle, Bide, dash, trainer
  replacements, level-up/capture toasts, native saving and cold boot.
- The available **older adventure save** was copied privately and tested through
  Cascoon → Torchic → victory → native save/reload. Its original stayed unchanged.
- **The newly reported Magikarp/second-opponent save is still unavailable.** The
  original Ivan/Billy teams are strong targeted reproductions, not proof that
  the missing save has been tested or that both reports have the same cause.
- Double/link battles and unsupported abilities/items/movesets retain native
  classic fallback. Native learning/replacement decisions may still use native
  menus. This does not certify the whole story, every species or every emulator.
- Busy scenes still miss the 97% cadence target: approximately 96.7%, 94.6%,
  84.9% and 92.5% on the four measured integrated workloads before the final
  lettering-only adjustment. No sprite upload overflow or lost real projectile
  was observed. These are mGBA frame timings, **not a constant-60-fps promise**.
- Aqua/MyBoy reporter saves, a full story run and physical/mobile-emulator
  validation remain pending. Existing saves should be backed up.

Lab SHA-256: `11d343040e5d30221e9a3f78de5a3b3de954d7f5871b7d04403acfbcd83b2581`.

Shipping SHA-256: `a8d36c0c398f5281694c2d8dc5094a54a2276bd3092f5802cef6ef99369c645b`.

The public installer uses pinned, hash-verified PMDCollab inputs. The full BPS
patch and installer must reconstruct this same shipping hash. No original ROM,
private messages, reporter saves or emulator states are published.

## Updating

Use your own unmodified Emerald USA/Europe ROM. Back up the in-game `.sav`, then
import a copy for the new version; match basenames if the emulator requires it.
Never carry emulator save states across builds. See [PLAY.md](PLAY.md).
