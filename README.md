## Experimental State Tracker

Report your hutch's current status and track it over time via the archiver.

PVs:

``IOC:$(HUTCH):EXPSTATE:State.VAL``: for current state description

``IOC:$(HUTCH):EXPSTATE:State.INDX``: to set/get current state index

``IOC:$(HUTCH):EXPSTATE:StateOptions``: to set/get all possible states

``IOC:$(HUTCH):EXPSTATE:StateOptionsJSON``: JSON format of all possible states

``IOC:$(HUTCH):EXPSTATE:UserStatus``: free-form for user-reported status
(Access this by way of ``caget -S IOC:$(HUTCH):EXPSTATE:UserStatus``)

----------------------------------------------
launch_screen.sh is a script that sets up the environment and launches
a GUI.  The first parameter is the endstation to use, the second parameter
is a comma-separated list of macro assignments.  The macros are mostly
grubber parameters:
    lbinst  - The endstation to use for the grubber (default to the first arg).
    lbuser  - The user name to use for the grubber (default "*opr").
    lbpass  - The password to use (default "pcds").
    lbexp   - The experiment to use (default "current").
    lbdebug - Use the debug logbook, not the production one.
    nolb    - Don't bother with the grubber.
