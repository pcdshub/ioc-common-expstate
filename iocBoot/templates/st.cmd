#!$$IOCTOP/bin/rhel7-x86_64/expState

epicsEnvSet( "EPICS_NAME", "$$TRANSLATE(IOCNAME,"a-z_-","A-Z::")" )
epicsEnvSet( "ENGINEER",  "$$ENGINEER" )
epicsEnvSet( "LOCATION",  "$$HUTCH" )
epicsEnvSet( "IOCSH_PS1", "$$IOCNAME> ")

< envPaths

# Run common startup commands for linux soft IOC's
< /reg/d/iocCommon/All/pre_linux.cmd

# Register all support components
dbLoadDatabase("$(TOP)/dbd/expState.dbd")
expState_registerRecordDeviceDriver(pdbbase)

# Load record instances
dbLoadRecords("$(TOP)/db/iocSoft.db",            "IOC=$(EPICS_NAME)" )
dbLoadRecords("$(TOP)/db/save_restoreStatus.db", "P=$(EPICS_NAME):" )

$$LOOP(COUNT)
dbLoadRecords("$(TOP)/db/exp_state.template",    "P=IOC:$$HUTCH:$$INDEX:EXPSTATE")
$$ENDLOOP(COUNT)

# Setup autosave
save_restoreSet_status_prefix("$(EPICS_NAME):" )
save_restoreSet_IncompleteSetsOk( 1 )
save_restoreSet_DatedBackupFiles( 1 )

set_requestfile_path( "$(PWD)/../../autosave"             )
set_savefile_path   ( "$(IOC_DATA)/$$IOCNAME/autosave" )

set_pass0_restoreFile( "$$IOCNAME.sav" )        #just restore the settings
set_pass1_restoreFile( "$$IOCNAME.sav" )        #just restore the settings

# Configure access security: this is required for caPutLog.
asSetFilename("$(TOP)/iocBoot/templates/unrestricted.acf")

# Initialize the IOC and start processing records
iocInit()

# caPutLogInit("HOST:PORT", config)
# config options:
#       caPutLogNone       -1: no logging (disable)
#       caPutLogOnChange    0: log only on value change
#       caPutLogAll         1: log all puts
#       caPutLogAllNoFilter 2: log all puts no filtering on same PV
caPutLogInit("${EPICS_CAPUTLOG_HOST}:${EPICS_CAPUTLOG_PORT}", 0)

# Start autosave backups
create_monitor_set( "$$IOCNAME.req", 30, "" )

# All IOCs should dump some common info after initial startup.
< /reg/d/iocCommon/All/post_linux.cmd

