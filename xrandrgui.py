import subprocess
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QLineEdit

from PyQt5.QtCore import Qt

#dsplist = ['HDMI-1', 'DP-1']  # Replace this with your display devices' names

# Run the Linux command and capture its output
command_output = subprocess.check_output('xrandr | grep -v "disconnected" | grep "connected" | sed "s/connected.*//"', shell=True)

# Decode the output from bytes to a string
command_output = command_output.decode('utf-8')

# Split the output into an array of lines
dsplist = command_output.splitlines()

# Print each line of the output
for line in dsplist:
    print(line)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Brightness Control")
        self.setGeometry(100, 100, 500, 300)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        for dsp in dsplist:
            self.add_tab(dsp)

    def add_tab(self, dsp_name):
        tab = QTabWidget()
        layout = QVBoxLayout()


        brightness_label = QLabel(f"Brightness")
        

        brightness_slider = QSlider(Qt.Horizontal)
        brightness_slider.setMinimum(0)
        brightness_slider.setMaximum(200)
        brightness_slider.setValue(100)
        brightness_slider.setTickPosition(QSlider.TicksBelow)
        brightness_slider.setTickInterval(25)

        brightness_input = QLineEdit()
        brightness_input.setMaxLength(4)  # Set max length to 4 for floating point values
        brightness_input.setFixedWidth(50)  # Set the fixed width of the input box
        brightness_input.setText("1.0")  # Set the initial text value


        slider_input_layout = QHBoxLayout()
        slider_input_layout.alignment
        slider_input_layout.addWidget(brightness_slider)
        slider_input_layout.addWidget(brightness_input)

        brightness_control_layout = QVBoxLayout()
        brightness_control_layout.addWidget(brightness_label)
        brightness_control_layout.addLayout(slider_input_layout)
        brightness_control_layout.addStretch()

        layout.addLayout(brightness_control_layout)    

        brightness_input.editingFinished.connect(lambda: self.manual_input_brightness(brightness_input, dsp_name, brightness_slider))
        brightness_slider.valueChanged.connect(lambda value, dsp=dsp_name, slider=brightness_slider, input_box=brightness_input: self.update_brightness_input(value, dsp, slider, input_box))



        for color, color_name in zip(["r", "g", "b"], ["Red", "Green", "Blue"]):
                    gamma_label = QLabel(f"{color_name} gamma")
                    #layout.addWidget(gamma_label)

                    gamma_slider = QSlider(Qt.Horizontal)
                    gamma_slider.setMinimum(0)
                    gamma_slider.setMaximum(200)
                    gamma_slider.setValue(100)
                    gamma_slider.setTickPosition(QSlider.TicksBelow)
                    gamma_slider.setTickInterval(25)                    


                    gamma_input = QLineEdit()
                    gamma_input.setMaxLength(4)
                    gamma_input.setFixedWidth(50)
                    gamma_input.setText("1.0")




                    gamma_slider_input_layout = QHBoxLayout()
                    gamma_slider_input_layout.addWidget(gamma_slider)
                    gamma_slider_input_layout.addWidget(gamma_input)

                    gamma_control_layout = QVBoxLayout()
                    gamma_control_layout.addWidget(gamma_label)
                    gamma_control_layout.addLayout(gamma_slider_input_layout)
                    gamma_control_layout.addStretch()

                    layout.addLayout(gamma_control_layout)

                    gamma_slider.sliderMoved.connect(lambda value, dsp=dsp_name, slider=gamma_slider, input_box=gamma_input, color=color: self.snap_and_change_gamma(value, dsp, slider, input_box, color))

                    gamma_input.editingFinished.connect(lambda dsp=dsp_name, slider=gamma_slider, input_box=gamma_input, color=color: self.manual_input_gamma(dsp, slider, input_box, color))



        tab.setLayout(layout)
        self.tab_widget.addTab(tab, dsp_name)


    def snap_and_change_gamma(self, value, dsp_name, slider, input_box, color):
        snap_threshold = 10
        if 100 - snap_threshold <= value <= 100 + snap_threshold:
            value = 100
            slider.setValue(value)

        gamma = value / 100
        input_box.setText("{:.2f}".format(gamma))

        self.update_gamma_command(dsp_name, color, gamma)

    def manual_input_gamma(self, dsp_name, slider, input_box, color):
        try:
            input_value = float(input_box.text())
            if 0 <= input_value <= 2:
                slider.setValue(int(input_value * 100))

                self.update_gamma_command(dsp_name, color, input_value)
            else:
                input_box.setText(str(slider.value() / 100))
        except ValueError:
            input_box.setText(str(slider.value() / 100))

    def update_gamma_command(self, dsp_name, color, gamma_value):
        gamma_values = {
            "r": 1.0,
            "g": 1.0,
            "b": 1.0
        }

        gamma_values[color] = gamma_value
        cmd = f"xrandr --output {dsp_name} --gamma {gamma_values['r']}:{gamma_values['g']}:{gamma_values['b']}"
        subprocess.run(cmd, shell=True, check=True)




    def update_brightness_input(self, value, dsp_name, slider, input_box):
        self.snap_and_change_brightness(value, dsp_name, slider)
        input_box.setText("{:.2f}".format(value / 100))


    def snap_and_change_brightness(self, value, dsp_name, slider):
        snap_threshold = 5  # Adjust this value to set the snapping range
        if 100 - snap_threshold <= value <= 100 + snap_threshold:
            value = 100
            slider.setValue(value)

        brightness = value / 100
        cmd = f"xrandr --output {dsp_name} --brightness {brightness}"
        subprocess.run(cmd, shell=True, check=True)
        
    def manual_input_brightness(self, input_box, dsp_name, slider):
        try:
            input_value = float(input_box.text())
            if 0 <= input_value <= 2:
                slider.setValue(int(input_value * 100))

                cmd = f"xrandr --output {dsp_name} --brightness {input_value}"
                subprocess.run(cmd, shell=True, check=True)
            else:
                input_box.setText(str(slider.value() / 100))  # Reset to the current slider value if input is out of range
        except ValueError:
            input_box.setText(str(slider.value() / 100))  # Reset to the current slider value if input is not a number


    @staticmethod
    def change_brightness(value, dsp_name):
        brightness = value / 100
        cmd = f"xrandr --output {dsp_name} --brightness {brightness}"
        subprocess.run(cmd, shell=True, check=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())




