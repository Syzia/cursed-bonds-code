Patterns for P8's p2_saves harness (review round 2 of wave 0). Not harnesses:
the files end in .txt so nothing installs, lints or checks them.

zz_rev_play.rpy.txt   loads an owner save, drives the real loop, saves from
                      inside the interaction with the rollback log untrimmed,
                      reloads and compares statement, call depth, day, period
                      and place.
zz_old_park.rpy.txt   makes pre-phase-2 saves parked on sb_map, sb_char, a say,
                      the journal and sb_place, from a scratch rebuild of the
                      tree at 1d3a9db.

Two things a harness that loads a save and plays on must allow for, or it
sits until the watchdog:
  1. Call autoplay(True) BEFORE renpy.load: a menu rebuilt by the load only
     gets its auto-pick then.
  2. The first interaction after a load does not skip. Have the driver end a
     say (return True) or pick the first choice (items[0].action() from the
     choice screen's scope) when one statement has waited for 2 seconds.
