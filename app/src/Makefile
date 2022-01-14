TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build an ioc application
PROD_IOC = expState

# expState.dbd will be created and installed
DBD += expState.dbd

# expState.dbd will be made up from these files:
expState_DBD += base.dbd
expState_DBD += PVAServerRegister.dbd
expState_DBD += qsrv.dbd
expState_DBD += iocAdmin.dbd
expState_DBD += asSupport.dbd
expState_DBD += caPutLog.dbd

# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
expState_SRCS += expState_registerRecordDeviceDriver.cpp
expState_SRCS_DEFAULT += expStateMain.cpp

# Add locally compiled object code

expState_LIBS += qsrv
expState_LIBS += $(EPICS_BASE_PVA_CORE_LIBS)
expState_LIBS += caPutLog
expState_LIBS += devIocStats
expState_LIBS += autosave
expState_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

