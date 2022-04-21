from dataclasses import dataclass
from functools import partial
import json

from ophyd import EpicsSignal

from pydm import Display
from pydm.widgets.channel import PyDMChannel
from pydm.widgets import PyDMLineEdit

from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QApplication, QMainWindow, QRadioButton

import LogBookClient.LBG as lbg
from LogBookClient.LogBookWebService import LogBookWebService
from qtpy.QtGui import QFontDatabase, QFont
import os

@dataclass
class ExperimentState:
    index: int
    desc: str
    widget: str


experiment_states = {
    0: ExperimentState(
           index=0,
           desc="Configuration Change / Tuning",
           widget="config_change_button",
       ),
    1: ExperimentState(
           index=1,
           desc="Beam Down (Upstream of Dump)",
           widget="beam_down_button",
       ),
    2: ExperimentState(
           index=2,
           desc="X-ray Beam Alignment",
           widget="alignment_button",
       ),
    3: ExperimentState(
           index=3,
           desc="X-ray Beam Focusing",
           widget="focusing_button",
       ),
    4: ExperimentState(
           index=4,
           desc="Laser / X-ray Spatial Overlap",
           widget="ip_spacial_button",
       ),
    5: ExperimentState(
           index=5,
           desc="Laser Coarse Timing",
           widget="coarse_timing_button",
       ),
    6: ExperimentState(
           index=6,
           desc="Laser Fine Timing",
           widget="fine_timing_button",
       ),
    7: ExperimentState(
           index=7,
           desc="Sample Alignment",
           widget="sample_alignment_button",
       ),
    8: ExperimentState(
           index=8,
           desc="Collecting Data",
           widget="collecting_data_button",
       ),
    9: ExperimentState(
           index=9,
           desc="Sample Change",
           widget="sample_change_button",
        ),
    10: ExperimentState(
           index=10,
           desc="Down - PPS",
           widget="down_pps_button",
        ),
    11: ExperimentState(
           index=11,
           desc="Down - MPS / PMPS",
           widget="down_mps_button",
        ),
    12: ExperimentState(
           index=12,
           desc="Down - Mechanical",
           widget="down_mechanical_button",
        ),
    13: ExperimentState(
           index=13,
           desc="Down - Laser",
           widget="down_laser_button",
        ),
    14: ExperimentState(
           index=14,
           desc="Down - Controls",
           widget="down_controls_button",
        ),
    15: ExperimentState(
           index=15,
           desc="Down - DAQ",
           widget="down_daq_button",
        ),
    16: ExperimentState(
           index=16,
           desc="Down - AMI",
           widget="down_ami_button",
        ),
    17: ExperimentState(
           index=17,
           desc="Down - Network",
           widget="down_network_button",
        ),
    18: ExperimentState(
           index=18,
           desc="Down - Sample Delivery",
           widget="down_sample_delivery_button",
        ),
    19: ExperimentState(
           index=19,
           desc="Down - Data Analysis Delaying Decisions",
           widget="down_data_analysis_button",
        ),
    20: ExperimentState(
           index=20,
           desc="Down - Other",
           widget="down_other_button",
        ),
    21: ExperimentState(
           index=21,
           desc="Standby / Off Shift",
           widget="standby_button",
        ),
}

#
# PYDMLineEdit by default clears itself if it loses focus without a
# return being pressed.  People don't like that, so override the
# focusOutEvent method with this.
#
def myFocusOutEvent(self, event):
    if self._display is not None:
        self.send_value()
    super(PyDMLineEdit, self).focusOutEvent(event)

class ESTApp(Display):
    new_value = Signal(int)

    #
    # When the grubber resizes, tell the mainwindow to adjust to it!
    #
    def lb_resize_handler(self):
        self.mw.adjustSize()

    #
    # This looks at the macros to do some argument parsing similar to the
    # LBG.run_GUIGrabSubmitElog function.
    #
    def setup_grubber(self, layout, macros):
        app = QApplication.instance()
        fontfile = os.path.abspath(os.path.join(lbg.__file__, "..", "..", "static",
                                                "PlayfairDisplay-Regular.ttf"))
        id = QFontDatabase.addApplicationFont(fontfile)
        if id >= 0:
            app.setFont(QFont(QFontDatabase.applicationFontFamilies(id)[0], 10))
        with open(os.path.abspath(os.path.join(lbg.__file__, "..", "..", "static", 
                                               "lgbk.css")), 'r') as f:
            app.setStyleSheet(f.read())
        inssta = macros['endstation']
        try:
            inssta = macros['lbinst']
        except:
            pass
        sta = '0'
        pos = inssta.rfind(':')
        if pos==-1:
            ins = inssta
        else:
            ins = inssta[:pos]
            if len(inssta[pos:]) > 1:
                sta = inssta[pos+1:]

        url = "https://pswww.slac.stanford.edu/ws-auth/lgbk"
        try:
            if macros['lbdebug']:
                url = "https://pswww.slac.stanford.edu/ws-auth/devlgbk"
        except:
            pass

        usr = ins.lower() + "opr"
        try:
            usr = macros['lbuser']
        except:
            pass

        pas = "pcds"
        try:
            pas = macros['lbpass']
        except:
            pass

        exp = "current"
        try:
            exp = macros['lbexp']
        except:
            pass

        pars = {
            'ins'    : ins,
            'sta'    : sta,
            'exp'    : exp,
            'url'    : url,
            'usr'    : usr,
            'pas'    : pas
        }
        lbws = LogBookWebService(**pars)
        pars2 = {
            'ins'    : "OPS",
            'sta'    : sta,
            'exp'    : ins + " Instrument",
            'url'    : url,
            'usr'    : usr,
            'pas'    : pas,
        }
        lbws2 = LogBookWebService(**pars2)
        w = lbg.GUIGrabSubmitELog(cfname=None, lbws=lbws, lbws2=lbws2, opts=None)
        w.lb_resize.connect(self.lb_resize_handler)
        layout.addWidget(w)
        self.lbg = w
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                self.mw = widget
                break

    def __init__(self, parent=None, args=None, macros=None):
        super().__init__(parent=parent, args=args, macros=macros)
        # This is probably assuming too much about est.ui, but whatever.
        if 'nolb' not in macros.keys():
            self.setup_grubber(self.ui.verticalLayout_3, macros)
        inssta = macros['endstation']
        if inssta.find(":") == -1:
            macros['endstation'] = inssta + ":0"
        self.initialize_state_options(macros['endstation'])
        self.channel = PyDMChannel(
            address=f"ca://IOC:{macros['endstation']}:EXPSTATE:State.INDX",
            value_slot=self.handle_state_update,
            value_signal=self.new_value,
        )
        self.channel.connect()
        self.setup_radio_buttons()
        self.setup_timer()
        #
        # Sigh.  We've patched the endstation macro to make sure
        # that it has a station... but too late for the user_note_edit.
        # Let's not define a channel for it in the ui file, but set
        # it here instead.
        #
        self.user_note_edit.channel = f"ca://IOC:{macros['endstation']}:EXPSTATE:UserStatus"

        # Does nothing on moba, need to test in hutch
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint
        )

        ## Makes the app never render over moba, need to test in hutch
        #app = QApplication.instance()
        #for widget in app.topLevelWidgets():
        #    if isinstance(widget, QMainWindow):
        #        widget.setWindowFlags(
        #            widget.windowFlags() | Qt.WindowStaysOnTopHint
        #        )
        #        print('here')
        #        break
        self.ui.user_note_edit.focusOutEvent = partial(
            myFocusOutEvent, self.ui.user_note_edit
        )
        

    def initialize_state_options(self, endstation):
        state_options = EpicsSignal(
            f'IOC:{endstation}:EXPSTATE:StateOptions',
            name='state_options',
        )
        state_options.put([state.desc for state in experiment_states.values()])
        state_json = EpicsSignal(
            f'IOC:{endstation}:EXPSTATE:StateOptionsJSON',
            name='state_options_json',
            string=True,
        )
        state_json.put(
            json.dumps(
                {
                    state.index: state.desc
                    for state in experiment_states.values()
                }
            )
        )

    def setup_radio_buttons(self):
        for state in experiment_states.values():
            button = self.findChild(QRadioButton, state.widget)
            button.clicked.connect(
                partial(self.handle_button_click, state)
            )

    def handle_button_click(self, state, checked):
        if checked:
            self.new_value.emit(state.index)
            self.reset_timer()

    def handle_state_update(self, index):
        try:
            button_name = experiment_states[index].widget
        except IndexError:
            return
        button = self.findChild(QRadioButton, button_name)
        button.setChecked(True)

    def setup_timer(self):
        self.is_red = True
        self.full_timer = QTimer()
        self.full_timer.timeout.connect(self.timer_expired)
        self.full_timer.setSingleShot(True)
        self.reset_timer()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_clock)
        self.update_timer.start(1000)

    def get_timer_setting(self):
        try:
            value = int(self.ui.timer_setting_edit.text())
        except ValueError:
            value = 15
        # Cap the timer at 1 hour
        return min(value, 60)

    def reset_timer(self):
        mins = self.get_timer_setting()
        self.full_timer.start(mins * 60 * 1000)
        self.set_circle_color('black')
        self.expired = False

    def update_clock(self):
        mins = self.get_timer_setting()
        msec = mins * 60 * 1000
        remaining = self.full_timer.remainingTime()
        try:
            deg = (remaining / msec) * 360
        except ZeroDivisionError:
            deg = 360
        self.ui.clock_arc.spanAngle = deg
        remaining_mins = int(remaining/1000/60)
        remaining_secs = int(remaining/1000) % 60
        self.time_remaining_rbv.setText(
            f"{remaining_mins:02}:{remaining_secs:02}"
        )
        if self.expired:
            if self.is_red:
                self.set_circle_color('transparent')
            else:
                self.set_circle_color('red')
            self.is_red = not self.is_red

    def timer_expired(self):
        self.expired = True

    def set_circle_color(self, color):
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(QColor(color))
        self.ui.alarm_circle.brush = brush

    def ui_filename(self):
        return 'est.ui'
