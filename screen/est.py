from dataclasses import dataclass
from functools import partial

from ophyd import EpicsSignal

from pydm import Display
from pydm.widgets.channel import PyDMChannel

from qtpy.QtCore import Qt, Signal, QTimer
from qtpy.QtGui import QBrush, QColor
from qtpy.QtWidgets import QApplication, QMainWindow, QRadioButton


@dataclass
class ExperimentState:
    index: int
    desc: str
    widget: str


experiment_states = {
    0: ExperimentState(
           index=0,
           desc="Configuration Change",
           widget="config_change_button",
       ),
    1: ExperimentState(
           index=1,
           desc="Tuning",
           widget="tuning_button",
       ),
    2: ExperimentState(
           index=2,
           desc="Beam Down (Upstream of Dump)",
           widget="beam_down_button",
       ),
    3: ExperimentState(
           index=3,
           desc="Alignment and Shaping",
           widget="alignment_button",
       ),
    4: ExperimentState(
           index=4,
           desc="Focusing and Correction",
           widget="focusing_button",
       ),
    5: ExperimentState(
           index=5,
           desc="IP Spatial Overlap",
           widget="ip_spacial_button",
       ),
    6: ExperimentState(
           index=6,
           desc="Coarse Timing",
           widget="coarse_timing_button",
       ),
    7: ExperimentState(
           index=7,
           desc="Fine Timing",
           widget="fine_timing_button",
       ),
    8: ExperimentState(
           index=8,
           desc="Sample Alignment",
           widget="sample_alignment_button",
       ),
    9: ExperimentState(
           index=9,
           desc="Collecting Data",
           widget="collecting_data_button",
        ),
    10: ExperimentState(
            index=10,
            desc="Instrument Down",
            widget="instrument_down_button",
        ),
    11: ExperimentState(
            index=11,
            desc="Standby / Off Shift",
            widget="standby_button",
        ),
}


class ESTApp(Display):
    new_value = Signal(int)

    def __init__(self, parent=None, args=None, macros=None):
        super().__init__(parent=parent, args=args, macros=macros)
        self.initialize_state_options(macros['endstation'])
        self.channel = PyDMChannel(
            address=f"ca://IOC:{macros['endstation']}:EXPSTATE:State.INDX",
            value_slot=self.handle_state_update,
            value_signal=self.new_value,
        )
        self.channel.connect()
        self.setup_radio_buttons()
        self.setup_timer()

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

    def initialize_state_options(self, endstation):
        state_options = EpicsSignal(
            f'IOC:{endstation}:EXPSTATE:StateOptions',
            name='state_options',
        )
        state_options.put([state.desc for state in experiment_states.values()])

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
            return int(self.ui.timer_setting_edit.text())
        except ValueError:
            return 15

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
