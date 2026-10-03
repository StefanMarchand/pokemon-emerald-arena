# Emerald Arena 0.12.0 — community stability update

This release focuses on playtesting feedback rather than another showcase-only feature.

- Fixes the reproduced Route 102 trainer replacement UI corruption and hardens native/arena transitions.
- Fixes Ralts-to-Mudkip switching, allows harmless held items such as a held Potion, and supports adapted status-only movesets.
- Adds poison and paralysis support, Shed Skin recovery, contact status abilities and Synchronize integration.
- Preserves attack/dodge recovery through native menus and adds a short recovery after voluntary switching.
- Adds Headbutt, Body Slam, Steel Wing and Thunder Shock profiles with native damage and relevant secondary effects.
- Adds ten story sprite sets: Barboach, Spheal, Solrock, Sandshrew, Trapinch, Torkoal, Numel, Duskull, Carvanha and Magnemite. The integrated roster is now 162, including the previously previewed Gastly.
- Hardens navigation around blocked destinations. Preserves flame clashes, ghost evolution art, community arenas and earlier contributions.

Thanks to @MatheusLynar, @TyGuy044, @CammyGbr and everyone reporting issues on Discord. Previous contributions and art credits remain in CREDITS.md and the sprite manifests.

## Download

- [Full BPS patch](https://github.com/GBurgardt/pokemon-emerald-arena/releases/download/v0.12.0/Emerald-Arena-0.12.0-full.bps)
- [Installer ZIP](https://github.com/GBurgardt/pokemon-emerald-arena/releases/download/v0.12.0/Emerald-Arena-0.12.0.zip)

Requires your own unmodified Emerald (USA/Europe). Back up your in-game save before updating; do not reuse emulator save states. No ROMs or player saves are distributed.

## Scope and checks

Tested in mGBA: native combat/capture/result flow, early teams, PP exhaustion, status persistence, menu pause, actual Static/Synchronize procs and a complete original Route 102 trainer event. A copied existing save cold-boots in the shipping build; the original save remains untouched. All 58,624 frames across 162 sprite sets pass the decoder. The installer checks 584 pinned source images and reproduces the shipping hash.

Not full-adventure, physical-GBA, MyBoy, PizzaBoy or gpSP certification. The reported Aqua story blocker still needs a reproducing save. Sleep/freeze/toxic and other unsupported encounters retain classic fallback, including Effect Spore/contact cases. Substitute/smoke transient state through native menus still needs work. The revised video omits classic fallback footage; it does not imply those cases are adapted.

Clean pinned-source compilation, the installer and the full BPS reconstruction all match byte for byte. All 17 public installer/player-journey checks pass.

ROM SHA-256: `9a0c906ab622ef22d528315e823902cb6f06e9e4373189caa6ba1f7d50078e2f`.
