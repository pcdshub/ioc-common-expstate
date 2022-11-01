from dataclasses import dataclass
from functools import partial
import json

from ophyd import EpicsSignal

from pydm import Display
from pydm.widgets.channel import PyDMChannel
from pydm.widgets import PyDMLineEdit

from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QApplication, QMainWindow, QRadioButton, QTextEdit

import LogBookClient.LBG as lbg
from LogBookClient.LogBookWebService import LogBookWebService
from qtpy.QtGui import QFontDatabase, QFont
import os

@dataclass
class ExperimentState:
    index: int
    desc: str

# What numbers do dividers go before?
dividers = [2, 4, 8, 10, 21]
cb2esmap = {}
es2cbmap = {}

experiment_states = {
    0: ExperimentState(
           index=0,
           desc="Configuration Change / Tuning",
       ),
    1: ExperimentState(
           index=1,
           desc="Beam Down (Upstream of Dump)",
       ),
    2: ExperimentState(
           index=2,
           desc="X-ray Beam Alignment",
       ),
    3: ExperimentState(
           index=3,
           desc="X-ray Beam Focusing",
       ),
    4: ExperimentState(
           index=4,
           desc="Laser / X-ray Spatial Overlap",
       ),
    5: ExperimentState(
           index=5,
           desc="Laser Coarse Timing",
       ),
    6: ExperimentState(
           index=6,
           desc="Laser Fine Timing",
       ),
    7: ExperimentState(
           index=7,
           desc="Sample Alignment",
       ),
    8: ExperimentState(
           index=8,
           desc="Collecting Data",
       ),
    9: ExperimentState(
           index=9,
           desc="Sample Change",
        ),
    10: ExperimentState(
           index=10,
           desc="Down - PPS",
        ),
    11: ExperimentState(
           index=11,
           desc="Down - MPS / PMPS",
        ),
    12: ExperimentState(
           index=12,
           desc="Down - Mechanical",
        ),
    13: ExperimentState(
           index=13,
           desc="Down - Laser",
        ),
    14: ExperimentState(
           index=14,
           desc="Down - Controls",
        ),
    15: ExperimentState(
           index=15,
           desc="Down - DAQ",
        ),
    16: ExperimentState(
           index=16,
           desc="Down - AMI",
        ),
    17: ExperimentState(
           index=17,
           desc="Down - Network",
        ),
    18: ExperimentState(
           index=18,
           desc="Down - Sample Delivery",
        ),
    19: ExperimentState(
           index=19,
           desc="Down - Data Analysis Delaying Decisions",
        ),
    20: ExperimentState(
           index=20,
           desc="Down - Other",
        ),
    21: ExperimentState(
           index=21,
           desc="Standby / Off Shift",
        ),
}

class ESTApp(Display):
    new_value = Signal(int)
    new_msg = Signal(str)

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
        if ins in ["ASC", "RIX", "TMO", "TXI", "UED"]:
            ins = ins.lower()

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
        try:
            pars['cmd'] = macros['cmd']
        except:
            pass
        lbws = LogBookWebService(**pars)
        pars2 = {
            'ins'    : "OPS",
            'sta'    : sta,
            'exp'    : ins + " Instrument",
            'url'    : url,
            'usr'    : usr,
            'pas'    : pas,
        }
        try:
            pars2['cmd'] = macros['cmd']
        except:
            pass
        lbws2 = LogBookWebService(**pars2)
        w = lbg.GUIGrabSubmitELog(cfname=None, lbws=lbws, lbws2=lbws2, opts=None)
        self.msgbox = w.findChild(QTextEdit)
        print(self.msgbox)
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
            self.setup_grubber(self.ui.verticalLayout_1, macros)
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
        self.ch2 = PyDMChannel(
            address=f"ca://IOC:{macros['endstation']}:EXPSTATE:Update",
            value_slot=self.handle_update_ctr,
        )
        self.ch2.connect()
        self.ch3 = PyDMChannel(
            address=f"ca://IOC:{macros['endstation']}:EXPSTATE:UserStatus",
            value_signal=self.new_msg,
        )
        self.ch3.connect()
        self.setup_button()
        self.setup_combobox()
        self.setup_timer()

        # Does nothing on moba, need to test in hutch
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint
        )

        app = QApplication.instance()
        for widget in app.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                self.setWindowTitle("%s Experiment State Tracker" % macros['endstation'])
        
        ## Makes the app never render over moba, need to test in hutch
        #app = QApplication.instance()
        #for widget in app.topLevelWidgets():
        #    if isinstance(widget, QMainWindow):
        #        widget.setWindowFlags(
        #            widget.windowFlags() | Qt.WindowStaysOnTopHint
        #        )
        #        print('here')
        #        break

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

    def handle_state_update(self, index):
        self.ui.comboBox.setCurrentIndex(es2cbmap[index])

    def handle_update_ctr(self, value):
        self.reset_timer()  

    def handle_combobox(self, i):
        print(cb2esmap[i])
        self.new_value.emit(cb2esmap[i])
        self.reset_timer()

    def setup_combobox(self):
        # We need to do these in order!!
        j = 0
        for i in range(len(experiment_states)):
            if i in dividers:
                self.ui.comboBox.insertSeparator(1000)
                j = j + 1
            self.ui.comboBox.addItem(experiment_states[i].desc)
            cb2esmap[j] = i
            es2cbmap[i] = j
            j = j + 1
        self.ui.comboBox.currentIndexChanged.connect(self.handle_combobox)

    def handle_msgbutton(self):
        self.new_msg.emit(self.msgbox.toPlainText())

    def setup_button(self):
        self.ui.msgButton.clicked.connect(self.handle_msgbutton)

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
