# Emerald Arena 0.13.0 — community feedback update

START menu, trainer compatibility, Struggle, smarter dodge and field notifications.
Busy-scene performance, reporter-specific saves and external-emulator checks remain open.

Pokémon Emerald with real-time battles. Move, dodge, attack and break the arena.
Requires your own unmodified Emerald ROM (USA/Europe).

1. Extract this ZIP on a computer.
2. Open **Prepare-Emerald-Arena.html** in a current Chrome, Safari or Firefox.
3. Choose your original `.gba`, not a ZIP. Wait for verification and click **Download game**.
4. Open **Emerald-Arena-0.13.0.gba** in your GBA emulator.
5. With a separate fresh save, highlight **NEW GAME** and press **SELECT**, not A.
6. Press **L and R together** in the field to fight. Charizard leads; reorder the party to try others.

Your ROM stays on your device and is never overwritten. No account or compiler required.
Updating? Back up your in-game save and import a copy for the new ROM. Match the
ROM/save basenames if required. Do not carry emulator save states across versions.

Setup needs Internet for the animations. The game then works offline.
Terminal option, Node 22+: `node install.mjs original.gba arena.gba`.

GBA controls: direction buttons to move, A to attack, B + direction to dodge, L/R to change move,
START for Pokémon / Bag / Moves / Resume; up/down chooses and A opens.
Inside MOVES, arrows select a move. B goes back; START resumes.
Hold L + R in battle to aim a regular Poké Ball, release to throw, B to cancel.
Balls come from your bag. A fresh practice save starts with 20; existing saves
keep their own inventory. Other ball types remain available in classic battle.
The first pause screen has explicit Pokémon, Bag and Moves choices.
SELECT opens the party. Save from the field menu.
These are GBA button names, not literal keyboard keys: check the emulator's input
settings. Visit a Pokémon Center to restore HP and PP. Back up existing saves.

Party: Charizard, Blastoise, Eevee, Dragonite, Scizor and Blaziken.
Box 1: Treecko, Poochyena, Bulbasaur, Squirtle, Grovyle and Sceptile.
187 animated Pokémon, including all Hoenn starter families and Kyogre.
Also included: 25 additional original PMD sprite sets, persistent
Substitute/smoke/Double Team/Protect/barrier state across menus, sleep/freeze/toxic,
Effect Spore, and Blizzard, Dragon Breath, Rock Slide and Shadow Punch profiles.
Sprites do not imply support for every ability, item or moveset.
Protect/Hyper Beam, evolution, rain/flooding, community arenas and menus remain.
Protect does not reflect attacks. Full story and mobile-emulator validation remain pending.
Rollout contributed by Didier Lopes (DidierRLopes), PR #4.
Dig, Fly, Teleport, Seismic Toss and Double Team are included, along with
elemental terrain, trainer send-outs and five arena environments.
Seismic Toss contributed by Didier Lopes (DidierRLopes), PR #1.
Unsupported abilities, effects and movesets still use classic battles.
This is not a fully rebalanced adventure.

This package contains a compiled code delta and a local installer, not a ROM,
save or sprite sheets. The installer verifies pinned SpriteCollab assets and
checks that the result matches the tested release, byte for byte.

Source and credits: https://github.com/GBurgardt/pokemon-emerald-arena

Full instructions and troubleshooting:
https://github.com/GBurgardt/pokemon-emerald-arena/blob/main/PLAY.md

Report a problem (no ROM or save attachments):
https://github.com/GBurgardt/pokemon-emerald-arena/issues/new?template=bug_report.yml
New arena rule: Struggle is available when no adapted damaging move has PP,
without changing learned moves or costing HP. Splash and Bide are adapted.
Dodge crosses obstacles only with a clear landing. Level-up/capture notices
appear while walking. See release-0.13.0.md in the repository for test scope.
