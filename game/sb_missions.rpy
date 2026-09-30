################################################################################
## Cursed Bonds — the mission registry: the story chain, character missions,
## the objective, and Arc Two.
##
## WP3 owns this file (PHASE1_DESIGN.md 3.6). WP0 wrote the frozen signatures
## below as stubs, so other packages can code against them. Every stub says
## what it returns until WP3 writes it.
################################################################################

init -1 python:

    ## Acts: (id, title, kanji, grade band). (WP0 stub: empty.)
    ACTS = []

    ## Who the journal's People tab shows, in order (3.6.2). A basic list until
    ## WP3 settles the format: name / colour / role only for those without a
    ## CAST entry; met is ("roster",), ("flag", name) or ("always",).
    JOURNAL_CAST = [
        dict(who="yuji",    met=("roster",), hint=""),
        dict(who="megumi",  met=("roster",), hint=""),
        dict(who="nobara",  met=("roster",), hint=""),
        dict(who="maki",    met=("roster",), hint="A second-year. She trains at dawn."),
        dict(who="panda",   met=("roster",), hint=""),
        dict(who="toge",    met=("roster",), hint=""),
        dict(who="gojo",    met=("roster",), hint=""),
        dict(who="utahime", met=("roster",), hint="Someone is clearing the room next to Yaga's."),
        dict(who="shoko",   met=("roster",), hint=""),
        dict(who="yaga",    met=("roster",), hint=""),
        dict(who="ijichi",  met=("roster",), hint=""),
        dict(who="nanami",  met=("flag", "met_nanami"), name="Kento Nanami", color="#e8d27a",
             role="Grade 1 sorcerer", hint="A Grade 1 who hates overtime. Act III."),
        dict(who="todo",    met=("flag", "met_todo"), name="Aoi Todo", color="#d89a6a",
             role="Kyoto third-year", hint="Kyoto's loudest third-year. Act IV."),
        dict(who="miwa",    met=("flag", "met_miwa"), name="Kasumi Miwa", color="#8ab8e8",
             role="Kyoto second-year", hint="A Kyoto second-year. Act IV."),
        dict(who="mei_mei", met=("flag", "met_mei_mei"), name="Mei Mei", color="#c8b0e0",
             role="Grade 1 sorcerer", hint="Does nothing for free. Act V."),
        dict(who="yuta",    met=("flag", "met_yuta"), name="Yuta Okkotsu", color="#b8c8d8",
             role="Special grade", hint="A voice on Gojo's phone. Act V."),
        dict(who="sana",    met=("always",), hint=""),
    ]

    ## Status and queries -------------------------------------------------------

    def mission_status(id):
        """WP3. done / skipped / closed / unwritten / active / waiting /
        available / locked, cached per interaction. (WP0 stub: "locked".)"""
        return "locked"

    def mission_reason(id):
        """WP3. Why a mission is locked, in the player's words, e.g.
        "Needs Grade 3". (WP0 stub: "".)"""
        return ""

    def missions_list(kind=None, status=None, act=None, who=None):
        """WP3. Missions matching every filter given, in order. (WP0 stub: [].)"""
        return []

    def missions_here(loc):
        """WP3. Start-type missions available here, with their giver present. (WP0 stub: [].)"""
        return []

    def missions_with(who, loc=None):
        """WP3. Start-type missions this person can give now. (WP0 stub: [].)"""
        return []

    def mission_markers():
        """WP3. {loc: [(text, kind)]} for the map. (WP0 stub: {}.)"""
        return {}

    def next_for(who):
        """WP3. (text, where): the next thing to do with someone. (WP0 stub: None.)"""
        return None

    def current_objective():
        """WP3. dict(text, where, when, mid) for the NEXT line, or None. (WP0 stub: None.)"""
        return None

    def objective_text():
        """WP3. The one-line objective. (WP0 stub: "".)"""
        return ""

    def act_done(act):
        """WP3. True when every non-optional written row of the act is done. (WP0 stub: False.)"""
        return False

    def acts_done():
        """WP3. How many acts, from Act I, are done in a row. (WP0 stub: 0.)"""
        return 0

    def act_progress(act):
        """WP3. (done, written, total) for an act. (WP0 stub: (0, 0, 0).)"""
        return (0, 0, 0)

    def main_story_complete():
        """WP3. Every non-optional story row is written and done. (WP0 stub: False.)"""
        return False

    ## Changing state -------------------------------------------------------------

    def mission_fail(id):
        """WP3. Not today: the mission can be retried tomorrow. (WP0 stub: no-op.)"""
        return

    def complete_mission(id):
        """WP3. Records the mission done and pays its rewards once. (WP0 stub: no-op.)"""
        return

    def begin_arc_two():
        """WP3. Sets arc2_started and closes unfinished Arc One character
        missions. (WP0 stub: no-op.)"""
        return


## WP3. Plays a mission's scene, then completes it and charges its cost.
## (WP0 stub: returns.)
label start_mission(mid):
    return

## WP3. The "This begins Arc Two" warning and card, reached from the campus
## journal. (WP0 stub: returns.)
label arc_two_start:
    return
