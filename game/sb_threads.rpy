################################################################################
## Cursed Bonds — story threads.
##
## A thread is one person's unfinished business. Events advance it; the journal
## shows the player what they've opened and what's still hanging.
##
## `stages` are the lines I learn, in order; `short` names each of them in a
## word or two, for a person's page when the whole line doesn't fit (the whole
## line is then the hover label). Only the stage index is saved.
################################################################################

init -1 python:

    THREADS = {
        "yuji_countdown": dict(
            who="yuji", title="The Countdown",
            short=["Something quiet", "The roof", "Going first", "The promise"],
            stages=[
                "He is the loudest person here and something underneath him is very quiet.",
                "He stopped moving for one second on the roof. Something enormous is underneath.",
                "He told me the half he never says out loud: he expects to go first.",
                "I promised to be there. He said I couldn't promise that. I did it anyway.",
            ]),
        "megumi_tsumiki": dict(
            who="megumi", title="An Unsolved Problem",
            short=["The exits", "Tsumiki", "The folder", "Fresh eyes"],
            stages=[
                "He watches the exits in every room and won't say what he's watching for.",
                "His step-sister Tsumiki has been cursed asleep for a year.",
                "He gave me the folder. Every note he has, in handwriting like a code.",
                "I found something in it that he had stopped being able to see.",
            ]),
        "nobara_saori": dict(
            who="nobara", title="Somebody Remembered",
            short=["No reasons", "Saori", "Tokyo faces", "Out loud"],
            stages=[
                "She decided she liked me inside a week and won't be asked why.",
                "Saori. The city girl her village decided about until she left.",
                "I've started looking at faces in Tokyo too. She noticed.",
                "One person remembering out loud. That was the whole plan.",
            ]),
        "maki_zenin": dict(
            who="maki", title="Make Them Look",
            short=["Dawn appointment", "Heavenly Restriction", "Mai", "Going back"],
            stages=[
                "Dawn, the dojo, and a standing appointment I didn't agree to.",
                "Heavenly Restriction. I worked it out without being told.",
                "Mai. A twin at Kyoto who hates her in public and might not mean it.",
                "She asked me to be there when she goes back. That is not a small ask.",
            ]),
        "panda_made": dict(
            who="panda", title="Something That Could Say No",
            short=["Welfare checks", "Yaga's work", "Two before"],
            stages=[
                "He does welfare checks at eight in the evening with crisps.",
                "Cursed corpse. Yaga built him a personality and then had to live with it.",
                "He told me about the two he had before him. He doesn't tell people that.",
            ]),
        "toge_voice": dict(
            who="toge", title="Six Words",
            short=["Six fillings", "Getting fluent", "One word"],
            stages=[
                "Salmon, tuna, tuna mayo, bonito flakes, mustard leaf, kelp.",
                "I've started getting them right more often than wrong.",
                "He said a real word to me, on purpose, aimed at nothing.",
            ]),
        "shoko_remembers": dict(
            who="shoko", title="The One Who Was There",
            short=["No rota", "Suguru Geto", "Somebody asked"],
            stages=[
                "Four people in the country can heal. There is no rota.",
                "Suguru Geto. Eleven years, and nobody has asked her how she is about it.",
                "She stopped pretending she didn't need anyone to ask.",
            ]),
        "gojo_measure": dict(
            who="gojo", title="Taking My Measure",
            short=["The alley", "The test", "No show"],
            stages=[
                "He recruited me off one night in an alley and has been unreadable since.",
                "He's been testing me the whole time. I finally noticed.",
                "He taught me something real, without the show. Once.",
            ]),
    }

    THREAD_ORDER = ["yuji_countdown", "megumi_tsumiki", "nobara_saori", "maki_zenin",
                    "panda_made", "toge_voice", "shoko_remembers", "gojo_measure"]

    def thread_stage(tid):
        """-1 = not opened yet."""
        return store.threads.get(tid, -1)

    def open_thread(tid):
        if thread_stage(tid) < 0:
            store.threads[tid] = 0
            renpy.notify("New thread — %s" % THREADS[tid]["title"])

    def advance_thread(tid, to=None):
        """Move a thread forward. Never backwards."""
        cur = thread_stage(tid)
        nxt = (cur + 1) if to is None else to
        nxt = min(nxt, len(THREADS[tid]["stages"]) - 1)
        if nxt <= cur:
            return
        store.threads[tid] = nxt
        if cur < 0:
            renpy.notify("New thread — %s" % THREADS[tid]["title"])
        else:
            renpy.notify("%s — advanced" % THREADS[tid]["title"])

    def thread_done(tid):
        return thread_stage(tid) >= len(THREADS[tid]["stages"]) - 1

    def threads_open():
        return [t for t in THREAD_ORDER if thread_stage(t) >= 0]

    def threads_complete():
        return [t for t in THREAD_ORDER if thread_done(t)]


default threads = {}
