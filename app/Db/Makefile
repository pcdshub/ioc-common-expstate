TOP=../..
include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE

#----------------------------------------------------
#  Optimization of db files using dbst (DEFAULT: NO)
#DB_OPT = YES

#----------------------------------------------------
# Create and install (or just install)
# databases, templates, substitutions like this
DB_INSTALLS += $(IOCADMIN)/db/iocSoft.db
DB_INSTALLS += $(AUTOSAVE)/db/save_restoreStatus.db

DB += exp_state.template

#----------------------------------------------------
# Create and install (or just install)
# Archive files, templates, substitutions like this

ARCHIVE += exp_state.tpl-arch

#----------------------------------------------------
# Create and install (or just install)
# Autosave request files, templates, substitutions like this

REQ += exp_state.tpl-req

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

