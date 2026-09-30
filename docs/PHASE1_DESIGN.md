# Phase 1 design: the Arc One foundation

*Jujutsu Kaisen: Cursed Bonds · Ren'Py 8.5.3 · written 29 Sep 2026 against commit `025f5e8`.*

This is the build plan for phase 1 of the Arc One storyboard (`docs/arc1_storyboard.html`, with the owner's decisions in its comments). It starts from the "evolve" design, which the judges scored highest. It folds in the grafts the judges recommended and closes every gap they found; each of those is logged as a decision in section 1. Separate agents can implement the work packages in section 7 in parallel.

Where this document and older notes disagree, this document wins. Where it and the storyboard's decisions disagree, the storyboard wins, and the difference is a bug in this document.

---

## 0. What phase 1 changes, in plain words

**What you'll notice when you play:**

- **The story is told as "I".** The prologue (the diner, the alley, the offer, the tour, your first morning) is rewritten so that Kaito narrates. Everyone else still says "you" or your name. Later chapters keep "you" for now and get converted one by one in later phases.
- **Kaito is off screen.** He no longer stands in any scene, so everyone looks at the camera, which is you. His portrait appears beside his own lines (you can switch that off in Preferences). His full picture lives in the journal.
- **Faces move.** Characters change expression during scenes, and when someone off screen speaks, their portrait appears beside the text.
- **Sana tells you the thing.** In the dark alley she finally tells you: she has been seeing creatures for weeks. Seconds later one kills her.
- **One technique: Last Light (残光, Zankō).** There is no technique choice any more. Your power wakes as the instant the lights went out, held still. Filament and Emberfall are gone. Old saves that picked them become Last Light.
- **The alley fight ends** after four exchanges instead of grinding forever. The alley has its own (placeholder) background.
- **The casket is gone.** On the tour, Gojo points up at the veil on the mountain ridge, where Sukuna's mummified body sits cross-legged with its fingers missing. He asks you never to go near it.
- **A quieter screen.** Walking around, you see only the day and weekday, plus three buttons: Map, Journal and Menu. Rewards stack up in the corner instead of replacing each other. When your next goal changes, a short banner tells you what it is.
- **People are doing things.** Each place shows who is there and what they're doing ("Yuji — halfway through an enormous bowl"). Clicking someone brings them closer and offers three or four sensible choices, not a long list of locked rows. They stay on screen while you talk.
- **A new map.** The campus is grouped into six areas that show who is where and which missions are waiting. A Tokyo tab opens after Ijichi's ride-along. Trips there take half a day; the districts themselves are placeholders for now.
- **A journal with six tabs:** People, Missions, Memories, Stats, Equipment and Inventory. You can replay any scene you've seen.
- **Grades as in the show.** You're assessed as Grade 4 at roll call. Your grade limits how far your stats and cursed energy can grow, which board jobs you can take, what the armory will give you and how many talismans you can wear. Everyone else has a grade too, grows on their own schedule, grows faster when you train together, and can be promoted without you.
- **Two new offices.** Utahime's office opens early in Act I; she runs a board of graded jobs, which you take with a partner. Gojo's office opens after his first lesson, and on the odd day he's in, he'll teach you.
- **Nothing runs on a deadline.** The Kyoto countdown is gone. Story beats come in order and wait for you. The Goodwill Event is part of the story (Act IV), no longer a date.

**What isn't there yet (by design):**

- Board jobs are narrated and resolved automatically; real fights for them come in the combat update (phase 2).
- Most character missions show as "Written in a later build". Two are playable: Ijichi's ride-along and Maki's armory.
- Talismans and cursed tools can be collected and equipped, but their effects switch on in phase 2.
- The Tokyo districts play a short arrival and bring you back.
- New acts (the detention center, Nanami, Kyoto and the rest) appear in the journal as "Coming in a later build".
- Art for the offices, the alley, the ridge veil and Tokyo is placeholder.

**How you'll review it:** at four checkpoints (section 8.6) you play the game from the SDK as usual. A short checklist in `docs/PLAYTEST.md` tells you what to look at. A "Review tools" button, which only shows when you run from the SDK, lets you jump ahead (promote yourself, open Tokyo, finish the next story step) without playing hours to get there. Your existing saves keep loading, and they are backed up before anything is built.

---

## 1. Decisions (grafts and gaps closed)

Every graft the judges recommended and every gap they found is resolved below. "WP" is the package that implements it (section 7).

| # | Decision | WP |
|---|---|---|
| D1 | **The load-failure path is handled properly.** Ren'Py's `load_failed()` jumps straight to `config.load_failed_label`. It does not run `execute_default_statement` or the `_after_load` callbacks (checked in `renpy/rollback.py:848`). So `label load_recover` first runs `renpy.execute_default_statement(False)`, sets `_in_replay = None`, and then runs the migrations before it routes. | WP0 |
| D2 | `config.return_not_found_label = "return_recover"` is the second safety net: it re-runs the migrations, then goes to the sandbox or resumes the prologue. | WP0 |
| D3 | Migrations run from `config.after_load_callbacks` on **every** load (they are idempotent). They also run from `ensure_state()`, which the sandbox calls on every pass and which only does work while `save_version < SAVE_VERSION`. When a save is upgraded on load, `renpy.block_rollback()` is called once, so rolling back can't restore pre-migration values. | WP0 |
| D4 | **Journal context.** On campus the journal opens through the loop (`Return(("journal", tab))` → `call screen journal(tab)`), in the main context. Only there can you change equipment or begin Arc Two. Opened from the quick menu during a scene (`ShowMenu("journal")`, a menu context), the Equipment tab is read-only and says "Change equipment on campus". As a second safeguard, `equip_*`/`unequip_*` call `renpy.retain_after_load()`. | WP7, WP8, WP6 |
| D5 | Every memory replay uses `Replay(..., locked=False)`. Whether a memory is seen comes from the save's own state, never from persistent seen-labels. | WP5 |
| D6 | **Memories are recorded per save:** `config.label_callbacks` adds catalogued labels to `memories_seen` (never during a replay), plus legacy rules read from `done_events` and flags. For settled old saves, the prologue sub-labels are backfilled as seen by migration 65. Nothing is written to `persistent`. | WP5 |
| D7 | The toast queue is a `builtins.object` / `builtins.list` created in `init python`. It is never assigned at runtime, so it is not saved and not rolled back. It is muted during replays and migrations. | WP0, WP7 |
| D8 | **Calendar phrasing sweep.** Every deadline-bound line is listed with its replacement in section 5.4.2, including `story_arc1.rpy:264/266/324/339/349/364/418/423/450/467/494/497`, `events_arc1.rpy:1574` and `ch5_debrief.rpy:38/163–172`. Durations that aren't deadlines ("four days later", "Three weeks" of Nade's silence) stay. | WP0, WP10 |
| D9 | **The seam between "I" and "you".** Phase 1 also converts to "I": the sandbox's own narration (`sb_loop.rpy`, `sb_smalltalk`), `st_roll_call` (reworked anyway) and every new scene, including Utahime's arrival. So the first "you" scene the player meets is the Sun Mall briefing, on day 4 at the earliest. Phase 3 converts in story order: Sun Mall/ch4/ch5 → aftermath → Kurose → second-years → noise → Oda → intensive → Nade → hangouts. | WP7, WP3, WP10 |
| D10 | **Storehouse vs armory.** The `storehouse_access` flag (roll call, Yaga's workshop) lets you **enter and look** ("Look through the racks", once a day). `armory_open` is set by Maki's character mission *The Armory* in Act II, as the storyboard has it, and **releases tools up to your grade**. Yaga's roll-call line becomes "Look, don't take. Nothing on those racks leaves without a grade and a reason." | WP10, WP3, WP6 |
| D11 | **Sana's flashbacks have unlock triggers, stored as data:** *The Diner* on the first trip to Yotsuka; *The Daisy Clip* when the keepsake `daisy_clip` is in the inventory (handed out in phase 3); *The Teacher Ranking* once Oda's first letter is read. Each one's label is written in phase 3. Until then, a triggered flashback shows "Written in a later build". | WP5, WP6 |
| D12 | **"Grade is who gets picked; they say so."** When an NPC is promoted: a toast overnight, a remark on your next Talk with them (`pending_remarks`), and a line in the People tab. While any student outranks you, Utahime's board shows a read-only card: "Grade 2 · taken by Megumi". `pick_team(n, min_key)` is provided now for phase 3 (Kyoto team, big missions). | WP2, WP3, WP4 |
| D13 | **Utahime leaves to lead Kyoto** (Act IV, phase 3). `board_host()` switches on the flag `utahime_leads_kyoto`: the board moves to Yaga's office under Ijichi, with a line saying so. A generic `FLAG_SCHEDULES` table lets a flag replace a character's schedule. That will also be needed when Yuji "dies" in Act I. Phase 1 ships the mechanism with an empty table. | WP1, WP4 |
| D14 | **Aftermath placement.** In phase 1 the existing `st_aftermath` (Shoko on cursed-energy debt, "the morning after Saitama") stays in Act I, the morning after the Sun Mall. When the detention center lands in phase 3, the storyboard's new Aftermath gets its own label and step. `m_aftermath` then moves to Act II with its first line rewritten; its id stays, so saves past it are unaffected. | WP3 |
| D15 | **Sukuna seeds.** The ridge place now mentions the veil above. Gojo's ambient pose there is "sitting just outside the veil". A free, once-a-day ridge action, *Look up at the veil*, has three rotating lines; the third time, "It is facing the school." Reserved flag names for phase 3 are in section 10. | WP1 |
| D16 | **No grade until roll call.** `grade` defaults to `None` ("Not yet assessed"). Roll call assesses you on screen as Grade 4, with a grade card. While `grade` is `None`, caps and slots use Grade 4's numbers. | WP2, WP10 |
| D17 | **"Gojo is in" days start after his first lesson** (flag `intensive_done`). About 1 day in 6, seeded by day, never two days running. His office is locked before that, with a note on the door ("SOON!"). | WP1 |
| D18 | **The Grade 3 promotion is a real mission with Maki watching.** It is a fight in the training hall on the existing combat engine, against a new enemy entry `promo_g3`. Losing or withdrawing means trying again the next day. It needs 60 merit. The story alone pays 70 merit by the end of Act II, so the board is never a grind wall for the reviewer. | WP3, WP2 |
| D19 | The Grade 2 promotion (on Nanami's word) is an unwritten row in phase 1. Grade 3 is the ceiling in normal play; the review tools can promote further. | WP3 |
| D20 | **Every storyboard beat has a row:** detention center, infirmary, The Strongest, the secret, Nanami, cinema, Junpei, Satozakura, Kyoto arrives, team battle, the attack, baseball, new faces, Yasohachi, Mei Mei, the recommendation, Yuta's call, the sketchbook. Unwritten rows never block written ones and never complete an act or the arc. Rows have spaced `order` numbers and a `skip_if`, so beats inserted in phase 3 don't become stale objectives for saves already past them. | WP3 |
| D21 | NPC xp is **cumulative**; promotion thresholds are cumulative too. Stats are base + a growth bonus, so they never drop. `ACT_STUDENT_CAP` limits NPC promotions by how many acts are complete. No existing dialogue names an NPC's grade (checked), so there is nothing to contradict. | WP2 |
| D22 | The mission status cache is cleared by `config.interact_callbacks`. The cache is exactly per interaction, so a bond gain shows a newly available character mission immediately. | WP3 |
| D23 | `arc_one_open` sets `arc_start_day = day` (default 1). The prologue step's done-day is `arc_start_day`, so roll call waits for day 2, as it does today. | WP3, WP9 |
| D24 | Keepsakes are granted only by `sync_keepsakes()`, which is idempotent and reads the flags. It runs as a migration and when the campus opens, not at the packing choice. One path, no double grants. | WP6 |
| D25 | **Quick menu:** BACK · HISTORY · SKIP · AUTO · SAVE · JOURNAL · MENU. It hides itself while any screen tagged `sandbox` or `menu` is showing. The sandbox stops setting `quick_menu = False`, and migration 5 restores `quick_menu = True` for old saves. The game menu's navigation column serves as the pause menu; there is no separate `pause_menu` screen. | WP7, WP8 |
| D26 | Small exploit fixes pulled forward: *Hold the hour*, *Get patched up* and *Look through the racks* are once a day (`actions_today`). HP refills at dawn. The rest of the combat economy is phase 2. | WP7, WP1 |
| D27 | **Test isolation.** `tools/smoke.sh` v2 runs each harness in a **scratch copy** of the project, with `--savedir` set to a scratch folder. It never touches the owner's saves, persistent data or `.rpyc` files, and it passes or fails from a result file. Package worktrees get read-only **copies** of the owner's `game/*.rpyc`, so load tests match the real tree. | WP0 |
| D28 | **Integration happens in the owner's folder** on branch `phase1`, after the backup (WP0 task 0). The owner plays the checkpoints there. `main` is untouched until the owner approves. | WP0, WP11 |
| D29 | New text never contains a literal "Kaito" or "Amagiri"; it uses `[mc_name]`/`[mc_surname]`. `check_content.py --no-literal-name` enforces this. | all |
| D30 | **Review tools** are a developer-only panel (runs from the SDK), reachable from a small HUD button in any sandbox place, not only explore mode. They run in the main context, so their changes stick. | WP11, WP7 |
| D31 | `sb_do_temper` is kept as a two-line retired label ("The forge is cold."), not deleted, following the label policy. | WP7 |
| D32 | Re-pointing the placeholder `bg city` scenes to the Tokyo districts is left to phase 3. The list is in section 10. | — |
| D33 | The HUD on the map screen shows the date and MENU only. The person view shows the date only. JOURNAL appears on the place view. | WP7 |
| D34 | Consecutive bond or affection toasts for the same person merge ("Yuji bond +4"). Toast kinds are colour-coded with a kanji. | WP7, WP0 |
| D35 | A place/period **arrival caption** fades after about 3 s, replacing a permanent place label. A "running on empty" line appears when stamina is below 25. | WP7 |
| D36 | Ijichi's ride-along unlocks after Utahime's arrival. *Ask Ijichi for a ride* is both a gate action and a person choice. Yotsuka (home) opens with Shibuya and Harajuku. | WP3, WP1 |
| D37 | The written hangouts are **25** `ev()` registrations (the judges' 27 and 29 were miscounts). The Kaito sprite lines are **41**: 39 `show mc` plus 2 `hide mc`, 5 of them in the prologue files and 36 elsewhere (verified with grep). | — |
| D38 | Beginning Arc Two goes through the campus journal: `Return(("arc_two",))` → `call arc_two_start`. Evolve's `sandbox_request` variable is dropped. | WP8, WP7, WP3 |
| D39 | The prologue is split into called sub-labels (`ch1_diner`, `ch1_the_thing`, `ch1_gojo`, `ch2_arrival`, `ch2_the_veil`, `ch2_yaga`, `ch2_first_years`). Each can be a memory and a precise resume point. | WP9 |
| D40 | `find_events()` stops checking `min_day`/`max_day`; `ev()` still accepts them, so nothing breaks. Mission gates replace the calendar, and WP10 deletes the now-unused arguments. Until WP3's gate binds every story/mission `ev()`, WP0's transitional `_calendar_gate` in `sb_events.rpy` keeps `min_day`/`max_day` for unbound events; WP3 deletes it, and WP10's `min_day` removal merges after WP3. | WP0, WP3, WP10 |

---

## 2. Ground rules for every package

### 2.1 Keeping saves loading

Ren'Py puts a save back at the **statement name** it was sitting on. When a file is recompiled, names are carried over from the old `.rpyc` by a difflib match on each statement's `diff_info` (`renpy/script.py:556`):

- For Say statements that is (who, what).
- For `call screen …` and other user statements it is the line text.
- For Python blocks it is the source.
- Unchanged statements keep their names, and edited ones get new names.

On load, Ren'Py rolls back through the saved log to the most recent statement that still exists. It calls `load_failed_label` only when none do.

The rules:

1. **Keep these statements textually identical** (the text, not the surrounding lines):
   - in `sb_loop.rpy`: `call screen sb_place`, `$ _r = _return`, `call screen sb_map`, `$ _m = _return`, `call screen sb_char(who)`, `$ _p = _return`, `call sb_activity(_p[1], _p[2])`, `call play_event(_story)`, `call expression "sb_do_" + _r[1]`, `call expression "act_" + aid pass (who)`;
   - in `sb_combat.rpy`: `call screen combat_screen`, `$ _a = _return`;
   - in `sb_events.rpy`: `call expression e["label"]` and the `if e["thread"]:` line after it;
   - in `script.rpy`: every line of `label start`.

   New branches go in as **new** `elif` lines, and new statements go before or after these.
2. **Never delete a label a save could be inside.** Retired labels stay, unreachable. The only deletions this phase are unregistering `ev()` entries, which are init code, not labels.
3. **Never rename a store variable.** Change a value's shape only with a migration (section 3.12). All new state is `default`.
4. **Never delete, move or force-recompile `game/*.rpyc` in the owner's folder.** They are gitignored and hold the statement names. Worktrees get copies (2.2).
5. **Screens keep their names and return tuples.** `sb_place`, `sb_map`, `sb_char`, `sb_hud`, `combat_screen`, `jjk_status` and `jjk_journal` all survive. `sb_map` gains an optional `layer="campus"`.
6. **Nothing un-picklable goes into saved state.** Registries are init-time data and are never saved. Saved state holds only `str`, `int`, `bool`, `None`, `list`, `dict`, `set` and `tuple`. Functions are referenced by name string.

### 2.2 Working method

- **Backup first (WP0 task 0).** Copy `game/*.rpyc`, `game/saves/` and `~/Library/RenPy/JJKgamemd-1788928056/` to `~/Desktop/JJK_backup_phase1_<date>/` before anything compiles in the owner's folder.
- **Branches.** WP0 commits to branch `phase1` in the owner's folder. Every wave-1 package works in its own git worktree at `~/Desktop/JJK_worktrees/wpN`, branched from `phase1` after WP0. It is merged back into `phase1` when its acceptance passes. Wave-1 packages own disjoint files, so merges are conflict-free.
- **`.rpyc` in worktrees.** Right after creating a worktree, copy the owner's `game/*.rpyc` into it (`cp -p`). Never copy `.rpyc` from a worktree back.
- **Smoke harnesses** run through `tools/smoke.sh` v2 (section 8.1). It runs in a scratch copy, so several harnesses can run at once, even from one checkout, and none touch saves, persistent data or `.rpyc`.
- **Lint** is `~/Desktop/renpy-8.5.3-sdk/renpy.sh <tree> lint`. The baseline today is clean: 2,099 dialogue blocks, 54 menus, 225 images, 37 screens. "Lint clean" means no report lines before `Statistics:` and no `VALIDATE:` lines (8.4).
- **The tree stays playable.** After every package merge, New Game → prologue → campus → sleep one night must run without an exception. Packages code against WP0's stubs, so this holds whatever order the merges happen in.

### 2.3 Writing rules (all new or edited text)

- **First person.** Kaito narrates in "I", present tense. Lines about Kaito and Sana together use "we" and "us". Everyone else says "you", `[mc_name]` or `[mc_surname]`. Nobody says `[mc_name]` before Gojo asks for it in the alley. `mcthink` lines are already "I". Menu prompts are narration, so they convert; choice captions are Kaito's own words.
- **No literal name.** "Kaito" and "Amagiri" appear only in the defaults and the `renpy.input` default (D29).
- **Staging without Kaito.** Kaito never appears on screen (`## first-person exception` comments allow deliberate future moments). Everyone faces the camera:
  - 1 person: `pos_c`.
  - 2 people: `pos_cl` / `pos_cr`.
  - 3 people: `pos_l` / `pos_c` / `pos_r`.
  - 4 or more: positions unchanged.
  - `show expression _p at pos_cr` beside Kaito becomes `pos_c`.
- **Expressions.**
  - Use the six attributes neutral / happy / serious / angry / surprised / sad, on the 13 tagged characters only: mc, yuji, megumi, nobara, maki, panda, toge, gojo, yaga, ijichi, shoko, utahime, sana.
  - Sticky change: `yuji happy "..."`. One-line change: `yuji @ surprised "..."`. Held mood: `show sana sad`.
  - Change a face every few lines at most.
  - **Never** give attributes to Mom, Dad, Oda, Kurose, Nade, `voice_` or the curses: they have no image tag, and Ren'Py raises an error.
- **Flags and stats stay put.** Every `flag()`, `gain()`, `add_bond()` and `add_aff()` stays on the same choice. Packages that rewrite a scene diff these lines before and after.
- **Placeholders are labelled.** Every placeholder scene starts with `## PLACEHOLDER — rewrite in phase 3`.

### 2.4 Code conventions

- A new system file has one `init` block for its registries, and `default` lines for its state at the bottom.
- Public functions carry a docstring naming their owning package, and their signatures are frozen by WP0 (section 6).
- A package may not remove or rename a symbol that another package uses. Changes go through WP11.
- Notifications go through `toast(text, kind, who, amount)` (3.1). Existing `renpy.notify` calls keep working, because `config.notify` routes into the same queue.

---

## 3. Data model

### 3.1 Hooks, migrations, recovery: `game/sb_hooks.rpy` (WP0, frozen afterwards)

```python
init -5 python:
    import builtins
    SAVE_VERSION = 1

    NEW_DAY_HOOKS = []      # [(order, fn)]    fn() — run at the end of new_day()
    EVENT_GATES = []        # [fn(e) -> bool]  find_events() drops e if any gate says False
    EVENT_DONE_HOOKS = []   # [fn(e)]          play_event runs these after the label + thread advance
    MIGRATIONS = []         # [(order, name, fn)]
    PLACE_ACTIONS = []      # dicts, see register_place_action
    VALIDATORS = []         # [fn() -> [str]]  run by lint (config.lint_hooks)

    def register_new_day(fn, order=50)
    def run_new_day_hooks()
    def register_event_gate(fn)
    def event_allowed(e) -> bool
    def register_event_done(fn)
    def run_event_done(e)
    def register_place_action(id, label, hint, cost=0, locs=None, when=None, order=50, explore=False)
        # when = NAME of a store function returning bool; the action runs `label sb_do_<id>`
    def registered_place_actions(loc) -> [(id, label, hint, cost)]   # filtered, sorted by order
    def register_migration(order, fn, name)
    def run_migrations(block=False) -> bool   # sorted by order; each in try/except
                                               # (re-raise if config.developer); toasts muted;
                                               # sets save_version; returns True if it upgraded;
                                               # calls renpy.block_rollback() if block and upgraded
    def ensure_state()                         # if save_version < SAVE_VERSION: run_migrations()
    def register_validator(fn)

    TOAST_SINK = builtins.list([None])  # WP7 puts toast_push here
    TOAST_MUTE = builtins.list([0])
    def toast(text, kind="info", who=None, amount=None):
        # muted while _in_replay or TOAST_MUTE[0]; else TOAST_SINK[0](...) if set,
        # else renpy.display_notify(text)   (never renpy.notify: that would loop)

    PROLOGUE_STEPS = [("ch1_diner","chapter_one"), ("ch1_the_thing","chapter_one"),
                      ("ch1_gojo","chapter_one"), ("chapter_one_b","chapter_one_b"),
                      ("ch2_arrival","chapter_two"), ("ch2_the_veil","chapter_two"),
                      ("ch2_yaga","chapter_two"), ("ch2_first_years","chapter_two"),
                      ("arc_one_open","arc_one_open")]
    def legacy_story_point() -> str            # see 3.13
    def prologue_plan(point) -> [label]        # remaining step labels; if the sub-labels don't
                                               # exist yet (pre-WP9), the remaining chapters instead

    config.after_load_callbacks.append(lambda: run_migrations(block=True))
    config.lint_hooks.append(_run_validators)  # prints "VALIDATE: <msg>" per problem

define config.load_failed_label = "load_recover"
define config.return_not_found_label = "return_recover"

default story_point = None       # the prologue step playing (set at the top of each step label)
default save_version = 0
default arc_start_day = 1        # set by arc_one_open
default actions_today = set()    # once-a-day actions ("hold", "rest", "racks", "veil", "lesson", "cap:control"…)
default hide_side_images = False # the prologue's blackout
default smoke_autoplay = False   # test harness hook (8.1): skips renpy.input, auto-answers combat
default persistent.mc_face = True
```

Labels `load_recover`, `return_recover` and `resume_story` are in 3.13. WP0 also adds `actions_today = set()` to `new_day()`.

### 3.2 World: `game/sb_world.rpy` (WP1)

**New places** (added to `LOCATIONS` and `LOC_ORDER`; x/y are kept only for `tools/genworld.py`):

| key | name | indoor | bg | x, y | desc |
|---|---|---|---|---|---|
| `utahime_office` | Utahime's Office | yes | `bg utahime_office` | 1480, 560 | Neat, traditional, and a mission board already fuller than Yaga's ever was. |
| `gojo_office` | Gojo's Office | yes | `bg gojo_office` | 1640, 560 | Sweets on every surface and a television the size of a door. |

The ridge's description becomes "Above the treeline, as far as the rope markers. Higher up, the veil." A comment above `LOCATIONS` says the map uses `AREAS`.

**AREAS** (ordered; the anchor is the card centre on `map_campus.png`):

| key | name | seal | places | anchor |
|---|---|---|---|---|
| `heart` | Courtyard & Gate | 門 | gate, courtyard | (960, 900) |
| `school` | Classrooms | 校 | classroom, cafeteria, infirmary | (420, 740) |
| `dorms` | Dormitories | 寮 | dorm, dorm_common, girls_dorm, rooftop | (900, 560) |
| `staff` | Staff Building | 職 | office, utahime_office, gojo_office | (1560, 440) |
| `grounds` | Training Grounds | 練 | training, dojo, storehouse | (1560, 760) |
| `mountain` | The Mountain | 山 | forest, riverside, ridge | (740, 290) |

Functions: `area_of(loc)`, `places_in(area)`.

**Schedules.** Each new character appears once in `SCHEDULE`, with `WEEKEND` overrides:

| who | Morning | Noon | Afternoon | Evening | Night | Weekend changes |
|---|---|---|---|---|---|---|
| utahime | utahime_office | utahime_office | utahime_office | cafeteria | - | Afternoon `-`, Evening courtyard |
| ijichi | gate | gate | gate | - | - | none |

**Flag schedules (D13).** `FLAG_SCHEDULES = []` holds entries `(flag, who, table_or_None)`. When the flag is set, `table` replaces that character's schedule, and `None` means off campus. `char_location` checks it before `schedule_overrides`. Phase 1 ships the list empty and tests it in the harness.

**Gojo.** `roll_gojo()` keeps `GOJO_SPOTS` roaming. `default gojo_in = False`.
- `gojo_in_on(day)` is deterministic: `Random(day*131+7).random() < 1/6`, never two days running (checked recursively and memoised), and False unless `intensive_done` (D17).
- `roll_gojo()` sets `gojo_in = gojo_in_on(day)`. On those days Gojo is at `gojo_office` Morning–Afternoon and roams the rest.
- `gojo_in_today()` reports it. Story milestones may still `pin("gojo", "gojo_office")`.
- `new_day()` toasts "Gojo is in today." (kind `info`) when it's true.

**Access** (`can_enter`, keeping the existing rules):
- `utahime_office`: needs the flag `utahime_arrived`; locked at Night ("Her door is shut. There's light under it.").
- `gojo_office`: before `intensive_done`, locked with "Locked. A note on the door says SOON! and has a drawing of him on it."; after that, locked only at Night.

**Clock.** `new_day()` keeps today's behaviour and adds `actions_today = set()` (WP0), `refresh_vitals()`, `hp = hp_max`, and the call to `run_new_day_hooks()`, which stays last. `KYOTO_DAY` and `days_left()` are deleted by WP0.

**Helpers:**
- `usual_places(who)` gives a string such as "Dojo (mornings) · Training Hall (afternoons) · Riverside (evenings)". Gojo's is "Nowhere you can predict. His office on the days he's in."
- `when_at(who, loc)` gives when someone is at a place, e.g. "weekday mornings, noon and evenings".

**Ridge extra (D15).**
- `register_place_action("veil", "Look up at the veil", "Free. Once a day.", locs=("ridge",), when="veil_ok")`.
- `veil_ok()` means `saw_the_ridge_veil` is set and `"veil"` is not in `actions_today`.
- `label sb_do_veil` is first person and rotates three short passages, counting with the flags `looked_at_veil_1..3`. The third ends on the mcthink "It's facing the school."
- It costs no time.

### 3.3 Tokyo layer: `game/sb_tokyo.rpy` (WP1)

```python
DISTRICT_ORDER = ["shibuya", "harajuku", "shinjuku", "kawasaki", "yotsuka"]
DISTRICTS[key] = dict(name, kanji, desc, places, bg, min_grade, needs_flag, locked_hint, lines)
```

| key | name | kanji | places (shown as "what's there") | bg | opens when |
|---|---|---|---|---|---|
| shibuya | Shibuya | 渋谷 | the scramble crossing, the station, an arcade, a café | `bg shibuya` | flag `ijichi_rides` |
| harajuku | Harajuku | 原宿 | Takeshita Street; supplies and sealing talismans (later) | `bg harajuku` | `ijichi_rides` |
| shinjuku | Shinjuku | 新宿 | neon streets, the station, rooftops at night | `bg shinjuku` | `ijichi_rides` and Grade 2 |
| kawasaki | Kawasaki | 川崎 | the cinema, Junpei's neighbourhood | `bg kawasaki` | `ijichi_rides` and flag `kawasaki_open` (Act III, phase 3) |
| yotsuka | Home — Yotsuka | 四塚 | my parents' house, the diner, the alley | `bg yotsuka` | `ijichi_rides` |

`lines` holds 2–3 first-person arrival lines for each district (WP1 writes them, following the writing rules in 2.3).

**Functions:**
- `tokyo_open()` is `has_flag("ijichi_rides")`.
- `district_state(key)` returns `(open, reason)`, with reasons in the player's words: "After Ijichi's ride-along", "Grade 2", "Act III".
- `trip_ok_now()`: Ijichi is at the gate this period, and it is Morning, Noon or Afternoon.
- `car_action_ok()`: `trip_ok_now()`, `tokyo_open()` and `here == "gate"`.

`default districts_visited = set()`

**label `sb_trip(key)`:**
1. A menu: "Half a day in [name]." Choices "Go." and "Not today." (return).
2. `scene bg car`, then one Ijichi line.
3. `scene` the district's background, and play its `lines`.
4. `districts_visited.add(key)`.
5. `call expression "district_" + key` if `renpy.has_label` (none exist in phase 1).
6. `advance_period(2)`, `here = "gate"`, `scene expression graded_bg()`.

A trip that starts in the Morning ends in the Afternoon, at the gate.

**label `sb_do_car`:**
- `call screen sb_map(layer="tokyo")`. This is a new, separate call statement; the existing `call screen sb_map` stays untouched.
- `("district", k)` → `call sb_trip(k)`.
- `("go", loc)` → walk there, as `sb_travel` does.
- It is registered with `register_place_action("car", "Ask Ijichi for a ride", "Into the city. Half a day.", cost=2, locs=("gate",), when="car_action_ok")`.

### 3.4 Grades, merit and per-character stats: `game/sb_grades.rpy` + `game/sb_energy.rpy` (WP2)

**The ladder:**

| key | name | rank | reserve cap | stat cap | talisman slots | merit to reach | how |
|---|---|---|---|---|---|---|---|
| `g4` | Grade 4 | 0 | 100 | 40 | 1 | — | assessed at roll call |
| `g3` | Grade 3 | 1 | 140 | 55 | 2 | 60 | then the promotion mission with Maki watching |
| `g2` | Grade 2 | 2 | 180 | 70 | 3 | 150 | then a Grade 1's word (Nanami, phase 3) |
| `s1` | Semi-Grade 1 | 3 | 220 | 85 | 4 | 260 | then a recommendation (phase 3) |
| `g1` | Grade 1 | 4 | 260 | 100 | 4 | — | two Grade 1 recommendations (Arc Two) |
| `sp` | Special Grade | 5 | None | None | 4 | — | `off_scale=True`; never reachable |

**API:**
- `GRADE_ORDER`, `GRADES`.
- `grade_key(v)`: a key passes through. A legacy **enemy** int is literal (4→g4, 3→g3, 2→g2, 1→g1, 0→sp). `None` → `None`.
- `grade_rank(v)`: −1 for None/ungraded.
- `grade_label(v)`: accepts a key, an int or None; None → "Not yet assessed".
- `player_grade()`, which returns `store.grade`.
- `grade_cap(kind)`: `"stat"` or `"reserve"`, taken from the player's grade (g4's numbers while None).
- `talisman_slots(key=None)`, `merit_needed(key=None)`.
- `add_merit(n, why="")`: toast kind `grade`, e.g. "Merit +30 — The Sun Mall".
- `merit_progress()` → `(merit, need, next_key)`.
- `next_grade_text()` for the Stats tab, e.g. "Merit 34/60, then a promotion mission — Maki will watch."

**Promotion.** `promote(who, key, why="", quiet=False)`:
- For `"mc"` it sets `store.grade`; for anyone else it sets `npc_state[who]["grade"]`.
- It never lowers a value.
- It appends `dict(day, who, grade, why)` to `promotions_log`.
- It toasts "Nobara — promoted to Grade 2" (kind `grade`, in their colour) unless quiet.
- For NPCs it sets `pending_remarks[who] = True`.

Related helpers:
- `recent_promotion(who, days=3)`.
- `pop_remark(who) -> bool`: returns and clears the pending remark.
- `pick_team(n, min_key=None) -> [who]`: rostered students ranked by grade rank, then bond (D12, for phase 3).

**Player numbers** stay in the existing store variables: `ce`, `ce_max`, `control`, `output`, `insight`, `hp`, `hp_max`, `stamina`.
- `default grade = None` (D16). The value is a key from roll call on.
- `gain(stat, amount, quiet=False)`:
  - It keeps today's diminishing returns.
  - It caps `control` and `output` at `grade_cap("stat")`. It never lowers a value already above the cap.
  - Once per stat per day it toasts "Control is at the Grade 4 limit — a promotion lifts it" (tracked in `actions_today` as `"cap:<stat>"`).
  - `insight` stays capped at 100.
  - Toasts use kind `stat`.
- `raise_reserve(n)` replaces every hard-coded `ce_max = min(...)`. It stops at `grade_cap("reserve")` and never lowers.
- `default merit = 0`, `default merit_granted = set()` (keys such as `"mission:m_sunmall"` or `"ch5_recommendation"`).

**NPC stats.** `NPC_BASE` (define):

| who | grade | reserve | control | output | rate (xp/day) | max grade in Arc One | notes |
|---|---|---|---|---|---|---|---|
| yuji | g4 | 110 | 28 | 62 | 3 | g2 | |
| megumi | g2 | 150 | 58 | 44 | 2 | s1 | |
| nobara | g3 | 120 | 46 | 50 | 2 | g2 | |
| maki | g4 | 0 | 30 | 88 | 2 | g4 | `restricted=True`, note "Heavenly Restriction — and the Zenin keep her grade low" |
| panda | g2 | 160 | 42 | 70 | 1 | s1 | |
| toge | s1 | 170 | 62 | 56 | 1 | s1 | |
| gojo | sp | — | — | — | 0 | sp | `off_scale=True` |
| yaga | g1 | 220 | 80 | 78 | 0 | g1 | role "Principal" |
| utahime | s1 | 200 | 72 | 50 | 0 | s1 | role "Kyoto teacher" |
| shoko | None | 180 | 90 | 10 | 0 | — | role "Doctor" |
| ijichi | None | 60 | 30 | 8 | 0 | — | role "Assistant manager" |
| nanami, todo, mei_mei | g1 | — | — | — | 0 | — | registered, hidden until met |
| miwa | g3 | — | — | — | 0 | — | hidden until met |
| yuta | sp | — | — | — | 0 | — | hidden |

- `default npc_state = {}` maps `who → dict(grade, xp, promoted_day)` and is created lazily.
- `npc_stats(who)` returns `grade`, `ce_max`, `control` and `output`, each computed as base + `min(30, xp // 6)` (so it never drops), plus `off_scale`, `restricted`, `role` and `note`.
- **Growth** (`grow_everyone`, a new-day hook). Every rostered NPC with rate > 0 gains `rate` xp, plus a jitter of 0 or 1 from `Random(day*1009 + zlib.crc32(who))`. xp is cumulative. They are promoted when all of these hold:
  - xp ≥ `PROMO_XP[next]`, with `PROMO_XP = {"g3": 40, "g2": 130, "s1": 290}` (cumulative);
  - the next rank ≤ their max grade;
  - the next rank ≤ `ACT_STUDENT_CAP[acts_done()]`, where `ACT_STUDENT_CAP = {0: None, 1: "g3", 2: "g2", 3: "g2", 4: "s1", 5: "s1"}` and None means no promotions (D21).
- **Working together.** `train_together(who, n=3, stat=None)`: the NPC gains `2*n` xp, and if `stat` is given the player gets `gain(stat, 1)`. It is called by:
  - sparring and `act_train` (n=3, "output");
  - `act_study` (n=2, "insight");
  - `act_swim` and `act_walk` (n=1);
  - board jobs (n=6).
- `sorcerer_power(who)`:
  - player: `(control+output)/2 + insight/4 + 6*tech_tier()[0]`;
  - NPC: `(control+output)/2`;
  - off-scale: 999.

**Last Light** (`sb_energy.rpy`). `TECHNIQUES` keeps only `"timestop"` (the internal key never changes):

```python
"timestop": dict(name="Last Light", jp="残光 · Zankō", tag="Control", scales="control",
    blurb="I hold the instant the lights went out. It is not speed and it is not foresight: the second simply does not happen until I let it.",
    verb="Hold", verb_desc="Once a day, spend most of my reserve and the hour does not pass.",
    tiers=[("Stutter", "A held half-second. Enough to be somewhere else.", 0),
           ("Held Second", "A full second, and I can move inside it.", 30),
           ("Arrest", "Long enough to walk across a room nobody is crossing.", 60),
           ("The Second That Did Not Happen", "Domain Expansion.", 90)])
```

- `tech()` returns `TECHNIQUES["timestop"]` whatever `store.technique` holds. `default technique = "timestop"`.
- Keep `add_ce`, `tech_stat`, `tech_tier`, `next_tier`, `spend_ce`, `restore_ce` and `spend_stamina`. `grade_name()` becomes `return grade_label(store.grade)`.
- With the caps, Held Second is reachable at Grade 4, Arrest from Grade 2, and the fourth tier only at Grade 1.

**Grade card.**
- `screen grade_card(key, kicker)`, with `kicker` "ASSESSED" or "PROMOTED".
- `label show_grade_card(key, kicker="PROMOTED")`: shows the card, `renpy.pause(3.0)`, hides it with a dissolve.

**State:** `merit`, `merit_granted`, `npc_state`, `promotions_log = []`, `pending_remarks = {}`.

### 3.5 Combat data: `game/sb_combat.rpy` (WP2)

- `MOVES = {"timestop": [Stutter, Held Second, Arrest]}`, with today's numbers unchanged. `moves_available()` reads `MOVES["timestop"]`. The heal, burn and ally_buff branches in `combat_player`/`combat_enemy` are deleted; stored `cb` keys are read with `.get()`.
- `ENEMIES` grades become keys: `alley_curse` `"g1"`, `nade_curse` `"g3"`, `warehouse` `"g2"`.
- `alley_curse` gains `rounds=4`. After round 4, `combat_enemy` sets `cb["over"] = "down"` and logs "It stops playing with you." `combat_begin` copies it as `cb["rounds"] = e.get("rounds")`.
- New entry `promo_g3`: name "Grade 3 assessment curse", grade `"g3"`, hp 100, power 16, sprite `"curse small"`, tells heavy / fast / grab.
- `combat_begin(key_or_dict, ally=None, flee_ok=True, bg=None)` accepts an enemy dict (for board fights in phase 2). It floors HP at half: `hp = max(hp, hp_max // 2)`.
- `combat_screen` prints `grade_label(_c["grade"])` in place of "GRADE [_grade]". When `smoke_autoplay` is set, it adds `timer 0.05 action Return((ANSWERS[_c["kind"]],))` (8.1).
- `refresh_vitals()` is unchanged.

### 3.6 Missions: `game/sb_missions.rpy` + `game/missions_stubs.rpy` (WP3)

**One record format** (defined at init, never changed; ids stay stable for ever):

```python
mission(id, kind,            # "story" | "character" | "promotion"
        act, order,          # act id "P","I".."V"; order spaced by 10 for inserts
        title, summary, objective,   # objective: short verb phrase for the NEXT line
        label=None,          # None or a missing label  => status "unwritten"
        trigger="auto",      # "auto" (an ev() story event finds you) | "start" (a gold button/choice)
        where=None,          # loc | tuple of locs | None (= wherever with_who / who is)
        with_who=None,       # giver who must be present for "start"
        who=None,            # character missions: whose story
        periods=None,        # tuple or None
        cost=0,              # periods charged by start_mission AFTER the label (new labels only)
        gate=dict(after=None, gap_days=0, flags=(), not_flags=(), min_bond=0,
                  min_grade=None, merit=0, thread=None, gojo_in=False, act_done=None),
        done_if=(),          # any of "event:<label>", "flag:<f>", "grade:<key>" (rank ≥), "mission:<id>"
        skip_if=(),          # same syntax; "skipped" counts as satisfied
        optional=False, group=None,        # group: "The Surveyor" → shown as 2/3
        rewards=dict(merit=0, bond={}, yen=0, items={}, flags=()),
        hidden_until_met=False)
```

`MISSIONS`, `MISSION_BY_ID`, `MISSION_BY_LABEL`, `ACTS` (id, title, kanji, grade band), `RETIRED_LABELS = {"st_board_open", "ev_patrol"}`.

**Status** is computed from state and cached until the next interaction (D22). It is the first that applies of:

1. `done`: any `done_if` is true, or the id is in `missions_done`.
2. `skipped`: any `skip_if` is true.
3. `closed`: `mission_state[id] == "closed"` (Arc Two).
4. `unwritten`: no label, or `not renpy.has_label(label)`.
5. `active`: `mission_state[id] == "active"` (started, scene not finished).
6. `waiting`: everything is met except that the gap day or retry day hasn't come yet. This shows as "tomorrow" or "in 2 days".
7. `available`:
   - **Story chain.** Every earlier non-optional story row is done, skipped or unwritten. `day ≥ done_day(previous written step) + gap_days`, where the prologue's done day is `arc_start_day` (D23) and backfilled steps count as day 0.
   - **Gates.** `gate` flags / not_flags / min_bond (with `who` or `with_who`) / min_grade / merit / thread `(tid, stage)` / gojo_in / act_done all pass.
   - **Retry.** `day ≥ mission_retry_day.get(id, 0)`.
8. `locked` otherwise.

`mission_reason(id)` gives the lock in the player's words: "Needs Grade 3", "Bond 40 with Megumi", "After The Sun Mall", "Merit 34/60", "Try again tomorrow", "Weekday mornings".

**State** (all `default`): `mission_state = {}`, `missions_done = set()`, `mission_done_day = {}`, `mission_retry_day = {}`, `last_objective = None`.

**Hooks** (registered by WP3):
- **Event gate.** An event whose label is in `MISSION_BY_LABEL` fires only while that mission is `available`. A label in `RETIRED_LABELS` never fires. Once Arc Two has started, arc-1 hangouts with `thread=` stop firing if that thread is unfinished.
- **Event done.** `complete_mission(id)` records `mission_done_day[id] = day`, adds the id to `missions_done`, clears `mission_state[id]`, and pays the rewards once (`merit_granted` key `"mission:<id>"`). Rewards merit (`add_merit`), bond, yen (`add_yen`), items (`give_item`) and flags.

**`label start_mission(mid)`:**
1. `mission_state[mid] = "active"`.
2. If an `EVENTS` entry has the label: `call play_event(e)`. This keeps `done_events` and thread advancement exactly as today; the done hook completes the mission.
3. Otherwise: `call expression label`. Then, unless the scene called `mission_fail(mid)`, run `complete_mission(mid)`.
4. Charge `cost` with `advance_period(cost)`.

`mission_fail(mid)` sets `mission_retry_day[mid] = day + 1`, removes the `"active"` state and toasts "Not today. Try again tomorrow."

**Queries:**
- `missions_list(kind=None, status=None, act=None, who=None)`.
- `missions_here(loc)`: start-type, `available`, `where` matches, the giver is present and the period fits.
- `missions_with(who, loc=None)`.
- `mission_markers()` → `{loc: [(text, kind)]}`. For example "Yaga · The Sun Mall" at the giver's place, "Board · 3 jobs" at Utahime's office, "Gojo is in" at his office.
- `next_for(who)` → `(text, where)`. Priority: a mission with them, then a new bond scene (`has_event("hangout", who)`), then the next activity unlock (`next_unlock`), then "Talk".
- `act_done(act)`: at least one written row, and all non-optional written rows done or skipped.
- `acts_done()`: consecutive acts done from I.
- `act_progress(act)` → `(done, written, total)`.
- `main_story_complete()`: every non-optional story row is written and done. It is always False in phase 1, except when a review-tools flag `dev_story_complete` is set and `config.developer` is on.
- `current_objective()` → `dict(text, where, when, mid)` or None. `objective_text()` gives the one-line string.

**The objective composer:**
- The first story row, in order, that is `active`, `available` or `waiting`:
  - auto rows: "<objective> — <periods>, wherever I am", with "tomorrow" or "in N days" when waiting;
  - start rows: "<objective> — <place>, <when_at(giver, place)>".
- If the first unfinished row is locked by merit: "Earn merit on Utahime's board: 34/60 — then the promotion fight".
- If only unwritten rows remain: the best available character mission ("Ijichi has something for me — Main Gate, mornings to afternoons").
- Otherwise: "The story continues in a later build. The board and everyone on campus are open."

#### 3.6.1 The main story, from existing scenes plus new rows

Unwritten rows are **bold italic**. The labels of all written rows exist today, except the ones marked NEW (written by WP3 in `missions_stubs.rpy`).

| order | id | label | trigger · where · periods | gap | gate / notes | done_if (old saves) | merit | objective (NEXT line) |
|---|---|---|---|---|---|---|---|---|
| 0 | m_prologue | — | — | — | | flag:settled_in | | — |
| **Act I · Grade Four** (band: Grade 4) |
| 110 | m_roll_call | st_roll_call | auto · Morning | 1 | | event:st_roll_call, flag:roll_call | 5 | Roll call with Principal Yaga |
| 120 | m_utahime | st_utahime_office NEW | auto · M/N/A | 1 | ev() priority 96 | event:st_utahime_office, flag:utahime_arrived | 0 (items: paper_ward, sealing_talisman ×2) | Someone is moving into the room next to Yaga's |
| 130 | m_sunmall | ev_mission_sunmall | start · office · with yaga | 1 | | event:ev_mission_sunmall, flag:sunmall_done | 30 | Yaga has a mission for the first-years |
| 140 | m_aftermath | st_aftermath | auto · Morning | 1 | D14 | event:st_aftermath, flag:aftermath_done | 5 | Shoko wants to look at all four of us |
| 150 | m_kurose | st_kurose | auto · Afternoon/Evening | 0 | | event:st_kurose, flag:kurose_met | 0 | A man from auxiliary management is waiting outside Yaga's office |
| 160 | ***m_detention*** | — | | | | | | The detention center |
| 170 | ***m_aftermath_2*** | — | | | | | | Aftermath |
| 180 | ***m_infirmary*** | — | | | | | | The infirmary |
| **Act II · The Ones Who Stay** (band: Grade 4 → Grade 3) |
| 210 | m_second_years | st_second_years | auto · Afternoon | 1 | | event:st_second_years, flag:met_second_years | 0 | The second-years are back from wherever they were |
| 220 | m_noise | st_noise | auto · Evening | 1 | | event:st_noise | 10 | Stay on campus into the evening |
| 230 | m_oda_letter | st_oda_letter | auto · Evening | 1 | | event:st_oda_letter, flag:oda_letter_read | 0 | A letter is on its way from home |
| 240 | m_intensive | st_intensive | auto · Afternoon | 2 | Gojo's first lesson | event:st_intensive, flag:intensive_done | 0 | Gojo wants eleven minutes of my time |
| 250 | ***m_strongest*** | — | | | | | | "The Strongest" |
| 260 | ***m_secret*** | — | | | | | | The secret |
| 270 | m_promo_g3 | st_promotion_g3 NEW | start · training/dojo · with maki | 1 | merit 60; kind promotion | grade:g3 | 0 | Promotion fight: find Maki (Dojo mornings, Training Hall afternoons) |
| **Act III · Overtime** (band: Grade 3 → Grade 2) |
| 310 | ***m_nanami*** | — | | | | | | Nanami |
| 320 | m_nade_1 | ms_nade_1 | start · office · with yaga | 1 | group "The Surveyor" | event:ms_nade_1, flag:nade_named | 25 | Yaga has a name |
| 330 | m_kurose_2 | st_kurose_2 | auto · Evening | 1 | | event:st_kurose_2, flag:kurose_leak | 0 | Something from Kurose is waiting in my room |
| 340 | ***m_cinema*** | — | | | | | | The cinema |
| 350 | ***m_junpei*** | — | | | | | | Junpei |
| 360 | m_nade_2 | ms_nade_2 | start · office · with yaga | 2 | group | event:ms_nade_2, flag:nade_traced | 25 | Yaga wants the annexe looked at |
| 370 | m_oda_2 | st_oda_2 | auto · Evening | 1 | optional; flag oda_answered | event:st_oda_2, flag:oda_thread_open | 0 | Oda-sensei writes back |
| 380 | m_nade_3 | ms_nade_3 | start · office · with yaga | 2 | group | event:ms_nade_3, flag:nade_map | 30 | Yaga knows where Nade is |
| 390 | ***m_satozakura*** | — | | | | | | Satozakura High |
| 395 | ***m_promo_g2*** | — | | | kind promotion | grade:g2 | | Grade 2, on a Grade 1's word |
| **Act IV · Goodwill** (band: Grade 2) |
| 410 | m_roster | st_roster | auto · Noon | 1 | the Goodwill announcement | event:st_roster | 0 | The Kyoto roster is going up |
| 420 | m_night_before | st_night_before | auto · Evening/Night | 2 | | event:st_night_before, flag:arc1_complete, flag:night_before_done | 0 | The night before Kyoto |
| 430–470 | ***m_kyoto_arrives, m_team_battle, m_attack, m_baseball, m_new_faces*** | — | | | | | | |
| **Act V · Cursed Womb** (band: Grade 2 → Grade 1 candidate) |
| 510–550 | ***m_yasohachi, m_meimei, m_recommended, m_yuta_call, m_sketchbook*** | — | | | | | | |

The existing `ev()` registrations keep `periods`, `loc`, `priority` and `requires`. WP10 deletes their `min_day` arguments; WP0 has already stopped `find_events` from reading them (D40). `st_board_open` and `ev_patrol` are unregistered by WP10 and blocked by the gate until then; their labels stay. `sb_do_missions` and `sb_patrol` stay as unreachable labels.

The story alone pays merit 5 + 30 + 5 + 10, plus 20 from the ch5 recommendation: **70 by the end of Act II** (D18). Act III adds 80 more (**150**), which will be the Grade 2 threshold once `m_promo_g2` is written.

#### 3.6.2 Character missions

The label is `cm_<who>_<n>`, the trigger is `start` with `who`, and `where` is None (wherever they are). They show as `unwritten` until the label exists. **Written in phase 1:** `cm_ijichi_1` and `cm_maki_1`, both placeholders.

| who (thread) | 1 | 2 | 3 |
|---|---|---|---|
| yuji (yuji_countdown) | Grandpa's Last Words: bond 30, thread ≥1 | The Basement: flag `yuji_secret` (phase 3) | A Finger Retrieval: g3, bond 50 |
| megumi (megumi_tsumiki) | The Hospital: bond 35, thread ≥1 | Divine Dogs: g3 | What the Zenin Wanted: bond 65 |
| nobara (nobara_saori) | Harajuku: bond 30, flag `ijichi_rides` | Straw Doll: g3 | Saori's Letter: bond 60, thread ≥1 |
| maki (maki_zenin) | **The Armory** (written): bond 10, flag `met_second_years` | Mai, Before Kyoto: after m_roster | Playful Cloud, on Loan: bond 70, g2 |
| panda (panda_made) | Gorilla Core: bond 30 | Yaga's Son: bond 45 | Three Hearts: bond 65, thread ≥2 |
| toge (toge_voice) | Onigiri Words: bond 20 | Throat Medicine: bond 40 | Don't Move: g3 |
| gojo (gojo_measure) | Infinity: `gojo_in`, flag `intensive_done` | Unlimited Void, From Outside: act II done | Under the Blindfold: bond 60 |
| utahime | What She's Helping Gojo With: bond 30 | Rivals: bond 45 | Kyoto's Teacher: after m_roster |
| shoko (shoko_remembers) | Coffee in the Infirmary: bond 20 | Reverse Cursed Technique, in Theory: bond 40 | Old Friends: bond 60, thread ≥1 |
| yaga | The Cursed Doll Workshop: bond 30 | Why Do You Do This?: bond 60 | — |
| ijichi | **Ride-Along** (written): after m_utahime; at the gate, M/N/A; cost 2 | The Veil: bond 30, g3 | — |
| nanami (hidden) | The Bakery | Ratio | — |
| todo (hidden) | What Type of Woman? | Brother | The Idol Handshake Event |
| miwa (hidden) | Simple Domain | An Autograph from Gojo | — |
| mei_mei (hidden) | Everything Has a Price | — | — |

How the existing content maps:
- **Hangouts.** The 25 hangout `ev()`s (`ev_<who>_1..3`, `*_r1`, gojo/yaga) stay the bond scenes behind "Spend time together". They keep advancing THREADS.
- **THREADS** stay the backbone. The People tab shows them, and character missions are gated on them.
- **ACTIVITIES** stay the catalogue, and SMALLTALK stays as Talk. Confide, stand, romance and intimate are unchanged.
- **Journal cast.** `JOURNAL_CAST` (ordered): yuji, megumi, nobara, maki, panda, toge, gojo, utahime, shoko, yaga, ijichi, nanami, todo, miwa, mei_mei, yuta, sana. Each entry has a name, colour and role (for those without a `CAST` entry), a met rule (in roster, or a flag) and a hint. For example:
  - maki: "A second-year. She trains at dawn."
  - utahime: "Someone is clearing the room next to Yaga's."
  - nanami: "A Grade 1 who hates overtime. Act III."
  - todo: "Kyoto's loudest third-year. Act IV."
  - miwa: "A Kyoto second-year. Act IV."
  - mei_mei: "Does nothing for free. Act V."
  - yuta: "A voice on Gojo's phone. Act V."
  - sana: always shown, as a memorial card.

#### 3.6.3 Arc Two

- `begin_arc_two()` sets flag `arc2_started` and `arc = 2`. Every Arc One character mission that isn't done gets `mission_state[id] = "closed"`. Memories are untouched.
- `label arc_two_start`:
  1. `menu`: "This begins Arc Two. Character stories you haven't finished in Arc One will close." — "Begin Arc Two" / "Not yet".
  2. On yes: `begin_arc_two()`.
  3. The card `chapter_card("ARC TWO", "Shibuya Is a Long Way Off", "Arc Two arrives in a later build. Everything you finished stays in your journal.")`.
  4. Back to campus.

It is reached only from the campus journal (D38), and only while `main_story_complete()` is true.

### 3.7 Utahime's board: `game/sb_board.rpy` (WP4)

**Parts** (define):

- `BOARD_CASES` (6): Missing persons · A haunting · Residual clean-up · A school after hours · Unexplained injuries · Livestock deaths.
- `BOARD_PLACES` (8):
  - a drainage tunnel in Nerima
  - a closed maternity ward in Adachi
  - a dead platform under Ikebukuro
  - a school pool in Setagaya, after hours
  - an apartment stairwell in Kita
  - a train depot in Shinagawa
  - a riverbank underpass in Edogawa
  - a karaoke box in Koenji that closed mid-song
- `BOARD_CURSES`, 3 or 4 per grade:
  - g4: a residual that eats light bulbs · a stairwell crawler · a grudge the size of a dog
  - g3: a mimic that uses the missing person's voice · a nest of finger-length curses · a pool drowner
  - g2: a curse that only moves in the dark · a platform pusher · a thing wearing the building
  - s1: a named curse with a domain it can't close yet · a crowd that is one curse
- `BOARD_TWISTS`:
  - `dark` +4 "It only moves in the dark"
  - `civilian` +6 "Someone is still inside"
  - `split` +5 "There are two of them"
  - `decoy` +3 "The reported curse is a decoy"
  - `daylight` −3 "It sleeps in daylight" (mornings only)
  - `none` 0
- `PARTNER_LINES[who] = dict(arrive, win, hurt)` for yuji, megumi, nobara, maki, panda and toge, in first-person narration around their spoken line.

**State:** `board_offers = []`, `board_week = -1`, `board_log = []` (last 30 runs).

An offer is a plain dict: `id, grade, true_grade, case, place, curse, twist, title, blurb, merit, yen, drop, senior_only`. A taken card is `dict(taken_by=who, grade, title)`, read-only.

**Generation** (a new-day hook plus migration 80):
- Offers regenerate on Mondays, seeded with `Random(week*7919 + 11)`. When an offer is taken, a replacement appears the next day.
- Three offers: two at or below your grade (Grade 4 while `grade` is None) and one a grade up with `senior_only=True`.
- About 1 in 6 offers at g4 or g3 is **misgraded**: `true_grade` is one step higher. That is Wakuri's hand.
- One taken card appears while any rostered student outranks you (D12).

**Rules:**
- `board_host()` → `("utahime", "utahime_office")`, or `("ijichi", "office")` once the flag `utahime_leads_kyoto` is set (D13).
- `board_open()`: flag `mission_board_open`, `here` is the host place, and the host is there this period (`char_location`). An old save carries `mission_board_open` from the retired `st_board_open`, but its board stays closed until Utahime is rostered, because an unrostered character has no location.
- `register_place_action("board", "Mission board", "Graded jobs. Bring someone.", locs=("utahime_office", "office"), when="board_open")`.
- **Partners:** anyone rostered with an NPC grade that is not None, excluding gojo, yaga and utahime, and currently on campus. A senior partner is anyone whose grade rank is above yours. You can't go alone ("Always take someone," Utahime's rule).
- **Cost:** 2 periods and 25 stamina. Refused in the Evening and at Night, with the line "Utahime doesn't send anyone out after dark."

**Resolve** (phase 1 resolves automatically; phase 2 turns it into a fight):
- power = `sorcerer_power("mc") + 0.6 * sorcerer_power(partner)`, times a factor between 0.9 and 1.1 (seeded by offer id and day).
- difficulty = g4 30 / g3 55 / g2 80 / s1 110 for the **true** grade, plus the twist's modifier.
- Outcome: `clean` if power ≥ difficulty; `costly` if power ≥ 0.7 × difficulty; `withdrew` otherwise.

**Rewards:**
- merit: g4 10 / g3 18 / g2 28 / s1 40 (the posted grade), times 1.0 clean, 0.6 costly, 0 withdrew;
- yen: g4 3,000–6,000 / g3 6,000–10,000 / g2 10,000–15,000 / s1 15,000–20,000;
- partner bond +5 clean / +6 costly / +2 withdrew;
- `train_together(partner, 6)`;
- drops: 30% a sealing talisman; 10% a not-yet-owned talisman of the posted grade (g4 paper_ward or steady_hand, g3 deep_well or iron_seal).

All of it is paid exactly once per run.

**Misgrade reveal.** A misgraded job gets an extra narration beat, and a toast "Filed as Grade 3. It wasn't." It counts in `misgrade_count()` and sets flag `wakuri_clue`.

**Labels and screens:**
- `label sb_do_board` → `screen board_screen` → `screen board_partner(offer)` → `label run_board_mission(offer_id, partner)`.
- The narration is 6–10 first-person lines built from the parts, plus the partner's `arrive` / `win` / `hurt` line and the outcome.
- `board_summary()` gives the journal what it needs: offers, taken cards, the last 10 log rows and the misgrade count.

### 3.8 Items and equipment: `game/sb_items.rpy` (WP6)

`ITEMS[id] = dict(name, kind, grade, special, sealed, stack, desc, effect, fx, source, from_flag, hidden)`. Kinds: `keepsake`, `sealing`, `supply`, `mission`, `tool`, `talisman`. `fx` holds the phase-2 numbers (stored now, not applied).

| id | kind | grade | notes |
|---|---|---|---|
| photo, hachimaki, watch | keepsake | — | from `took_photo` / `took_hachimaki` / `took_watch` |
| oda_letter | keepsake | — | from `oda_letter_read` |
| daisy_clip | keepsake | — | `hidden`; phase 3 hands it out; it unlocks a Sana memory (D11) |
| kurose_card | mission | — | from `kurose_card` |
| kurose_photocopy | mission | — | from `kurose_leak` |
| presigned_form | mission | — | from `nade_traced` |
| nade_map | mission | — | from `nade_map` ("my home town circled") |
| sealing_talisman | sealing | g4 | stacks; binds a curse for a turn (phase 2) |
| first_aid | supply | — | stacks; defined, not handed out in phase 1 |
| slaughter_demon | tool | g4 | armory; fx `{"bleed": 3}` |
| nunchaku | tool | g3 | armory; fx `{"chain": 1}` |
| playful_cloud | tool | g2 | story (Maki's third mission) |
| split_soul | tool | s1 | story (Act V) |
| inverted_spear | tool | sp | `sealed="Arc Two"`; visible in the armory |
| paper_ward / steady_hand | talisman | g4 | +10 reserve / techniques cost less (`{"reserve":10}` / `{"tech_cost":-0.1}`) |
| deep_well / iron_seal | talisman | g3 | `{"reserve":20,"recover":-0.1}` / `{"strike":0.15,"guard":-0.15}` |
| spark / held_breath | talisman | g2 | `{"bf_window":0.1}` / `{"hold_cost":-0.15,"hold_beats":1}` |
| afterglow / black_sun | talisman | g1 | `{"bf_refill":0.5}` / `{"bf_mult":3.0,"bf_window":-0.1}` |
| unending_moment, the_zone, finger_wrap, tengens_seal | talisman | sp | `special=True`; bound by story; `tengens_seal` also sealed "Arc Two" |

**State:** `inventory = {}` (id → count), `items_granted = set()`, `yen = 0`, `equipped_tool = None`, `equipped_talismans = []`, `bound_specials = set()`.

**API:**
- `give_item(id, n=1, quiet=False)` (toast kind `item`), `take_item`, `has_item`, `item_count`, `items_in(kind)`, `add_yen(n)`.
- `can_wear(id)` → `(ok, reason)`. The reasons: "Needs Grade 2"; "Special: bound by story"; "A special is already worn"; "No free slot — opens at Grade 3"; "Sealed — Arc Two".
- `equip_talisman(id)`, `unequip_talisman(id)`, `equip_tool(id or None)`. All three call `renpy.retain_after_load()` (D4).
- `armory_open_now()`: `here == "storehouse"` and `has_flag("armory_open")`.
- `armory_tools()` → `[(id, state, reason)]`, where the state is `take`, `owned`, `sealed` ("Sealed until Grade 3"), `story` ("Story reward") or `arcii` ("Sealed — Arc Two").
- `sync_keepsakes()` is idempotent (keys `"flag:<f>"` in `items_granted`). It runs as a new-day hook and as migration 70 (D24).

**Rules:**
- Slots come from `talisman_slots()`.
- A talisman's grade rank must be ≤ yours; while `grade` is None, Grade 4 applies.
- Only one special can be worn, and only one in `bound_specials`.
- One tool in hand.
- The armory releases tools whose rank is ≤ yours, once `armory_open` is set.

**Registration:**
- `register_place_action("armory", "Armory", "Cursed tools released at your grade.", locs=("storehouse",), when="armory_open_now")`.
- `label sb_do_armory` → `screen armory`.

Before `armory_open`, the old storehouse action stays as "Look through the racks" (WP7, once a day, insight +1).

### 3.9 Memories and replay: `game/sb_memories.rpy` (WP5)

`MEMORIES` entries: `dict(id, title, who=(), act, label, args=(), seen=rule, hint, unlock=None, bg)`. The `act` is Prologue / I / II / III / IV / V / Bonds / Sana. The seen rule is one of:
- `("label", name)`: in `memories_seen`;
- `("event", label)`: in `done_events`;
- `("flag", name)`;
- `("act", "aid:who")`: in `seen_acts`;
- `("together", who)`.

**Contents:**
- **Prologue sub-labels** (D39):
  - `ch1_diner` "Nine Hundred Yen" (sana)
  - `ch1_the_thing` "The Thing She Told Me" (sana)
  - `ch1_gojo` "The Man in the Blindfold" (gojo)
  - `chapter_one_b` "The Offer" (gojo)
  - `ch1b_goodbye` "Breakfast for Four"
  - `ch2_arrival` "The Strongest of Today" (gojo, ijichi)
  - `ch2_the_veil` "The Veil on the Ridge" (gojo)
  - `ch2_yaga` "Why Are You Here?" (yaga)
  - `ch2_first_years` "Three First-Years" (yuji, megumi, nobara)
- **Main story:** every written story row. `chapter_four` is "Kawagoe Sun Mall" and `chapter_five` is "What Should Have Happened", recorded through their labels.
- **Bonds:** all 25 hangouts (WP5 reads each and titles it), plus `act_confide`, `act_stand`, `act_rom_*` and `act_int_*` per person. These replay through `mem_play` with `args=(who,)`.
- **Sana:** "The Thing She Told Me" and "Nine Hundred Yen", plus three locked flashbacks:
  - *The Diner*: label `sana_mem_diner`; unlock `("district", "yotsuka")`; hint "A trip home might bring this back."
  - *The Daisy Clip*: `sana_mem_daisy`; unlock `("item", "daisy_clip")`; hint "Something of hers."
  - *The Teacher Ranking*: `sana_mem_ranking`; unlock `("flag", "oda_letter_read")`; hint "Someone she ranked first."

  When the trigger is met but the label is unwritten, the tile shows "Written in a later build".

**Recording (D6).**
- `default memories_seen = {}` maps label → day.
- `config.label_callbacks.append(_mem_label_cb)` records labels in `MEMORY_LABELS` when `not _in_replay`.
- `default seen_acts = set()` is filled by `record_act(aid, who)`, which `sb_activity` calls (WP7).
- Legacy fallbacks for old saves: `confided_<who>`, `did_stand_<who>`, `town_date_<who>`, `close_<who>`, `together`, `talked_about_after_<who>` (WP5 confirms each flag name against the act scenes).

**Replay.** `memory_replay(mem)` → `Replay("mem_play", scope=memory_scope(mem), locked=False)`.
- `memory_scope` copies `mc_name`, `mc_surname`, `flags` (a copy), `roster`, `bonds`, `affection`, `together`, `threads`, `technique`, `grade`, `control`, `output`, `insight`, `ce`, `ce_max`, `hp`, `hp_max`, `stamina`, `done_events`, `here` and `period`, and sets `_mem_label` and `_mem_args`.
- `label mem_play`: `call expression _mem_label pass (*_mem_args)`, then `return`, which ends the replay.
- Replays run in their own store (`renpy/game.py:361`), so nothing reaches the save. Toasts are muted.

Helpers: `memory_groups(mode)` (`"person"` / `"act"`; Sana first), `memory_counts()` → `(seen, total)`.

### 3.10 Toasts and the objective: `game/ui_hud.rpy` (WP7)

- `ToastQueue` is a `builtins.object` subclass holding a `builtins.list` (D7). `toast_push(text, kind, who, amount)` appends an item `{text, kind, who, amount, t_shown}`.
- **Merge (D34).** If the newest queued item has the same `(kind, who)`, both have an `amount`, and the kind is `bond` or `aff`, add the amounts and rebuild the text ("Yuji  bond +4" / "Nobara  ♡ +3").
- WP7 sets `TOAST_SINK[0] = toast_push` and `config.notify = lambda m: toast(m)`. Every existing `renpy.notify` therefore queues.
- **Kinds** (kanji, colour):

  | kind | kanji | colour |
  |---|---|---|
  | `bond` | 縁 | the character's colour |
  | `bond_rank` | 縁 | the character's colour |
  | `aff` | 恋 | `gui.romance` |
  | `stat` | 術 | `gui.violet` |
  | `grade` | 級 | `gui.gold` |
  | `mission` | 任 | `gui.seal` |
  | `item` | 品 | `gui.gold` |
  | `thread` | 糸 | `gui.dim` |
  | `info` | 報 | `gui.dim` |

  WP0 changes `add_bond` / `add_aff` / `recruit` / `begin_together` to call `toast(...)` with the right kind, who and amount.
- `check_objective()`, called by the loop: if `objective_text() != last_objective`, show `objective_toast` for 4.5 s and store the new text. Because `last_objective` starts as None, it appears once after loading an old save. It is skipped in explore mode.

### 3.11 Store variables

**Unchanged in name and value:**
- clock and presence: `day`, `period`, `here`, `gojo_today`, `schedule_overrides`, `talked_today`, `spent_today`;
- stats: `stamina`, `stamina_max`, `ce`, `ce_max`, `control`, `output`, `insight`, `hp`, `hp_max`;
- combat and UI: `cb`, `quick_menu`, `quick_menu_before_combat`;
- relationships: `roster`, `bonds`, `affection`, `flags`, `together`, `threads`, `done_events`, `companion`;
- other: `explore_mode`, `mc_name`, `mc_surname`, `scene_light`, `tname` (orphaned).

**Same name, value converted:**
- `technique`: always `"timestop"`;
- `grade`: an int becomes a key or None;
- `arc`: 2 becomes 1 unless Arc Two was begun.

**New:**

| owner | variables |
|---|---|
| WP0 (`sb_hooks`) | `story_point`, `save_version`, `arc_start_day`, `actions_today`, `hide_side_images`, `smoke_autoplay`, `persistent.mc_face` |
| WP1 | `gojo_in`, `districts_visited` |
| WP2 | `merit`, `merit_granted`, `npc_state`, `promotions_log`, `pending_remarks` |
| WP3 | `mission_state`, `missions_done`, `mission_done_day`, `mission_retry_day`, `last_objective` |
| WP4 | `board_offers`, `board_week`, `board_log` |
| WP5 | `memories_seen`, `seen_acts` |
| WP6 | `inventory`, `items_granted`, `yen`, `equipped_tool`, `equipped_talismans`, `bound_specials` |

### 3.12 Save migrations

All migrations are in one ordered list. Each is idempotent and wrapped in try/except, and toasts are muted while they run. They run on every load, and from `ensure_state()` for new games and the sandbox. Ren'Py applies new `default`s before the callbacks, and `load_recover` does so explicitly (D1).

| order | owner | what it does |
|---|---|---|
| 5 | WP0 | `quick_menu = True` (D25). If `renpy.showing("mc")`, `renpy.hide("mc")` (a stale sprite in a mid-scene save). `tname` = the save's technique name from `TECHNIQUES` ("Last Light" for an unknown technique, and for every save once WP2 leaves only timestop). If `_partner` is missing and the old `partner` is set, `_partner = partner` (a save made inside the Sun Mall mission before d06486a renamed it). |
| 10 | WP2 | `technique` other than `"timestop"` → `"timestop"`. An Emberfall save also gets `control = max(control, output)`, so Last Light's tier doesn't drop. Sets flag `technique_was_<old>`. |
| 15 | WP1 | If `gojo_today` is missing any period, `roll_gojo()`. If `here` is not in `LOCATIONS` and `settled_in` is set, `here = "courtyard"`. |
| 20 | WP2 | `grade`: int 3 → `"g3"`; any other int → `"g4"` if flag `roll_call`, else `None`; a key stays. |
| 30 | WP2 | `refresh_vitals()`; if `hp <= 0`, `hp = hp_max`. |
| 40 | WP3 | If `settled_in` and `"ijichi"` is not in the roster, add him. If `utahime_arrived` and she's missing, add her. If `arc1_complete`, set flag `night_before_done`. |
| 50 | WP3 | If `arc != 1` and not `arc2_started`, `arc = 1`. |
| 60 | WP3 | For every mission now `done` whose merit is not in `merit_granted`, pay it quietly. If `sunmall_done`, pay `"ch5_recommendation"` (20). |
| 65 | WP3 + WP5 | Every done story row with no recorded done day gets `mission_done_day = 0` (no gap delays). If `settled_in`, mark the prologue sub-labels in `memories_seen` (day 0). |
| 70 | WP6 | `sync_keepsakes()`: keepsakes and mission items from flags. |
| 80 | WP4 | If `mission_board_open` (the old flag or the new scene) and there are no offers, generate them. |

`mission_board_open` doesn't need backfilling: it was set by the old `st_board_open`. `utahime_arrived` is never inferred, so every old save meets Utahime once, and her scene's text is timeless.

### 3.13 Load recovery (WP0)

```renpy
label load_recover:
    $ renpy.execute_default_statement(False)   # D1: load_failed() skipped this
    $ _in_replay = None
    $ run_migrations(block=True)
    scene black
    if has_flag("settled_in"):
        "(This save came from an older version of the game. Picking up on campus.)"
        jump sandbox
    "(This save came from an older version of the game. The prologue has been rewritten, so it picks up at the start of the scene.)"
    jump resume_story

label return_recover:
    $ run_migrations(block=True)
    if has_flag("settled_in"):
        jump sandbox
    jump resume_story

label resume_story:
    $ _plan = prologue_plan(story_point or legacy_story_point())
    while _plan:
        $ _next = _plan.pop(0)
        call expression _next
    jump sandbox
```

`legacy_story_point()` handles old saves, which have no `story_point`:

| flags | resume at |
|---|---|
| `settled_in` | (sandbox) |
| the old `partner` or `_partner` is set, or any of `read_wall`, `ignored_wall`, `scouted_corridor`, `saved_civilian`, `fought_first`, `climax_strong`, `climax_thin` (an old linear-build save that reached the Sun Mall; the current build plays it only after `settled_in`) | `arc_one_open` |
| `enrolled` | `ch2_first_years` |
| `chose_jujutsu` | `ch2_arrival` |
| any of `gojo_asked_why`, `gojo_asked_sana`, `gojo_asked_advice` | `chapter_one_b` |
| any of `reached_for_her`, `stood_in_front`, `listened_first`, `dinner_*` | `ch1_the_thing` |
| none of these | `ch1_diner` |

Mid-scene progress is lost; nothing else is. A resumed chapter may re-add a small bond gain from a choice replayed after the save point. That is accepted.

---

## 4. Screens

Everything is laid out at 1920×1080, using the palette and fonts from `gui.rpy` (`gui.ink`, `panel`, `paper`, `dim`, `mute`, `violet`, `gold`, `seal`, `romance`, `stamina`; `display_font`, `body_medium_font`), the frames `gui/panel*.png`, and the `seal`, `section`, `meter` and `chapter_card` screens. Every screen that can be on screen when a save is made keeps its name and return tuple.

### 4.1 HUD: `screen sb_hud(on_map=False, person=False)` (`ui_hud.rpy`, WP7)

It replaces today's 92px rail with its roughly 12 readouts.

- **Date chip** at (40, 26): a `panel_ghost` frame, padding (22, 8), with "Day 9 · Monday" in `display_font` 28 (the full weekday via `weekday_full()`). Explore mode shows "Explore · Morning".
- **Buttons** at the top right (`xalign 1.0`, `xoffset -40`, `ypos 26`, spacing 10), 148×52 `jjk_button`s:

  | button | action | when shown |
  |---|---|---|
  | MAP | `Return(("map",))` | place view only |
  | JOURNAL | `Return(("journal","people"))` | place view only (D33) |
  | MENU | `ShowMenu()` | always |

- **Keys:** `m` opens the map and `j` the journal (place view only).
- **Review tools** (developer only, D30): a small `jjk_label` button at the bottom left (40, 1040): "Review tools" → `Return(("dev",))`, place view only.
- **Gone:** period pips, energy, stamina, stats, technique, the STATUS and SAVE buttons, and the "TO KYOTO" countdown. Grade, energy and health live in the journal's Stats tab and in combat.

### 4.2 Toasts: `screen toasts` (in `config.overlay_screens`, zorder 150, WP7)

- The stack sits at the top right: right edge at 1880, the first toast at y 92, spacing 8. Up to 4 are visible at once, newest at the bottom; the rest wait, and none are dropped.
- Each toast is 460×56: a 6px bar in the kind's colour, a 36px kanji seal, and the text in `body_medium_font` 20.
- A toast lives 3.2 s once visible, with a 0.2 s slide in and fade out. A `timer 0.1 repeat True` expires them.
- Toasts are hidden during replays. The old `notify` screen stays only as a fallback.

### 4.3 Objective toast and arrival caption (WP7)

- **`screen objective_toast(text)`**: a 900px panel at the top centre, `ypos 96`, with a gold 2px hairline on top. It shows the kicker "NEXT" (`jjk_label`, gold) and the text in `display_font` 26. It slides down over 0.3 s, holds 4.5 s, then fades.
- **Arrival caption** (inside `sb_place`, D35), at the top left (40, 100): the place name in `display_font` 44, "· Evening" in `jjk_label` 20, and the place description in 20 `dim`, max 700 wide. It fades in over 0.3 s, holds 2.5 s and fades out over 0.5 s. It shows once per change of (day, period, here). That key is tracked outside the store, so the caption also shows after a load.

### 4.4 Place view: `screen sb_place()` (`sb_screens.rpy`, WP7)

- **Background:** `add graded_bg()`, then `Solid(gui.ink)` at alpha 0.10.
- **Stage** (x 0–1400):
  - Up to 4 of `who_is_here(here)`, with the companion first. Sprites are `lit` images `"<who> <expr>"`, where `(caption, expr) = ambient_of(who, here)`.
  - Zoom is `PLACE_STAGING.get(here, {}).get("zoom", 0.52)`, with `yalign 1.0` and `yoffset -40` plus the place's `y`.
  - Centres by count: 1 → 700; 2 → 470/930; 3 → 330/700/1070; 4 → 240/540/860/1160.
  - Each person is a `button` with hover brightness +0.08, returning `("char", who)`.
  - A **nameplate** is centred on the person at y 960: the name in `display_font` 26 in their colour, then the caption in italic 18 `dim` ("halfway through an enormous bowl"). A gold 「!」 badge shows when `missions_with(who, here)` is non-empty, and a gold NEW chip when `has_event("hangout", who, here)`.
  - Overflow: a "+N" chip at (1300, 900) with a textbutton for each extra name.
  - An empty place shows a ghost panel at the centre of the stage: "Nobody here right now. The map shows who's where."
- **Action card** at `xpos 1440`, `yalign 1.0`, `yoffset -40`, `xsize 440`, in a `panel_dark` frame:
  1. gold **mission** buttons from `missions_here(here)` → `("mission", mid)`;
  2. place actions from `place_actions(here)` → `("act", id)`. Buttons are 392×62: a title (`display_font` 22), a hint (16 `dim`) and one ◆ per period of cost;
  3. **Wait ◆** as a link-style button, always last;
  4. if a companion is along, "[name] is with me · let them go" → `("act", "release")`.

  A line "I'm running on empty. Eat or sleep." sits above the card when `stamina < 25`.
- **`place_actions(loc)`**, the built-ins:
  - dorm: sleep, study
  - training, ridge, forest, dojo: train
  - riverside: swim, train
  - cafeteria: eat
  - infirmary: rest ("Get patched up", once a day)
  - storehouse: tools (`sb_do_tools`, relabelled "Look through the racks", once a day, only while `armory_open` is not set)
  - courtyard: train ("Practice")
  - classroom: study
  - rooftop: think
  - everywhere: hold ("Hold the hour — Last Light", once a day, D26)
  - then `registered_place_actions(loc)`, then wait.

  There is no "missions", "temper" or Travel button. Explore mode shows only "Time: <next>" plus any registered `explore=True` actions.
- **Data** (WP7): `AMBIENT[(who, loc)] = (caption, expr)`:

  | who | place | caption | expression |
  |---|---|---|---|
  | yuji | cafeteria | halfway through an enormous bowl | happy |
  | yuji | courtyard | at the vending machine | neutral |
  | megumi | classroom | reading | serious |
  | megumi | forest / riverside | with a Divine Dog | neutral |
  | nobara | dorm_common | on her phone | neutral |
  | nobara | rooftop | leaning on the railing | neutral |
  | maki | training / dojo | drilling with a staff | serious |
  | panda | courtyard | sparring with Toge | happy |
  | toge | cafeteria | with onigiri | happy |
  | gojo | gojo_office | eating mochi in front of the TV | happy |
  | gojo | ridge | sitting just outside the veil | serious |
  | utahime | (any) | buried in paperwork | serious |
  | shoko | (any) | with coffee | neutral |
  | yaga | office | sewing a cursed doll | serious |
  | ijichi | gate | on the phone beside the car | neutral |

  Plus a fallback per person ("waiting for something", neutral). Also `PLACE_STAGING`, and `PERSON_GREET_EXPR` (the face they look up with): yuji happy, megumi neutral, nobara happy, maki serious, panda happy, toge happy, gojo happy, utahime serious, shoko neutral, yaga serious, ijichi surprised.
- Returns `("map",)`, `("journal", tab)`, `("char", who)`, `("act", id)`, `("mission", mid)` or `("dev",)`.

### 4.5 Person view: `screen sb_char(who)` (WP7)

It replaces the 18-row panel with its locked rows.

- **Background:** `graded_bg()` under an ink wash at alpha 0.35. Other people are not drawn.
- **The person** is `"<who> <PERSON_GREET_EXPR[who]>"` at `transform char_focus(x0)`. It eases over 0.35 s from their stage centre at zoom 0.52 to `xcenter 520`, zoom 0.66, `yalign 1.0`, `yoffset -20`.
- **Card** at `xpos 1000`, `ypos 150`, `xsize 820`, in a `jjk_panel`:
  - the name in `display_font` 46, in their colour;
  - the role line: CAST `year` · `grade_label(npc grade)` or the role ("First-year · Grade 2", "Doctor", "Off the scale");
  - BOND with the rank name and a 740×10 meter; for romanceable characters with affection > 0, the affection meter and its cap note;
  - the thread title in gold, with stage pips;
  - the ambient caption in italic.
- **Choices:** up to 4 buttons, 780×84, from `person_choices(who, here)` (section 6), each with a title (26), a hint (18 `dim`) and cost ◆. Missions are drawn in gold, romance with ♡.
- **Footer:**
  - the invite link "Ask them along" / "Let them go" (`("do","invite",who)`), when that activity is available;
  - one gold hint from `next_unlock(who)`: "Closer: Sit out with them — at Bond 50";
  - "Back" (Esc and right-click too) → `("cancel",)`.
- **HUD:** `use sb_hud(person=True)`, which shows the date and MENU only.
- Returns `("do", aid, who)`, `("mission", mid)`, `("act", id)` or `("cancel",)`.

### 4.6 Map: `screen sb_map(layer="campus")` (`ui_map.rpy`, WP1)

It replaces the 16 equal pins. `default view = layer`.

- **Header** at `ypos 108`, centred: `seal("図")`, "TOKYO JUJUTSU HIGH", and tabs **[校 Campus] [東京 Tokyo]** (`SetScreenVariable("view", …)`). The Tokyo tab reads "After Ijichi's ride-along" and is insensitive until `tokyo_open()`. The subline reads "Walking is free. Doing something takes time."
- **Campus layer:** `bg map_campus` under a wash at alpha 0.35. The six AREAS cards (width 340) are centred on their anchors:
  - The card header shows the seal, the area name (`display_font` 24) and a gold "◆ N" when N missions are waiting in the area.
  - Each place is a 320×44 row button (64 tall when it has markers), with the place name (20) on the left and, on the right, one of:
    - who is there now (short names in their colours, up to 3, then "+n"; a gold "!" after a name with a mission or new scene);
    - "YOU ARE HERE" in `violet2`;
    - the lock reason in `seal` red (hover shows the full `can_enter` text).
  - The second line shows `mission_markers()` for that place ("Yaga · The Sun Mall", "Board · 3 jobs", "Gojo is in").
  - Clicking a row returns `("go", loc)`. Your own place and locked places are insensitive.
- **Find someone strip** at (40, 1000): a 56×56 face chip for each rostered person. The chip is their side image, cropped by `FACE_BOX.get(who, (68, 0, 223, 223))` and scaled. Hover shows "Yuji — Cafeteria" or "Off campus". A click returns `("go", loc)` when you can enter that place.
- **Stay here** at the bottom right → `("cancel",)` (Esc too).
- **Tokyo layer:** `bg map_tokyo`, plus five district cards (360 wide) at shinjuku (500, 300), harajuku (520, 540), shibuya (560, 780), kawasaki (1120, 820) and yotsuka (1340, 440), and a "Jujutsu High — Ijichi's car" card at (1500, 220).
  - Each district card has the kanji (48), the name, one line, "what's there", a "½ day" chip, a lock chip (from `district_state`) and a "visited" tick.
  - An open district returns `("district", key)` when `trip_ok_now()`. Otherwise it is insensitive with "Ijichi drives from the gate, mornings to afternoons."
  - Footnote: "A trip takes half a day. District scenes come in a later build."
- **HUD:** `use sb_hud(on_map=True)`, showing the date and MENU.
- Returns `("go", loc)`, `("district", key)` or `("cancel",)`.

### 4.7 Journal: `screen journal(tab="people")` (`ui_journal.rpy`, WP8)

`tag menu`. It has its own full-screen chrome, not `game_menu`.

- `default sel = None`, `default mfilter = "available"`, `default msub = "story"`, `default mem_mode = "person"`, `default inv_cat = "all"`.
- `editable = not renpy.context()._menu`, which is true when it was opened from campus (D4).

**Chrome.**
- A left rail from x 0 to 320 on `gui.panel`: `seal("記")` and "Journal", then six 260×72 tab buttons, each with a kanji seal, a label and an optional count badge: 人 People · 任 Missions · 憶 Memories · 力 Stats · 装 Equipment · 品 Inventory. **Return** is at the bottom (Esc and right-click too) → `Return()`.
- The content area runs from x 360 to 1880 and y 40 to 1040. At the top, a gold strip "◆ NEXT  <objective_text()>", 1520 wide.

**People.**
- A grid of 4 columns of 362×330 cards in `JOURNAL_CAST` order.
- A met card shows the side portrait (`images/side/<who>_neutral.png`, 360×223, at zoom 0.9), the name, a grade chip ("Off the scale" for Gojo, the role for the ungraded), the bond rank and meter (plus the heart meter for Nobara, Maki and Shoko), and "Next: <next_for> — <where>" in gold, on up to two lines.
- An **unmet** card shows a black silhouette: the neutral sprite through `TintMatrix("#000000")` at alpha 0.85. Characters without art get a panel with a large 「？」. The card also shows the hint.
- **Sana** shows her portrait, "In memory" and "Memories: n of m", and links to Memories filtered to her.
- Clicking a met card sets `sel`, which opens the **detail pane**:
  - on the left, the raw sprite file at zoom 0.5, unlit;
  - on the right:
    - the blurb and the grade;
    - bars for reserve (a 0–300 scale), control and output (0–100). Special grades run past the frame with "∞", and Maki's reserve reads "Heavenly Restriction";
    - "Promoted to Grade 2 on Day 14" lines;
    - bond and affection, with the affection-cap note;
    - the thread title and every stage learned so far;
    - their character missions (done ✓ / available with where / locked with `mission_reason` / "Written in a later build");
    - `usual_places(who)`; for Gojo on an in-day, "In his office today";
    - "Memories with them (n)" → the Memories tab.
  - Back closes the pane.

**Missions.**
- Sub-tabs **Story / Character / Board**, and filters **Available / Active / Done / All**.
- **Story:** collapsible act headers, e.g. "Act I · Grade Four — 3 of 5", with the grade band.
  - Rows are 1480×72: a status icon (✓ done · ◆ available (gold) · ● active · ◌ waiting · — locked · a dim "Coming in a later build" for unwritten), the title, then the objective with where and when (available or waiting), the reason (locked), and the merit reward.
  - Rows in a `group` show "The Surveyor 2/3".
  - A **promotion box** shows `merit_progress()` as a bar with `next_grade_text()`.
  - When `main_story_complete()` and `editable`, a card reads "Begin Arc Two" → `Return(("arc_two",))`. The exact warning line is in `arc_two_start`.
- **Character:** one group per met person, with rows as above.
- **Board:** "At Utahime's office", this week's offers (read-only), taken cards, the last 10 jobs (day, grade, partner, outcome, merit), and "Misgraded jobs found: N" once N ≥ 1.

**Memories.**
- A **By person / By act** toggle. Each group is a row of 280×158 tiles: the memory's `bg` as a thumbnail, with its title.
- A seen tile's `action` is `memory_replay(m)`. An unseen tile is dark with 「？」 and its hint.
- Counter: "14 of 52 found". Sana's group comes first in By person.

**Stats.**
- **Left** (x 360–860): `kaito_card_image()`, the raw file `images/char/mcyotsuka_neutral.png` until `settled_in` and `images/char/mc_neutral.png` after, at zoom about 0.62, unlit.
- **Right** (x 900–1880):
  - "[mc_surname] [mc_name]";
  - "First-year · Grade 4", or "Not yet assessed";
  - the promotion panel: a merit bar and `next_grade_text()`;
  - 620px bars with cap markers: Health (`hp`/`hp_max`), Cursed energy (`ce`/`ce_max`, marker at the reserve cap), Control and Output (marker at the stat cap), Insight (no cap), and Stamina;
  - a **Last Light** panel: 残光 · Zankō, the tier name and description, the next tier ("at Control 60 — needs Grade 2" when the cap is lower than the requirement), the Hold verb ("once a day"), and the moves with their costs;
  - a **"Your year"** strip: Kaito, Yuji, Megumi and Nobara on one reserve scale (0–300), with Gojo's bar running off the edge, labelled ∞.

**Equipment.**
- The tool card ("In my hand: Bare hands" or the tool), with a **Change** button.
- Four talisman slot cards. The first `talisman_slots()` are filled or empty. The rest read "Opens at Grade 3", "Opens at Grade 2" or "Opens at Semi-Grade 1".
- Clicking an open slot shows a modal picker: owned items of that kind, wearable ones selectable, others greyed with their `can_wear` reason, plus **Unequip**.
- Each item shows its effect text, marked "Takes effect in combat from the combat update".
- When not `editable`: "Change equipment on campus — open the journal from the place view."

**Inventory.**
- "¥ 12,000" at the top right.
- Category chips with counts: All · Keepsakes · Sealing talismans · Supplies · Mission items · Talismans · Cursed tools.
- 280×160 tiles (name, count, grade chip). The selected tile shows a panel with its description, source and effect.

**Wrappers.** `screen jjk_status(): use journal("stats")` and `screen jjk_journal(): use journal("people")` stay. Both are `tag menu`.

### 4.8 Board screens (`sb_board.rpy`, WP4)

- **`board_screen`**: the host's office background, the host's sprite (serious) at `xcenter 300`, and three job cards 400×620 at x 620 / 1060 / 1500. Each card shows:
  - a big grade chip, the title, the case, the place and the twist line;
  - the rewards: merit, a yen range and "may drop" items;
  - a "Needs a senior partner" tag;
  - **Take**, or the reason it can't be taken ("Evenings: Utahime doesn't send anyone out after dark", "Too tired — 25 stamina").

  Taken cards are small, read-only and grey. The footer reads "Offers change on Mondays." A Close button returns.
- **`board_partner(offer)`**: cards for eligible partners (side portrait, name, grade chip, bond, a "senior" chip), with ineligible people listed dimly and their reasons; Cancel.
- Both are `tag sandbox`, called from the `sb_do_board` label.

### 4.9 Armory (`sb_items.rpy`, WP6)

`screen armory`, over the storehouse background: one row per tool with a grade chip, the description, and one of Take / Return / Owned / "Sealed until Grade 3" / "Story reward" / "Sealed — Arc Two". Close. `tag sandbox`.

### 4.10 Grade card (`sb_grades.rpy`, WP2)

A card at the centre, 900×420, `jjk_panel`:
- `seal("級")` in `gui.seal`;
- the kicker (ASSESSED / PROMOTED);
- "[mc_surname] [mc_name]";
- the grade name in `display_font` 64;
- one line of what it opens: "Board: Grade 3 jobs · Reserve up to 140 · 2 talisman slots".

### 4.11 Engine screens: `screens.rpy` (WP8)

- **Say screen:**
  ```renpy
  if not renpy.variant("small") and not hide_side_images:
      if persistent.mc_face or renpy.get_say_image_tag() != "mc":
          add SideImage() xpos 6 yalign 1.0 zoom 0.8
  ```
  At 288×178, the image stays inside the 300px dialogue margin, so it never overlaps the text.
- **Preferences:** a new `radio` vbox, "[mc_name]'s portrait", with Show / Hide (`SetField(persistent, "mc_face", True/False)`).
- **Quick menu** (D25), both variants:
  - `if quick_menu and not renpy.get_screen(("sandbox", "menu")):` — the list form works (`renpy/display/screen.py:1128`). WP0 already made this change in both variants (migration 5 turns the quick menu on for every load, so it had to hide over the sandbox straight away); WP8 keeps the line as it is.
  - Default variant: BACK · HISTORY · SKIP · AUTO · SAVE · JOURNAL (`ShowMenu("journal")`) · MENU (`ShowMenu()`).
  - Touch variant: BACK · SKIP · AUTO · JOURNAL · MENU.
- **Navigation:** Status and Journal merge into one "Journal" entry → `ShowMenu("journal")`.

### 4.12 Combat screen (WP2)

Unchanged, except for the enemy grade line (`grade_label`) and the `smoke_autoplay` timer.

### 4.13 Review tools: `screen dev_panel` / `label dev_tools` (`explore.rpy`, WP11)

Developer builds only, reached from `("dev",)` in the place view. It runs in the main context. Buttons (each a `Function` followed by a toast):
- +50 merit
- promote me one grade
- promote Yuji / Megumi / Nobara one grade
- finish the next story step
- +20 bond with everyone
- open Tokyo (`ijichi_rides`)
- Gojo in today
- recruit Utahime (plays her scene)
- grant one of every item
- set `armory_open`
- mark the main story complete (`dev_story_complete`)
- jump to day +7
- Close

---

## 5. Story changes

### 5.1 Staging and voice

The rules are in 2.3. Kaito is off screen everywhere. The 41 `show mc` / `hide mc` lines are deleted:

| file | lines |
|---|---|
| **Prologue (WP9):** ch1_alley | 19 |
| ch1b_the_offer | 11 |
| ch2_tour | 28 |
| script | 63, 75 |
| **Later chapters (WP10):** events_arc1 | 58, 151, 243, 320, 475, 529, 585, 635, 690, 745, 809, 876, 933, 988, 1095, 1158, 1227, 1290, 1356, 1410, 1470, 1532, 1588, 1654 |
| ch4_mission | 45, 87, 102, 365 |
| missions_arc1 | 44, 115, 175 |
| story_arc1 | 255, 321 |
| ch5_debrief | 78, 146 |
| events_romance | 12 |

How the others are re-staged:

| where | before | after |
|---|---|---|
| hangouts (events_arc1) | the lone person at `pos_cr` | `pos_c` |
| ch4:42–45 and 362–365 | `pos_l` / `pos_cl` / `pos_cr` + mc | `pos_l` / `pos_c` / `pos_r` |
| ch4:97–101 | partner at `pos_cr` | `pos_c` |
| ch5:77 | gojo at `pos_cr` | `pos_c` |
| ch5:146–147 | `show mc at pos_c` and its `with dissolve` | both lines deleted |
| missions_arc1:43 | `show expression _p at pos_cr` | `pos_c` |
| missions_arc1:115–116 | `show mc` and its `with dissolve` | both deleted |
| missions_arc1:174 | nade at `pos_cr` | `pos_c` |
| story_arc1:254, 320 | gojo / maki at `pos_cr` | `pos_c` |
| events_romance:11 | `pos_cr` | `pos_c` |
| ch1:18 | sana at `pos_cr` | `pos_c` |
| ch1b:10 | gojo at `pos_cr` | `pos_c` |
| ch2:27 | gojo at `pos_cr` | `pos_c` |
| script:63, 75 | mc lines | deleted |

**People stay on screen during activities.** `label stage_person(who, expr=None)` (WP7, `sb_activities.rpy`) runs `scene expression graded_bg()`, then `$ renpy.show(who + " " + (expr or PERSON_GREET_EXPR[who]), at_list=[pos_c])`, then `with Dissolve(0.3)`. `sb_activity` calls it before Talk and before every `act_*` (not before "hang", because hangouts stage themselves). WP10 removes the scene resets inside the act labels:
- `events_activities.rpy:80` (`act_eat`): delete the `scene` line.
- `:103` (`act_swim`): after `scene bg riverside`, add `show expression who at pos_c`.
- `events_stand.rpy:11`: delete the `scene` line.
- `events_intimate.rpy:11` and `:48`: delete the `scene` lines.
- `:86` (`act_int_day`): after `scene bg riverside`, add `show expression who at pos_c`.
- `events_romance.rpy:49`: after `scene bg gate`, add `show expression who at pos_c`.

### 5.2 The prologue (WP9)

`label start` in `script.rpy` is unchanged (2.1). Every step label begins `$ story_point = "<its name>"`.

#### `ch1_alley.rpy` — The Lights

**Structure.** `chapter_one` keeps the chapter card, then calls `ch1_diner`, `ch1_the_thing` and `ch1_gojo`, and returns.

**`ch1_diner`** (the diner and the street, converted to "I"):
- Sana at `pos_c`, happy for the ranking; she points at the "bad ceiling" (a serious beat).
- It ends at "I cut through the alley behind the arcade because it saves four minutes and because I always do."

**`ch1_the_thing`** (the alley, in order):
1. `scene bg alley` with `Dissolve(1.0)`, then "Then the lights go out.", then `$ hide_side_images = True` and `scene bg black`.
2. **Sana tells the thing.** New lines go after "…that's a power cut, right?" and "I'm going to tell you the thing now, actually. This feels like a doorstep.". Written by WP9; these beats are required:
   - `sana serious "Okay. The thing."` She has been seeing things, not people, for about six weeks.
   - The one on the diner ceiling tonight: she pointed at it, and I looked right at it.
   - One stands on the platform every morning by the third pillar, and everyone walks through where it is.
   - She has been drawing them in the back of her maths book, so she'd know she isn't making it up: "if I was, I'd draw them different every time, and I don't."
   - Kaito: `mc "Is this a bit? This feels like a bit."`
   - `sana "There's one at the end of this alley."` It has been standing there since they turned in, and she didn't say in case saying it made it—
   - Set `flag("sana_told_the_thing")` and `flag("sana_sketchbook")` (the Act V seed).
3. The existing menu "Sana. Take my arm." / "Get behind me." / "Say nothing. Listen." stays, with the same flags and gains. Its prompt becomes "I cannot see my own hands."
4. "Something hits us both." Her death beats stay, converted.
5. **Contradictions rewritten:**
   - `mcthink "She never told me the thing."` → `mcthink "She told me. Thirty seconds ago she told me, and I asked if it was a bit."`
   - "You have never been able to see it, and neither could she…" → "I have never been able to see it. She could. For weeks she could, on her own, drawing them in the back of a maths book so she'd know she wasn't mad, and I asked if it was a bit. That, {i}that{/i}, is the thing my chest does not survive."
   - `mcthink "It was there while she was talking about the man at the next table."` → `mcthink "It was there while she was telling me about it."`
   - Optional added curse line: `curse2 "She could see me too. She kept looking right at me."`
6. The sight opens: `$ hide_side_images = False`, then `scene bg alley dark with flash_purple`, then `show curse big at pos_loom, pulse_in`.
7. **Last Light wakes.** The technique menu (lines 194–218) goes; there is no choice. Using the old Stillness text, in "I":
   > It is going to take me in about a second and a half. I can feel the shape of what is inside me, and I know exactly what I want it to be. / I do not want to be faster. I do not want to be stronger. I want the second to {b}stop{/b}: the one where she was talking, the one where the lights went, the one that is arriving now. / And it does.
   - `show layer master at last_light_still`, where `last_light_still` is defined in this file: `matrixcolor SaturationMatrix(0.08)`.
   - Then: the alley holds, colour goes out of it, dust hangs as if pinned, and the thing is still mid-reach, four feet away. **One light stays on: the lamp over the fire door, warm, the only warm thing left.** "I have one second. I am standing inside it…"
   - `show layer master` (restore). Set `$ technique = "timestop"` and `flag("last_light_woke")`. The Filament and Emberfall branches and `$ tname` are deleted.
8. `call combat("alley_curse", None, False, "bg alley dark")`. It ends "down" after four rounds (WP2). "I do not win." follows, converted.

**`ch1_gojo`:**
- `scene bg alley with flash_white`, then `show gojo serious at pos_c, pulse_in`. Converted to "I". Gojo gets expressions (serious, sad at Sana).
- The name input is wrapped: `if not (_in_replay or smoke_autoplay):`. The existing input code goes inside; otherwise the defaults stay.

#### `ch1b_the_offer.rpy` — The Offer

- `scene bg alley`, with Gojo alone at `pos_c`. Everything is converted to "I".
- **Gojo names it first:**
  > `gojo serious "Before anything else. The thing you did in there."` / `gojo "You held the second the lights went out. Stopped it, and stood in it."` / `gojo @ happy "Zankō. Last Light. Somebody has to put something on the form."`

  Then `flag("named_last_light")`.
- The home, breakfast, packing and car scenes are converted; the parents are at `pos_cl` / `pos_r`. The keepsake flags are unchanged (D24).
- `ch1b_the_other_road`: before `renpy.full_restart()`, add `if _in_replay:` / `$ renpy.end_replay()`.

#### `ch2_tour.rpy` — The Strongest of Today

**Structure.** `chapter_two` keeps its card, then calls `ch2_arrival`, `ch2_the_veil`, `ch2_yaga` and `ch2_first_years`.
- **`ch2_arrival`**: the car and Ijichi (surprised, then sad), the gate with Gojo at `pos_c`, and the courtyard tour. The tour line becomes: `gojo "Storehouse is Yaga's, the ridge is for running up — the lower half — and the riverside is freezing and everyone swims in it anyway."` The three questions stay as they are.
- **`ch2_the_veil`** replaces lines 75–139 (the building, the storehouse and the casket):
  - "Then, near the top of the grounds, he stops walking and looks up." The "strongest of today" exchange stays.
  - `scene bg ridge_veil with fade_curse`. High on the ridge the air is wrong: a dome, dark and faintly violet. Inside it, if I let my eyes do the new thing they do, a figure sits cross-legged, like someone meditating. It is dry, brown and very still, and the hands in its lap are missing their fingers.
  - `gojo "That's the strongest in history."` The title and filing-category lines are kept. `mcthink "Has. Present tense."`
  - Menu prompt: "The veil ripples very slightly. There is no wind up there." The choices and flags are unchanged (`asked_dead`, `asked_why_here`, `watched_the_box`):
    - dead → "He's a corpse. That's not the same thing, and the difference is the entire reason this school keeps a veil up there day and night." / "Nine people take turns holding it…"
    - why here → "Because I'm here…" (unchanged)
    - say nothing → "…It is facing the school." / `gojo "...Yeah. It does that."`
  - It ends: `gojo serious "Don't go near it. Not the ridge path past the rope markers. Not on a dare, not on your own. That's not a rule, the rules are Yaga's. That's me asking."`
  - `flag("saw_the_ridge_veil")` replaces `saw_the_casket`, which nothing reads.
- **`ch2_yaga`**: the interview. Only the voice changes; Yaga gets serious expressions.
- **`ch2_first_years`**: the meeting, with Gojo at `pos_fl` until he leaves and then the three at `pos_l` / `pos_c` / `pos_r`. Then the first night, converted.

#### `script.rpy` — `arc_one_open`

- The mc lines are removed, and the scene is converted ("My room: a bed, a desk, and a window that faces a mountain that is also, somehow, Tokyo.").
- Line 77 becomes "Nobody has given me a deadline. The campus is open, the clock runs whether I use it or not, and the three of them have somewhere they'll be."
- After `flag("settled_in")`, add `$ arc_start_day = day` and `$ ensure_state()`.
- Set `$ story_point = "arc_one_open"` at the top.

### 5.3 New scenes

All new scenes are first person, use expressions, and are marked as placeholders.

| label | file (WP) | trigger | content |
|---|---|---|---|
| `st_utahime_office` | missions_stubs (WP3) | `ev(kind="story", periods=M/N/A, priority=96)` | 15–25 lines, `scene bg utahime_office`. A new nameplate next to Yaga's door. Utahime (serious, then annoyed at the mention of Gojo) came ahead of the Goodwill Event to prepare it, and she's helping Gojo with something she won't explain. **Board rules:** jobs at my grade; one grade up with a senior partner; always take someone. She gives a Paper Ward she wrote herself and two sealing talismans. The items are granted by the mission's `rewards` when it completes, not in the scene. `recruit("utahime")`, `flag("utahime_arrived")`, `flag("mission_board_open")`. The text is **timeless**, because old saves may meet her late. |
| `st_promotion_g3` | missions_stubs (WP3) | start: Maki at training/dojo | Maki (serious) watches; Utahime has sent the paperwork. `call combat("promo_g3", None, True, "bg training")`. On `"win"`: Maki's verdict (happy), `promote("mc","g3","Promotion assessment")`, `call show_grade_card("g3")`. On `"down"` or `"fled"`: Maki's "Again. Tomorrow." and `mission_fail("m_promo_g3")`. |
| `cm_ijichi_1` Ride-Along | missions_stubs (WP3) | start: Ijichi at the gate, M/N/A, cost 2 | A day in his passenger seat, three sites and a veil raised on a street corner. He offers to drive me into the city on free days. `flag("ijichi_rides")`. |
| `cm_maki_1` The Armory | missions_stubs (WP3) | start: Maki, bond 10, `met_second_years` | Maki unlocks the racks; grade decides what they release. She gives the Slaughter Demon (`give_item`). `flag("armory_open")`. |
| `arc_two_start` | sb_missions (WP3) | the journal | See 3.6.3. |
| `act_lesson` (+ activity `lesson`) | sb_activities (WP7) | Gojo at `gojo_office` on an in-day, once a day | Three first-person variants. `gain("control", 5)`, `raise_reserve(5)`, 1 period. |
| `sb_trip`, the district lines | sb_tokyo (WP1) | the map | 3.3. |
| `sb_do_veil` | sb_world (WP1) | ridge | 3.2. |
| board narration | sb_board (WP4) | the board | 3.7. |
| sandbox narration | sb_loop (WP7), sb_events (WP3) | — | Converted to "I" (D9): "I let the time pass.", "She puts me on the floor eleven times…", "[_n] is busy with something. I leave it." |

`SMALLTALK` gains 4 lines each for `utahime` and `ijichi`. `PROMO_LINES[who]` is one line per student, spoken instead of small talk when `pop_remark(who)` is true. For example, nobara: "Grade 2. Don't make a face, you'll catch up. Probably."

### 5.4 Later chapters (WP10): compatibility edits only

Narration stays "you", except `st_roll_call` (D9).

#### 5.4.1 One technique

- **events_arc1 `ev_megumi_1`, lines 180–189:** keep only the timestop text, unconditionally, with the `if` line removed and the body dedented.
- **missions_arc1:**
  - lines 49–52: the timestop block becomes unconditional;
  - lines 128–136: delete the Filament branch; the timestop branch becomes unconditional.
- **ch4_mission:**
  - delete `$ tname = ...` (line 21);
  - choice 145 becomes `"Hold the corridor with Last Light."`;
  - each three-way branch collapses into one Last Light passage (the old `else` text was leftover "Aftersound" replay text):
    - **148–158, the corridor:** "You hold the second and walk into it." / "The service corridor waits, pinned: dust stopped in the security light, a drip halfway to the floor. You walk forty metres of it inside a moment that isn't passing." / "The residue doesn't thin as you go. It pools, deeper at every step, and at the far end something is breathing in four-four time, caught mid-breath like everything else."
    - **244–252, the rescue:** "You stop the atrium." / "The thing hangs off the escalator well with one limb reaching, and for one held second nothing in this building can move except you." / "You take her over the rail and down the far staircase, the one it would have had to turn around to see, and when the second lets go you are both already on the ground floor."
    - **283–288, fight first:** "It swings, and you stop the second on the swing." / "Its shoulder is already dropping, the way it has dropped every time. You put everything you have into the space where it is about to be, and let the second go."
    - **343–352, the climax:** "The second stops." / "The whole atrium holds, the dust, the faces, the thing with all of them pointing at you, and you walk into the space it is about to be, and you are already there when the world starts again."
  - ch4:212: `add_bond("maki", 4)` → `if "maki" in roster:` / `$ add_bond("maki", 4)`.

#### 5.4.2 No deadline (D8)

| file:line | now | becomes |
|---|---|---|
| story_arc1 43–57 and choice 62 (roll call) | Kyoto in three weeks; "Then I've got three weeks." | See 5.4.3. |
| story_arc1:82 | "Wrong week for it" | "Wrong day for it" |
| story_arc1:88 | "from Thursday there'll be work on the board" | "Two: Kyoto's teacher arrives tomorrow to prepare the Goodwill Event, and she has agreed to run the board while she is here. Low grade. Real." |
| story_arc1:86 | "Cursed tools. Take what you can name." | "Look, don't take. Nothing on those racks leaves without a grade and a reason." (D10) |
| story_arc1:264 | "You've been on campus a fortnight. You've got…" | "You've got a technique you didn't ask for and a body that hasn't caught up to it." |
| story_arc1:266 | "And in a week you're going to stand on a field…" | "And one of these days you're going to stand on a field opposite people who have had this their whole lives." |
| story_arc1:285, 296 | `$ ce_max = min(160, ce_max + 20)` / `+ 12` | `$ raise_reserve(20)` / `$ raise_reserve(12)` |
| story_arc1:324 | "…on a Thursday, and Maki…" | "…one noon, and Maki…" |
| story_arc1:339 | menu prompt "Four days." | "Not long now." |
| story_arc1:349 | "…four days out." | "…this close to it." |
| story_arc1:364 | "You could build four days around it." | "You could build the rest of the time around it." |
| story_arc1:418 | "Three weeks ago I'd have said…" | "When I got here I'd have said…" |
| story_arc1:423 | "I've been here three weeks and I've spent almost all of it alone…" | "I've spent almost all of my time here alone…" |
| story_arc1:445–446 | `$ arc = 2` and `$ flag("arc1_complete")` | `$ flag("night_before_done")` |
| story_arc1:450 | the card "END OF ARC ONE" / "Three Weeks" | `chapter_card("THE NIGHT BEFORE", "Goodwill", "The Kyoto Goodwill Event — coming in a later build.")` |
| story_arc1:467 | "…all week." | "…since you arrived." |
| story_arc1:494 | "You've been here all week." | "You've been here the whole time." |
| story_arc1:497 | "for the first four days" | "for the first few days" |
| events_arc1:1574 | "…three weeks from being sent somewhere." | "…a good deal less than that from being sent somewhere." |
| ch5_debrief:38 | "A fortnight ago you did not know…" | "Not long ago you did not know…" |
| ch5_debrief:163–172 | `days_left` block | WP0: `mcthink "Nobody has given me a date for anything."` / `mcthink "So I get to choose what the days are for."` |

The `ev()` registrations lose `min_day` in `story_arc1` (lines 10–25), `story_kurose` (10–13), `story_oda` (12–15), `missions_arc1` (9–14) and `events_arc1` (47). The `st_board_open` (14–15) and `ev_patrol` (49–50) registrations are deleted; their labels stay.

Kept because they are not deadlines: `ch5:135` ("an exchange event with Kyoto coming up"), missions_arc1:108 ("Three weeks" of Nade's silence), the Oda letters' durations, and "the night before Kyoto".

#### 5.4.3 Grades in later chapters

**`st_roll_call`** is converted to "I" and reworked. The target shape:
- Yaga on grades: "Every sorcerer in this country has a grade. It decides what you are sent to, and who is sent with you."
- A short Goodwill mention with no date: "Every year Kyoto sends their students here for the Goodwill Event…" The Nobara "job interview with sticks" joke stays.
- "When it comes, you will not be ready."
- `yaga "[mc_surname]. Last week you didn't know cursed energy existed. Today you get a number."`
- `$ promote("mc", "g4", "Assessed at roll call", quiet=True)`, then `call show_grade_card("g4", "ASSESSED")`.
- `yaga "Grade 4. Everyone starts somewhere. Most people start here."` Then: "Fushiguro is Grade 2. Kugisaki, Grade 3. Itadori is Grade 4 on paper, for reasons above both of us."
- The menu keeps its three flags and gains; the first choice becomes `"\"Then I'd better start now.\""` with Yaga's replies adjusted ("You had better." … "You heard it as a starting line.").
- Lines 86 and 88 as in the table above.

**`ch5_debrief` 49–60.** Replace the grade if/else with:
- `yaga "I am putting your name forward for Grade 3."`
- `yaga "That is not a promotion. It is a recommendation, and it is worth exactly what you do with it. Earn it on Iori's board, and then in front of a witness."`
- Keep the existing Maki-conditional line.
- `$ add_merit(20, "The Sun Mall")` and `$ flag("recommended_g3")`. `$ grade = …` goes.
- Old saves are covered by migration 60.

---

## 6. Contracts (frozen by WP0)

WP0 writes every one of these with its final signature, a docstring naming the owner, and the stub behaviour shown. Packages code against these and nothing else.

| symbol | owner | WP0 stub returns / does |
|---|---|---|
| `toast(text, kind="info", who=None, amount=None)` | WP0 (final) | final (3.1) |
| `register_*`, `run_migrations`, `ensure_state`, `registered_place_actions`, `prologue_plan`, `legacy_story_point` | WP0 (final) | final |
| `area_of(loc)`, `places_in(area)`, `usual_places(who)`, `when_at(who, loc)`, `gojo_in_today()`, `AREAS` | WP1 | `None` / `[]` / `""` / `""` / `False` / `[]` |
| `tokyo_open()`, `district_state(k)`, `trip_ok_now()`, `car_action_ok()`, `DISTRICTS`, `DISTRICT_ORDER`; labels `sb_trip(key)`, `sb_do_car` | WP1 | `False`, `(False,"Later")`, `False`, `False`, `{}`, `[]`; labels `return` |
| `grade_key`, `grade_rank`, `grade_label`, `player_grade`, `grade_cap(kind)`, `talisman_slots(key=None)`, `merit_needed(key=None)`, `merit_progress()`, `next_grade_text()` | WP2 | working simple versions (grade_label accepts int or key or None) |
| `add_merit(n, why="")`, `promote(who, key, why="", quiet=False)`, `recent_promotion(who, days=3)`, `pop_remark(who)`, `npc_stats(who)`, `train_together(who, n=3, stat=None)`, `sorcerer_power(who)`, `pick_team(n, min_key=None)`, `raise_reserve(n)` | WP2 | add to merit / set grade / `False` / `False` / base dict / no-op / 10 / `[]` / raise uncapped |
| screen `grade_card(key, kicker)`, label `show_grade_card(key, kicker="PROMOTED")` | WP2 | text-only card / `return` |
| `mission_status(id)`, `mission_reason(id)`, `missions_list(...)`, `missions_here(loc)`, `missions_with(who, loc=None)`, `mission_markers()`, `next_for(who)`, `current_objective()`, `objective_text()`, `act_done(a)`, `acts_done()`, `act_progress(a)`, `main_story_complete()`, `mission_fail(id)`, `complete_mission(id)`, `begin_arc_two()`, `JOURNAL_CAST`, `ACTS`; labels `start_mission(mid)`, `arc_two_start` | WP3 | `"locked"`, `""`, `[]`, `[]`, `[]`, `{}`, `None`, `None`, `""`, `False`, `0`, `(0,0,0)`, `False`, no-op, no-op, no-op, basic list, `[]`; labels `return` |
| `board_open()`, `board_host()`, `board_summary()`, `misgrade_count()`; label `sb_do_board`; screens `board_screen`, `board_partner(offer)` | WP4 | `False`, `("utahime","utahime_office")`, `{}`, `0`; `return`; empty screens |
| `MEMORIES`, `memory_groups(mode)`, `memory_counts()`, `memory_replay(mem)`, `record_act(aid, who)`; label `mem_play` | WP5 | `[]`, `[]`, `(0,0)`, `NullAction()`, no-op; `return` |
| `ITEMS`, `give_item`, `take_item`, `has_item`, `item_count`, `items_in(kind)`, `can_wear(id)`, `equip_talisman`, `unequip_talisman`, `equip_tool`, `armory_open_now()`, `armory_tools()`, `add_yen(n)`, `sync_keepsakes()`; label `sb_do_armory`; screen `armory` | WP6 | `{}`, working counters on `inventory`, `(False,"Later")`, no-ops, `False`, `[]`, add to yen, no-op; `return`; empty screen |
| screens `sb_hud(on_map=False, person=False)`, `toasts`, `objective_toast(text)`; `toast_push(...)`, `check_objective()` | WP7 | moved HUD without countdown; no-op; no-op |
| screens `sb_place()`, `sb_char(who)`; `place_actions(loc)`, `ambient_of(who, loc)`; label `stage_person(who, expr=None)` | WP7 | current screens; current function plus registered actions; `("", "neutral")`; `return` |
| `person_choices(who, loc=None)` → `[dict(kind="do"|"mission"|"act", id, label, hint, cost, gold=False, romance=False)]` | WP7 | `[]` |
| screen `sb_map(layer="campus")` | WP1 | the current map, moved, without the Filament line |
| screens `journal(tab="people")`, `jjk_status()`, `jjk_journal()`; `kaito_card_image()` | WP8 | `journal` shows the old Status/Journal by tab |
| label `dev_tools` | WP11 | `return` |

**`person_choices` ranking** (WP7). Fill up to 3, then add Talk as the last choice:
1. the first `missions_with(who, here)` (gold, `kind="mission"`);
2. the person-specific action: `board` (Utahime at her office and `board_open()`), `lesson` (Gojo, office, in-day, not yet today), `car` (Ijichi at the gate, `car_action_ok()`);
3. a milestone: `rom_say` > `stand` > `confide`;
4. `hang` ("Spend time together"), when `has_event("hangout", who, here)`;
5. one romance or intimate activity, in the order `int_*` > `rom_close` > `rom_town`;
6. the one activity that fits the place: eat (cafeteria) / train (training, dojo, ridge, forest) / swim (riverside) / stargaze (rooftop, ridge, riverside at night) / study (classroom, dorm_common, dorm) / walk;
7. `talk`.

Only available activities appear (`activity_state` ok). `invite` is the footer link.

---

## 7. Work packages

```
Wave 0 (sequential)   WP0  scaffold, contracts, tooling, backup
Wave 1 (parallel)     WP1 world/map/Tokyo · WP2 grades/Last Light/combat · WP3 missions/stubs/events
                      WP4 board · WP5 memories · WP6 items · WP7 HUD/place/person/loop
                      WP8 journal/engine screens · WP9 prologue · WP10 later chapters
Wave 2 (sequential)   WP11 integration, review tools, save regression, docs
```

**File ownership in wave 1** (disjoint; after WP0 every file has exactly one owner):

| package | owns |
|---|---|
| WP1 | `game/sb_world.rpy`, `game/sb_tokyo.rpy`, `game/ui_map.rpy`, `game/lighting.rpy`, `game/bg_placeholders.rpy`, `tools/smoke/wp1_world.rpy` |
| WP2 | `game/sb_grades.rpy`, `game/sb_energy.rpy`, `game/sb_combat.rpy`, `tools/smoke/wp2_grades.rpy` |
| WP3 | `game/sb_missions.rpy`, `game/missions_stubs.rpy` (new), `game/sb_events.rpy`, `tools/smoke/wp3_missions.rpy` |
| WP4 | `game/sb_board.rpy`, `tools/smoke/wp4_board.rpy` |
| WP5 | `game/sb_memories.rpy`, `tools/smoke/wp5_memories.rpy` |
| WP6 | `game/sb_items.rpy`, `tools/smoke/wp6_items.rpy` |
| WP7 | `game/ui_hud.rpy`, `game/sb_screens.rpy`, `game/sb_loop.rpy`, `game/sb_activities.rpy`, `tools/smoke/wp7_ui.rpy` |
| WP8 | `game/ui_journal.rpy`, `game/screens.rpy`, `tools/smoke/wp8_journal.rpy` |
| WP9 | `game/ch1_alley.rpy`, `game/ch1b_the_offer.rpy`, `game/ch2_tour.rpy`, `game/script.rpy`, `tools/smoke/wp9_prologue.rpy` |
| WP10 | `game/events_arc1.rpy`, `game/ch4_mission.rpy`, `game/ch5_debrief.rpy`, `game/missions_arc1.rpy`, `game/story_arc1.rpy`, `game/story_kurose.rpy`, `game/story_oda.rpy`, `game/events_romance.rpy`, `game/events_activities.rpy`, `game/events_stand.rpy`, `game/events_intimate.rpy`, `tools/smoke/wp10_chapters.rpy` |
| Frozen after WP0 (changes only via WP11) | `game/sb_hooks.rpy`, `game/jjk_defs.rpy`, `game/sb_relations.rpy`, `game/explore.rpy`, `tools/smoke.sh`, `tools/smoke/_lib.rpy`, `tools/smoke/load_slot.rpy`, `tools/load_all_saves.sh`, `tools/check_content.py` |
| Unchanged in phase 1 | `game/jjk_sprites.rpy` (not regenerated), `game/jjk_screens.rpy`, `game/gui.rpy`, `game/sb_threads.rpy`, `game/options.rpy` (until WP11), all images |

**Every package's standard acceptance** applies in addition to the package's own list:
- (a) Lint is clean, meaning no problems and no `VALIDATE:` lines (8.4).
- (b) `python3 tools/check_content.py --no-literal-name <owned .rpy files>` passes.
- (c) The package's harness passes via `tools/smoke.sh`.
- (d) The core-flow harness `tools/smoke.sh tools/smoke/core_flow.rpy` passes in the worktree. It sets a post-prologue fixture (names set, prologue flags), calls `arc_one_open`, then drives a day's loop functions:
  - `pick_event("story")` and `play_event`;
  - three `sb_do_*` actions;
  - `new_day()` ×3;
  - `sb_place`, `sb_char("yuji")` and `sb_map` each rendered once.

  It must finish with no exception. It deliberately doesn't play the prologue, whose name input blocks a harness until WP9 adds the autoplay guard; WP9's own harness covers the prologue.
- (e) The final message lists "what changed / what to look at" in five lines or fewer, for the owner.

### WP0 · Scaffold, contracts, tooling (wave 0, sequential)

**Owns** (then hands over as in the table):
- **new:** `game/sb_hooks.rpy`; `game/bg_placeholders.rpy`; `game/ui_hud.rpy`, `game/ui_map.rpy` and `game/ui_journal.rpy` (code moved in); stubs `game/sb_grades.rpy`, `sb_missions.rpy`, `sb_board.rpy`, `sb_memories.rpy`, `sb_items.rpy`, `sb_tokyo.rpy`; `tools/smoke/_lib.rpy`, `core_flow.rpy`, `wp0_stubs.rpy`, `load_slot.rpy`; `tools/load_all_saves.sh`; `tools/check_content.py`;
- **edits:** `game/sb_world.rpy`, `sb_events.rpy`, `sb_screens.rpy`, `sb_relations.rpy`, `sb_activities.rpy`, `jjk_defs.rpy`, `lighting.rpy`, `explore.rpy`, `ch5_debrief.rpy` (lines 163–172 only), `tools/smoke.sh`.

**Depends on:** nothing.

**Tasks:**
0. **Backup:** copy `game/*.rpyc`, `game/saves/` and `~/Library/RenPy/JJKgamemd-1788928056/` to `~/Desktop/JJK_backup_phase1_<YYYYMMDD>/`, and record the file count. Create branch `phase1` in the owner's folder.
1. `sb_hooks.rpy`, exactly as in 3.1 and 3.13, including migration 5.
2. `sb_world.rpy`:
   - `new_day()` adds `store.actions_today = set()` and ends with `run_new_day_hooks()`;
   - delete `KYOTO_DAY` and `days_left()`.
3. `sb_events.rpy`:
   - `find_events` checks `event_allowed(e)` and stops checking `min_day` / `max_day` (D40);
   - `play_event` gains `$ run_event_done(e)` as a new statement after the `if e["thread"]:` block. Existing statements stay textually unchanged.
4. **Move screens**, verbatim except the deletions listed:
   - `period_pips`, `sb_hud`, `hud_date` and the `sb_hud_*` / `sb_place_text` styles → `ui_hud.rpy`. Remove the countdown and the `days_left` call.
   - `sb_map` (signature becomes `sb_map(layer="campus")`) and the `sb_node_*` styles → `ui_map.rpy`. Remove the Filament line and `_sense`.
   - `jjk_status` and `jjk_journal` → `ui_journal.rpy`. Remove the countdown line. Add the stub `screen journal(tab="people")`.
   - `sb_screens.rpy` keeps `sb_place`, `sb_char`, `place_actions` and the action styles. `place_actions` appends `registered_place_actions(loc)` before "wait" and drops the Emberfall "temper" entry.
5. `ch5_debrief.rpy` 163–172 → the two mcthink lines (5.4.2).
6. `jjk_defs.rpy`:
   - `image="<tag>"` on mc, yuji, megumi, nobara, maki, panda, toge, gojo, yaga, ijichi, shoko, utahime and sana;
   - `define config.side_image_only_not_showing = True`;
   - `define config.say_attribute_transition = Dissolve(0.12)`;
   - `CHARS` gains `ijichi` and `sana`.
7. `sb_relations.rpy`:
   - `CAST` gains `utahime` ("Utahime Iori", "Kyoto teacher"), `ijichi` ("Kiyotaka Ijichi", "Assistant manager") and `sana` ("Sana Torii", "In memory");
   - `ROSTER_ORDER` gains utahime and ijichi;
   - `default roster` gains `"ijichi"`;
   - `add_bond`, `add_aff`, `recruit` and `begin_together` call `toast(...)` with kinds `bond` / `bond_rank` / `aff` / `info` and `who` / `amount` (D34).
8. `bg_placeholders.rpy` (`init -3 python`):
   - `bg_placeholder(path, fallback)`: the real file if `renpy.loadable(path)`, else `fallback`;
   - images `bg alley`, `bg alley dark`, `bg ridge_veil`, `bg utahime_office`, `bg gojo_office`, `bg map_tokyo`, `bg shibuya`, `bg harajuku`, `bg shinjuku`, `bg kawasaki` and `bg yotsuka`, built from existing pictures with `Transform`/`Composite` and `TintMatrix`, `BrightnessMatrix` and `SaturationMatrix`:
     - alley: konbini darkened −0.25 and desaturated 0.6;
     - alley dark: −0.45, with a violet tint;
     - ridge_veil: `ridge.png` with `veil.png` over it at alpha 0.35;
     - utahime_office: office, tinted cool;
     - gojo_office: dorm_common, tinted warm pink;
     - map_tokyo: city_night at −0.5;
     - districts: city_night, town_street and street_morning, variously tinted.
   - `BG_LIGHT` rows for each in `lighting.rpy`.
9. **Stub files:** every symbol in section 6 with its final signature, docstring and stub behaviour. Stub labels are in the files of their owners (`stage_person` in `sb_activities.rpy`, `dev_tools` in `explore.rpy`). `explore_campus` gains `$ ensure_state()`.
10. **Tooling** (section 8): `smoke.sh` v2, `_lib.rpy`, `core_flow.rpy`, `wp0_stubs.rpy`, `load_slot.rpy`, `load_all_saves.sh`, `check_content.py`.

**Acceptance:**
- Standard (a)–(e).
- `grep -n -e days_left -e KYOTO_DAY game/*.rpy` returns nothing.
- `tools/smoke/wp0_stubs.rpy` calls every stub in section 6 and renders every stub screen once, with no exception.
- `tools/load_all_saves.sh` runs over every owner save and writes `shots/load_report.txt`. Every slot must either land where it was or report `load_recover` / `return_recover` ran. No slot raises.
- `check_content.py --all game/*.rpy` runs and lists today's expected findings (the mc lines, technique text and so on). This is the baseline for WP11.
- **Owner check (checkpoint 1):** a new game plays as before. The HUD has no Kyoto countdown. Side portraits appear when an off-screen character speaks: Yaga in the Sun Mall briefing, Kaito on his own lines. An existing save loads.

### WP1 · World, offices, Tokyo and the map (wave 1)

**Owns:** see the table. **Depends on:** WP0. It reads `mission_markers()` (WP3) through the stub.

**Tasks:**
1. The offices in `LOCATIONS` / `LOC_ORDER`, the ridge description, and the AREAS comment (3.2).
2. `AREAS`, `area_of`, `places_in`, `usual_places`, `when_at` and `FLAG_SCHEDULES` (plus its check in `char_location`).
3. Schedules for Utahime and Ijichi, with WEEKEND. `gojo_in_on`, `roll_gojo`'s in-day placement, the `gojo_in` default, `gojo_in_today()` and the new-day toast.
4. The `can_enter` rules for both offices.
5. `new_day()`: `refresh_vitals()`, `hp = hp_max`, with the hook call kept last.
6. Migration 15. The validator: every `LOCATIONS` key is in exactly one area, every area place exists, every schedule location exists, and every district bg image exists.
7. `sb_tokyo.rpy`: `DISTRICTS` with 2–3 first-person arrival lines each; `tokyo_open`, `district_state`, `trip_ok_now`, `car_action_ok`; labels `sb_trip` and `sb_do_car`, with the action registration (3.3).
8. The ridge veil action and `label sb_do_veil` (D15).
9. `ui_map.rpy`: `sb_map(layer)` as in 4.6, with the Find someone strip and `FACE_BOX`.
10. `PLACE_LIGHT` for both offices, and tuning of the placeholder backgrounds.

**Acceptance:**
- Standard (a)–(e).
- `wp1_world` passes:
  - **Regression:** for days 1–14 × 5 periods, with no `intensive_done` flag, `char_location` for the original 9 characters equals a frozen copy of today's SCHEDULE / WEEKEND / roll_gojo logic embedded in the harness.
  - The offices lock correctly: Utahime's before `utahime_arrived` and at Night; Gojo's before `intensive_done`.
  - Once recruited, Utahime is in her office on a weekday morning.
  - Over 60 simulated `new_day()` calls with `intensive_done`, Gojo is in 7–14 times and never on consecutive days. Without the flag: 0 times.
  - `new_day()` restores hp.
  - Every district is locked without `ijichi_rides`. Shinjuku is locked below Grade 2; Kawasaki without `kawasaki_open`.
  - `sb_trip` started in the Morning under autoplay ends in the Afternoon, at the gate.
  - A `FLAG_SCHEDULES` test entry moves a character.
  - Screenshots of both map layers are saved to `shots/wp1/`.
- **Owner check:** on day 1 the map shows six areas with names of who is where. The Tokyo tab is locked with its hint. Using the review tools, Tokyo opens and a Shibuya trip takes half a day.

### WP2 · Grades, per-character stats, Last Light and combat data (wave 1)

**Owns:** see the table. **Depends on:** WP0. It reads `acts_done()` (WP3) through the stub.

**Tasks:**
1. `sb_grades.rpy`: everything in 3.4, including `grow_everyone` registered as a new-day hook.
2. `screen grade_card` and `label show_grade_card` (4.10).
3. `sb_energy.rpy`:
   - `TECHNIQUES` holds only `timestop`, shown as Last Light, and `tech()` ignores `store.technique`;
   - the capped `gain()` with its toasts;
   - `raise_reserve`;
   - `grade_name()` → `grade_label`;
   - `default technique = "timestop"`, `default grade = None`.
4. `sb_combat.rpy`, everything in 3.5. Keep `call screen combat_screen` and `$ _a = _return` textually identical.
5. Migrations 10, 20 and 30. The validator: NPC_BASE grades, ENEMIES grades and MOVES tiers are valid.

**Acceptance:**
- Standard (a)–(e).
- `wp2_grades` passes:
  - `tech()["name"] == "Last Light"` with `technique = "filament"`;
  - `MOVES` has one key;
  - the legacy grade migration: 3 → g3, 4 with `roll_call` → g4, 4 without it → None;
  - at g4, `control = 35`, then `gain("control", 50)` → 40; a value of 47 is never lowered;
  - at g4, `raise_reserve(100)` from 60 → 100;
  - `promote("mc", "g3")` → `talisman_slots() == 2` and `grade_cap("stat") == 55`;
  - 60 simulated days with `acts_done` stubbed to 1 give ≥ 1 NPC promotion and none above g3 or above the NPC's max grade; stats never decrease;
  - `combat_begin("alley_curse")` plus 4 rounds of any action → `cb["over"] == "down"`;
  - `promo_g3` answered correctly every round (autoplay) → `"win"`;
  - migration 10 on an Emberfall fixture gives `control ≥ output`, and a second run changes nothing.
- `check_content.py --one-technique game/sb_energy.rpy game/sb_combat.rpy game/sb_grades.rpy` finds nothing, except lines tagged `# legacy-technique`.
- **Owner check:** the alley fight ends after four exchanges.

### WP3 · Mission registry, story chain, new stub scenes and events (wave 1)

**Owns:** see the table. **Depends on:** WP0. It calls WP2's `add_merit` / `promote` / `show_grade_card` and WP6's `give_item` / `add_yen` through the stubs.

**Tasks:**
1. The record format, `ACTS`, the main story table (3.6.1), character missions (3.6.2), `MISSIONS`, `MISSION_BY_ID`, `MISSION_BY_LABEL`, `RETIRED_LABELS` and `JOURNAL_CAST`.
2. `mission_status` with the interaction-scoped cache (`config.interact_callbacks`), and `mission_reason`.
3. The queries: `missions_list`, `missions_here`, `missions_with`, `mission_markers`, `next_for`, `current_objective` / `objective_text` (every written step has an objective), `act_done`, `acts_done`, `act_progress` and `main_story_complete`.
4. Register the event gate and the done hook. `complete_mission` pays once; `mission_fail`.
5. `label start_mission(mid)`.
6. `missions_stubs.rpy`: `st_utahime_office` (registered with `ev`), `st_promotion_g3`, `cm_ijichi_1` and `cm_maki_1`, all first person, with expressions, and marked as placeholders.
7. Arc Two: `begin_arc_two` and `label arc_two_start` (3.6.3).
8. `sb_events.rpy`:
   - SMALLTALK for utahime and ijichi (4 lines each);
   - `PROMO_LINES`;
   - `sb_smalltalk` speaks the remark first when `pop_remark(who)`;
   - narration converted to "I";
   - delete WP0's transitional `_calendar_gate` (D40) once every story/mission `ev()` is bound to a mission or retired.
9. Migrations 40, 50, 60 and 65 (the mission part). The validator:
   - every written label exists;
   - `where` and `with_who` are valid;
   - `done_if` / `skip_if` syntax is valid;
   - ids and `order` values are unique;
   - every `ev(kind in ("story", "mission"))` label is bound to a mission or is in `RETIRED_LABELS`.

**Acceptance:**
- Standard (a)–(e).
- `wp3_missions` passes:
  - **A fresh post-prologue state** (`settled_in`, day 1, `arc_start_day` 1):
    - nothing is available on day 1;
    - on day 2, `m_roll_call` is available;
    - the steps then go locked → available/waiting → done in table order, with each gap respected;
    - no unwritten row ever blocks;
    - `m_sunmall` shows in `missions_here("office")` only while Yaga is there;
    - `m_promo_g3` is locked with the reason "Merit 50/60" at merit 50, and available at 60;
    - `mission_fail` makes it `waiting` until the next day.
  - **An old-save fixture:**
    - done_events {st_roll_call, st_board_open, st_second_years, ev_mission_sunmall, st_aftermath}, flag `sunmall_done`, grade g3;
    - after migrations: `m_utahime` is the current step; `m_promo_g3` is done; merit is backfilled to 5 + 30 + 5 + 20 = 60, and a second migration run adds nothing;
    - arc 2 → 1.
  - `current_objective()` is printed at every step to `shots/wp3/objectives.txt`, for a human read-through.
  - `begin_arc_two()` closes the unfinished character missions.
  - `main_story_complete()` is False.
- **Owner check:** in a new game, roll call comes the next morning with the grade card, then Utahime's introduction. The Sun Mall waits in Yaga's office until you start it, then comes the aftermath the next morning, then Kurose.

### WP4 · Utahime's board (wave 1)

**Owns:** see the table. **Depends on:** WP0. It uses WP2 (`sorcerer_power`, `npc_stats`, `add_merit`, `train_together`), WP6 (`give_item`, `add_yen`) and WP3 (`recruit` via the flag) through the stubs.

**Tasks:**
1. The parts tables, `PARTNER_LINES` and the defaults (3.7).
2. Weekly regeneration as a new-day hook, the replacement offer after one is taken, and the taken cards.
3. `board_host`, `board_open`, and the action registration.
4. `label sb_do_board` → `board_screen` → `board_partner` → `label run_board_mission`: narration, resolve, rewards, log, cost, time rules and the misgrade reveal.
5. `misgrade_count()` and `board_summary()`.
6. Migration 80. The validator: every grade has curses, and every partner has lines.

**Acceptance:**
- Standard (a)–(e).
- `wp4_board` passes:
  - offers are identical for the same week and differ across weeks;
  - at g4 the offers are two ≤ g4 and one g3 `senior_only`;
  - gojo, yaga, utahime, shoko, ijichi and anyone off campus are never offered as partners;
  - over 200 trials, a g4 job with Megumi is `clean` at least 80% of the time;
  - over 500 generated offers, 12–22% of the g4/g3 offers are misgraded;
  - rewards are paid exactly once; exactly 2 periods pass;
  - refused in the Evening;
  - a taken card appears when Megumi outranks you;
  - `board_host()` switches with `utahime_leads_kyoto`;
  - screenshots are saved.
- **Owner check:** after Utahime's introduction, take a Grade 4 job with Nobara, read the result, see the toasts stack, and find the merit in the journal.

### WP5 · Memories (wave 1)

**Owns:** see the table. **Depends on:** WP0. The prologue sub-label names are fixed by D39 (WP9 creates them).

**Tasks:**
1. The `MEMORIES` catalogue (3.9). Read every hangout and act scene to title it.
2. The seen rules and the legacy fallbacks (confirm each flag name against its scene). The `config.label_callbacks` recorder.
3. `memory_groups`, `memory_counts`, `memory_scope`, `memory_replay` and `record_act`; `label mem_play`.
4. The Sana unlock triggers (D11). The memory part of migration 65. The validator: every catalogued label exists, except Sana's three and, until WP9 merges, the prologue sub-labels.

**Acceptance:**
- Standard (a)–(e).
- `wp5_memories` passes:
  - a legacy fixture lists the right seen entries by person and by act;
  - the label callback records `st_roll_call` in normal play but not inside `renpy.call_replay`;
  - `memory_scope` contains every required key;
  - replaying `st_roll_call` and `act_confide("yuji")` via `mem_play` leaves `bonds`, `flags`, `day` and `period` unchanged, with no toasts;
  - the Sana flashbacks show their hints, and "Written in a later build" once triggered.
- **Owner check** (after WP8 merges): replay "Roll Call" from the journal and come back with nothing changed.

### WP6 · Items, equipment and the armory (wave 1)

**Owns:** see the table. **Depends on:** WP0. It uses WP2's grade API through the stubs.

**Tasks:**
1. `ITEMS` (3.8), including the `fx` numbers.
2. The inventory and equipment API with its rules. `retain_after_load` in the equip functions.
3. `sync_keepsakes()` as a new-day hook and as migration 70.
4. The armory action registration, `label sb_do_armory` and `screen armory`.
5. The validator: item grades are valid; items referenced by missions and board drops exist.

**Acceptance:**
- Standard (a)–(e).
- `wp6_items` passes:
  - flags `took_watch` and `kurose_leak` grant `watch` and `kurose_photocopy` exactly once across three syncs;
  - at g4: one slot; `spark` refused with "Needs Grade 2"; a special refused unless bound; a second special refused;
  - after `promote("mc", "g3")`: `iron_seal` equips into slot 2;
  - the armory at g4 offers `slaughter_demon` as `take`, `nunchaku` as `sealed`, `playful_cloud` as `story` and `inverted_spear` as `arcii`.
- **Owner check:** after Maki's armory mission, the Slaughter Demon shows under Equipment.

### WP7 · HUD, toasts, place view, person view, loop (wave 1)

**Owns:** see the table. **Depends on:** WP0. It uses WP3 (`missions_here`, `missions_with`, `start_mission`, `objective_text`, `arc_two_start`), WP1 (`gojo_in_today`, `car_action_ok`), WP2 (`train_together`, `raise_reserve`), WP5 (`record_act`), WP4 (`board_open`) and WP11 (`dev_tools`) through the stubs.

**Tasks:**
1. `ui_hud.rpy`:
   - the new `sb_hud` (4.1);
   - `ToastQueue`, `toast_push`, `TOAST_SINK[0]` and `config.notify`, with merging;
   - the overlay screen `toasts`, added to `config.overlay_screens`;
   - `objective_toast` and `check_objective()`.
2. `sb_screens.rpy`:
   - the new `sb_place` (4.4, including the arrival caption and the low-stamina line) and `sb_char` (4.5);
   - `AMBIENT`, `PLACE_STAGING`, `PERSON_GREET_EXPR` and `ambient_of`;
   - `place_actions` as specified.
3. `sb_activities.rpy`:
   - `label stage_person`;
   - `person_choices` with its ranking (section 6);
   - activity `lesson` (who gojo, loc `gojo_office`, `when="lesson_ok"`), with the `when` check added to `activity_state`, and `label act_lesson`.
4. `sb_loop.rpy`. All protected statements (2.1) are kept textually:
   - delete `$ quick_menu = False`;
   - add `$ ensure_state()` at the top of the `while` body, and `$ check_objective()` before `call screen sb_place`;
   - new `elif`s: `"mission"` → `call start_mission(_r[1])`; `"journal"` → `call screen journal(_r[1])`, then if the return is `("arc_two",)`, `call arc_two_start`; `"dev"` → `call dev_tools`;
   - `sb_travel` handles `("district", key)` → `call sb_trip`;
   - `sb_person` handles `"mission"` and `"act"`;
   - `sb_activity`:
     - calls `stage_person` before everything except "hang";
     - after the act, calls `record_act` and `train_together` (spar/train 3 "output", study 2 "insight", swim/walk 1);
     - resets with `scene expression graded_bg()`;
   - once a day (`actions_today`) for hold, rest and racks;
   - `sb_do_train`: `raise_reserve(1)` in place of the 140 clamp;
   - `sb_spar`: `train_together(who, 3, "output")` in place of its extra gains;
   - `sb_do_hold` gets Last Light text;
   - `sb_do_temper` is kept as a retired two-line label (D31);
   - `sb_do_tools` is relabelled "Look through the racks";
   - new `label sb_do_release` (companion leaves);
   - every narration line converted to "I" (D9).
5. The validator: `AMBIENT` and `PLACE_STAGING` keys are valid people and places.

**Acceptance:**
- Standard (a)–(e).
- `wp7_ui` passes:
  - `place_actions` has no "temper" or "missions", and includes "board" at `utahime_office` when open;
  - over every rostered person × every place × every period, `person_choices` returns ≤ 4 entries, always ends with talk, and never includes an unavailable activity;
  - 8 rapid `renpy.notify` calls all appear, in order;
  - two `add_bond("yuji", 2)` calls merge into "+4";
  - `sb_place` renders 4 people with nameplates (screenshot);
  - a returned `("act", "wait")` still works;
  - `renpy.get_screen(("sandbox", "menu"))` hides the quick menu (checked after WP8 merges).
- `tools/load_all_saves.sh` in the worktree: every save parked on `call screen sb_place` loads into the new place view without `load_recover`.
- **Owner check (checkpoint 3):**
  - over three in-game days, the HUD shows only the date and three buttons;
  - Yuji at noon offers 3–4 sensible choices and stays on screen while you talk and eat;
  - bond gains stack;
  - the next objective slides in when it changes;
  - Gojo's lesson appears on an in-day (use the review tools).

### WP8 · Journal and engine screens (wave 1)

**Owns:** see the table. **Depends on:** WP0. It reads the WP2–WP6 APIs; the final visual check runs after they merge.

**Tasks:**
1. `screen journal(tab)` with its six tabs and the people detail pane (4.7).
2. The `jjk_status` and `jjk_journal` wrappers.
3. `kaito_card_image()`.
4. Silhouettes and the generic 「？」 card.
5. A meter with a cap marker and an off-scale overflow (inside `ui_journal.rpy`).
6. The Equipment picker, with the `editable` rule (D4).
7. Memories tiles using `memory_replay`.
8. The Arc Two card.
9. `screens.rpy`: the say-screen side image and the `mc_face` preference; the quick menu, both variants (D25); navigation "Journal".

**Acceptance:**
- Standard (a)–(e).
- `wp8_journal` renders every tab for a fresh state and a rich fixture (grade g3, items, promotions, memories), with screenshots to `shots/wp8/`.
- An equipment change made through the campus journal survives a save and a load in the harness.
- A replay started from the journal returns to the journal.
- The quick menu is hidden on `sb_place` and shown in dialogue.
- **Owner check:** the six tabs read well at 1920×1080, with no overlaps. The side portrait never overlaps the text. The "[mc_name]'s portrait: Hide" preference works.

### WP9 · The prologue in first person (wave 1)

**Owns:** see the table. **Depends on:** WP0 (image tags, the backgrounds, `story_point`, `ensure_state`, `hide_side_images`). The fight's four-round ending needs WP2.

**Tasks:** everything in 5.2 and the prologue part of 5.1: the sub-labels, the conversion, Sana's thing, Last Light, the alley backgrounds and the blackout flag, the fight call, Gojo naming it, the ridge veil, `arc_one_open`, the story_point markers, the replay guards, and expressions in every scene (at least two expression changes per speaking character per scene).

**Acceptance:**
- Standard (a)–(e).
- `check_content.py --no-mc-on-screen --one-technique --no-deadline --narration-person` on the four files finds nothing.
- `grep -n -e tname -e casket -e 'bg konbini'` on the four files finds nothing.
- At least 30 say-with-attribute uses.
- A before/after diff of the `flag()` / `gain()` / `add_bond()` lines shows each still on the same choice (script: `git diff phase1 -- <files> | grep -E '^[-+].*(flag|gain|add_bond)\('`, reviewed by hand).
- `wp9_prologue` under autoplay:
  - calls `ch1_diner`, `ch1_the_thing`, `ch1_gojo`, `ch1b_goodbye`, `ch2_arrival`, `ch2_the_veil`, `ch2_yaga`, `ch2_first_years` and `arc_one_open` in order, with no exception;
  - asserts `technique == "timestop"`, the flags `sana_told_the_thing`, `last_light_woke`, `named_last_light` and `saw_the_ridge_veil`, and that `mc` is never showing;
  - `renpy.call_replay("ch1b_the_other_road")` returns to the harness (no restart);
  - `renpy.call_replay("ch1_gojo")` doesn't prompt for a name.
- **Owner check (checkpoint 2)**, playing the prologue twice (once to each ending):
  - first person throughout;
  - Sana tells the thing in the dark;
  - no technique choice; Last Light's grey-out with one warm light;
  - the fight ends after four rounds;
  - the alley is not the konbini picture;
  - the tour ends at the ridge veil;
  - expressions change and side portraits appear (not during the blackout);
  - the chosen name appears everywhere.

### WP10 · Later chapters: compatibility edits (wave 1)

**Owns:** see the table. **Depends on:** WP0 (the `raise_reserve`, `add_merit`, `promote` and `show_grade_card` stubs).

**Tasks:**
1. Delete the 36 mc lines and re-stage (5.1).
2. Remove the scene resets in the act labels and add the `show expression who at pos_c` lines (5.1).
3. One technique (5.4.1), including the four ch4 passages, the `tname` caption and the Maki guard.
4. The deadline sweep (5.4.2): every row in the table, `min_day` off every story/mission `ev()`, and the `st_board_open` / `ev_patrol` registrations removed (labels kept). Merge this after WP3: until WP3 deletes `_calendar_gate`, the `min_day` values still order the story beats (D40).
5. Roll call reworked and converted to "I" (5.4.3).
6. ch5: the recommendation in place of the grade.
7. The `raise_reserve` calls.

**Acceptance:**
- Standard (a)–(e).
- `check_content.py --no-mc-on-screen --one-technique --no-deadline` on the owned files finds nothing.
- `grep -n -e 'technique ==' -e tname -e min_day -e 'arc = 2' -e 'min(160' -e 'min(140' -e 'grade = '` on the owned files finds nothing.
- The label count per file is unchanged (`grep -c '^label'`).
- Every `flag("…")` string present before is still present (a script compares the sets).
- The lint dialogue-block count is reported before and after (the expected drop is only the collapsed technique branches and deadline lines).
- `wp10_chapters` under autoplay calls `st_roll_call`, `st_intensive`, `st_roster`, `st_night_before`, `chapter_four`, `chapter_five`, `ms_nade_1` and `act_eat("yuji")` on a seeded store, with no exception. It asserts `arc == 1`, `mc` never showing, and `grade == "g4"` after roll call.
- `tools/load_all_saves.sh` in the worktree reports which saves sit in edited statements and recover.
- **Owner check:** play the Sun Mall and Nade 1. Kaito never appears; Last Light is the only technique named; nothing mentions three weeks.

### WP11 · Integration, review tools, save regression, docs (wave 2)

**Owns:** `game/explore.rpy`, `game/options.rpy`, `README.md`, `tools/README.md`, `tools/gen_sprite_defs.py` (docstring only), `tools/smoke/phase1_all.rpy`, `docs/PLAYTEST.md`, plus all the WP0-frozen files. It may make integration fixes in any file, routing substantial ones to the owning package's agent.

**Depends on:** WP0–WP10 merged.

**Tasks:**
1. Confirm the WP0 backup exists. The integrated compile happens only in the owner's folder, and nothing ever runs Force Recompile.
2. Run lint, every package harness and `check_content.py --all game/*.rpy`, and fix or route every finding.
3. `explore.rpy`: `dev_tools` and `screen dev_panel` (4.13). Explore mode works with the new views and never fires missions.
4. `tools/smoke/phase1_all.rpy`:
   - a fresh game through the prologue (autoplay), then 30 simulated days;
   - each day: the story events and the start-type missions in order (driven through the loop functions), one board job, `new_day()`;
   - it asserts no exceptions and logs the objectives.
5. The save regression: `tools/load_all_saves.sh` over every save in both folders. For each slot, the report shows:
   - version, technique, grade, arc, day, roster size, merit, the current story step, the objective, inventory keepsakes;
   - where it landed (a statement, `load_recover` or `return_recover`).
6. `options.rpy`: `config.version = "0.3 — Arc One, phase 1"`.
7. Docs:
   - README: the new systems, and how to add a mission, memory, item, district, board part, ambient line and schedule-by-flag;
   - `tools/README.md`: the harness kit;
   - the `gen_sprite_defs.py` docstring: the image tags now exist in `jjk_defs.rpy`;
   - `docs/PLAYTEST.md`: a 20-minute owner checklist covering the checkpoints and the known placeholders.

**Acceptance:**
- Lint is clean on the merged tree.
- `check_content.py --all` finds nothing.
- All harnesses pass, including `phase1_all`.
- Every existing save loads without an exception. It lands on campus or at the right prologue step, with bonds, flags and keepsakes intact. The report is attached.
- **Owner check (checkpoint 4)**, following `docs/PLAYTEST.md`:
  - a new game from the alley to Utahime's first board job;
  - an old save loaded, with the journal showing the right story step;
  - the review tools reaching Arc Two with the exact warning text.

When the owner approves, `phase1` is merged into `main`. That is the owner's call.

---

## 8. Testing and review toolkit (WP0)

### 8.1 `tools/smoke.sh` v2

```
tools/smoke.sh <harness.rpy>
  env: SMOKE_TIMEOUT (180) · SMOKE_SAVES=1 (copy the owner's saves in, read-only copies)
       SMOKE_SLOT=<slot> (for load_slot.rpy) · SMOKE_SHOTS (shots/<harness>/) · HEADLESS=1 (opt-in)
```

1. It makes a scratch project under `$TMPDIR/jjk_smoke.XXXX/`:
   - copies `game/*.rpy` and `game/*.rpyc`;
   - symlinks `game/images`, `game/gui`, `game/fonts` and `game/audio`;
   - copies `tools/smoke/_lib.rpy` → `game/zz_smoke_lib.rpy` and the harness → `game/zz_smoke.rpy`.

   Nothing is written into the real `game/`.
2. It runs `renpy.sh <scratch> run --savedir <scratch>/savedir`. The game-local `game/saves` inside the scratch copy is empty, or holds copies when `SMOKE_SAVES=1`. The owner's saves, persistent data and `.rpyc` are never touched (D27). A real window opens, because the dummy driver stalls on macOS 27.
3. A watchdog kills it after `SMOKE_TIMEOUT`.
4. The result is `$SMOKE_SHOTS/result.txt`. The command prints it and exits 0 only if the last line is `RESULT PASS`. The scratch copy is deleted either way.

Several harnesses can run at once, even from one checkout.

### 8.2 `tools/smoke/_lib.rpy`

- `init 999 python`: `config.label_overrides["splashscreen"] = "zz_skip"` and `config.label_overrides["start"] = "zz_smoke"`. `label main_menu: return`. `label zz_skip: return`.
- `check(cond, name, detail="")` appends `PASS name` or `FAIL name: detail`.
- `shot(name)` calls `renpy.screenshot` into `SMOKE_SHOTS`.
- `finish()` writes the result file (with `RESULT PASS` or `RESULT FAIL`) and calls `renpy.quit()`.
- An uncaught exception is caught by `config.exception_handler`, which writes `RESULT FAIL` with the traceback and quits.
- `autoplay(on=True)`: sets `smoke_autoplay`, `config.auto_choice_delay = 0.05`, skip-unseen, and `config.skipping = "fast"`.
- `fixture(**kw)` sets store variables. `settle()` gives a post-prologue state: `settled_in`, `roll_gojo()`, `ensure_state()`.

### 8.3 Save tools

- `tools/smoke/load_slot.rpy` loads `SMOKE_SLOT` with `renpy.load`. A `config.label_callbacks` watcher notes whether `load_recover` or `return_recover` ran. On the first `config.start_interact_callbacks` after the load, it dumps state (3.12's fields plus `renpy.get_filename_line()`) and quits.
- `tools/load_all_saves.sh` runs it for every `*.save` in `game/saves` and `~/Library/RenPy/JJKgamemd-1788928056` (skipping names with spaces) and writes `shots/load_report.txt`. Today that means 3 slot saves, 10 autosaves and 10 trace/reload saves.

### 8.4 Static checks and validators

- **`tools/check_content.py [--all|flags] FILES`** prints `file:line: rule: text` and exits non-zero on findings. Rules:
  - `--no-mc-on-screen`: `^\s*(show|hide)\s+mc\b`, unless the line has `## first-person exception`.
  - `--one-technique`: `filament|emberfall|aftersound|stillness` (case-insensitive), except on lines tagged `# legacy-technique`.
  - `--no-deadline`: `KYOTO_DAY|days_left\(|days until Kyoto|TO KYOTO|Three weeks from today|In three weeks|\barc\s*=\s*2\b|END OF ARC ONE`.
  - `--narration-person`: narrator lines (`^\s*"…"` not ending in `:`) containing `\b(you|your|yours|yourself)\b` outside `{i}…{/i}`, except on lines tagged `## you-ok`.
  - `--no-literal-name`: `Kaito|Amagiri` inside string literals, except `jjk_defs.rpy` defaults, `script.rpy` `label start`, and the `renpy.input` defaults.
  - `--dup-labels`: a label defined twice across `game/`.
- **Validators** run inside lint (`config.lint_hooks`). Each registered function returns problem strings, which print as `VALIDATE: …`. Each package registers its own (listed in its tasks).

### 8.5 Worktrees and `.rpyc`

Create a worktree with `git worktree add ~/Desktop/JJK_worktrees/wpN phase1`, then `cp -p game/*.rpyc ~/Desktop/JJK_worktrees/wpN/game/`. Never the reverse.

### 8.6 Owner checkpoints

Each checkpoint is played in the owner's folder on branch `phase1`, from the SDK launcher as usual.

| checkpoint | after | what to play |
|---|---|---|
| 1 | WP0 | The old game, with no countdown and with side portraits. An old save loads. |
| 2 | WP2 + WP9 | The new prologue, both endings. |
| 3 | WP1, WP3, WP4, WP6, WP7 | The new campus: HUD, place view, people, map, Utahime and the board, the ride-along. |
| 4 | WP5, WP8, WP10, WP11 | Everything, with `docs/PLAYTEST.md`. |

---

## 9. Risks

1. **Statement names depend on the owner's `.rpyc`.** If they are deleted or force-recompiled, every save falls back to `load_recover` and loses its mid-scene position. *Mitigation:* the backup (WP0 task 0); compiling in the owner's folder only; copies in worktrees; `load_all_saves` in WP0, WP7, WP10 and WP11.
2. **Saves mid-prologue or mid-fight** land on an earlier statement or in `load_recover`, and lose the scene in progress. This is expected. `resume_story` restarts the right step. A save inside a called scene whose return site was rewritten goes to `return_recover`.
3. **Interfaces can drift across parallel packages.** *Mitigation:* the frozen contracts (section 6); the stub harness; validators; WP11's full pass.
4. **Lint can't see Python names in `$` lines or screens.** *Mitigation:* every package ships a harness; `core_flow` runs in every worktree.
5. **Old saves meet Utahime late** (her scene is the new step 120). *Mitigation:* her text is timeless.
6. **Balance numbers are unplayed guesses:** caps, merit, NPC rates, board difficulty. They are all in tables, so tuning never touches code. Values above a new cap are grandfathered, never lowered.
7. **Two populations.** Old saves promoted by the old ch5 keep Grade 3. New games reach Grade 3 through Maki's fight.
8. **Placeholders read as bugs** to a non-technical reviewer: automatic board jobs, unwritten missions, Tokyo arrivals, tinted backgrounds. *Mitigation:* every one says "later build"; `PLAYTEST.md` lists them.
9. **The rewrite can drift in tone or move a flag.** *Mitigation:* the flag/gain diff in WP9 and WP10; the owner reads the prologue.
10. **Replays need every variable a scene reads** in `memory_scope`. A missing one crashes only the replay. The input and `full_restart` are guarded.
11. **Say-with-attributes raises an error for untagged characters** (Mom, Oda, Kurose, Nade, curses). *Mitigation:* the rule in 2.3; `core_flow` and the prologue harness play those scenes.
12. **Ren'Py behaviours this design relies on,** checked in the 8.5.3 source: `load_failed()` skips defaults and callbacks (D1); `return_not_found_label` pops to one frame; `get_screen` accepts a list; `Replay(locked=)`; `call_replay` uses a clean store; `label_callbacks` exists; `side_image_only_not_showing` and `say_attribute_transition` exist; `auto_choice_delay` exists. Still to confirm in WP8's harness: `retain_after_load()` from the campus journal survives save and load. The fallback is already in place, because edits happen only in the main context.
13. **Too many toasts.** *Mitigation:* merging, four visible at a time, a short life, and NPC growth toasting only on promotion.
14. **Information leaves the HUD** (time of day, stamina). *Mitigation:* the arrival caption, graded backgrounds, the low-stamina line, the Stats tab. The owner should judge this in play.
15. **Mixed voice after the prologue** until phase 3 converts the chapters. *Mitigation:* D9 moves the seam to the Sun Mall.

---

## 10. Left for later phases

- **Phase 2 (combat):**
  - fix the damage-and-block moves, allies using your stats, and the Nade 1 bond inversion;
  - Black Flash;
  - partner moves;
  - tool and talisman `fx` applied;
  - board jobs as real fights (`use_combat` via `combat_begin(dict)`);
  - enemy phases;
  - the rest of the time economy.
- **Phase 3+ (story):**
  - write the unwritten rows (their ids are reserved in 3.6.1) and the character missions `cm_*`;
  - district scenes `district_<key>`;
  - Sana's flashbacks `sana_mem_*`;
  - move `m_aftermath` to Act II when the detention center lands (D14);
  - Utahime's Act IV switch (`utahime_leads_kyoto`);
  - Yuji's "death" through `FLAG_SCHEDULES`;
  - convert the chapters to "I" in the order given in D9;
  - re-point the placeholder `bg city` scenes: `ev_nobara_1` (events_arc1:239 and 305), `ev_nobara_3` (1225) and `act_rom_town` (events_romance:10) → Shibuya or Harajuku. The Kawaguchi warehouse and the Saitama Sun Mall keep their own backgrounds.
- **Reserved flag names:** `yuji_secret`, `utahime_leads_kyoto`, `kawasaki_open`, `sukuna_cheek_spoke`, `sukuna_vow_offered`, `sukuna_vow_taken`, `wakuri_clue`, `sana_sketchbook`, `daisy_clip` (item).
- **Art:** the alley, the ridge veil (the big-moment picture), the offices, the Tokyo districts and `map_tokyo`. Each drops in by filename through `bg_placeholder` with no script change: `images/bg/alley.png`, `alley_dark.png`, `ridge_veil.png`, `utahime_office.png`, `gojo_office.png`, `map_tokyo.png`, `shibuya.png`, `harajuku.png`, `shinjuku.png`, `kawasaki.png`, `yotsuka.png`.
