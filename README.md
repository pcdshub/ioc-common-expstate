## Experimental State Tracker

Report your hutch's current status and track it over time via the archiver.

PVs:

``IOC:$(HUTCH):EXPSTATE:State.VAL``: for current state description

``IOC:$(HUTCH):EXPSTATE:State.INDX``: to set/get current state index

``IOC:$(HUTCH):EXPSTATE:StateOptions``: to set/get all possible states

``IOC:$(HUTCH):EXPSTATE:StateOptionsJSON``: JSON format of all possible states

``IOC:$(HUTCH):EXPSTATE:UserStatus``: free-form for user-reported status
(Access this by way of ``caget -S IOC:$(HUTCH):EXPSTATE:UserStatus``)

