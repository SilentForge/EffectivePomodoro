import sys
import pygame
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout, QTextEdit, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QRectF, QPointF
from math import cos, sin, radians
from PyQt5.QtGui import QColor, QIntValidator, QIcon, QPainter, QBrush, QPen
# Assuming pomodoro_logic contains the PomodoroTimer class with the required signals
from pomodoro_logic import PomodoroTimer

class CircularProgressBar(QWidget):
    """
    A custom QWidget that displays a circular progress bar.
    
    Attributes:
        value (int): Current progress value, ranging from 0 to 100.
        timer_label (QLabel): Label to display timer or progress text.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)  
        self.value = 0
        self.timer_label = QLabel(self)  
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("QLabel { background-color: transparent; }")

    def resizeEvent(self, event):
        """
        Overridden resize event to update label geometry with the widget's size.
        
        Args:
            event: The resize event.
        """
        self.timer_label.setGeometry(0, 0, self.width(), self.height())

    def set_value(self, value):
        """
        Sets the value of the progress bar.

        Args:
            value (int): The progress value to set, from 0 to 100.
        """
        self.value = value
        self.repaint()

    def paintEvent(self, event):
        """
        Overridden paint event to draw the circular progress bar.
        
        Args:
            event: The paint event.
        """
        # Call the paint event of the base class to handle basic painting operations
        super().paintEvent(event)
    
        # Create a QPainter object for drawing within this widget
        painter = QPainter(self)
        # Enable antialiasing to make the edges of the circle smoother
        painter.setRenderHint(QPainter.Antialiasing)
    
        # Calculate the size of the drawable area, ensuring the circle fits within the widget
        size = min(self.width(), self.height()) - 1
    
        # Set padding around the circle to ensure it does not touch the widget's edges
        padding = 20
        # Define an additional offset for the X position to move the circle right or left
        additional_offset_x = - 1  # Adjust this value to move the circle horizontally
    
        # Define an additional offset for the Y position to move the circle up or down (optional)
        additional_offset_y = 0  # Adjust this value to move the circle vertically
    
        # Calculate the rectangle in which the circle will be drawn
        rect = QRectF(padding + additional_offset_x, padding + additional_offset_y, size - padding * 2, size - padding * 2)
    
        # Set the pen for drawing the circle's outline with a specific color and line width
        background_pen = QPen(QColor("#C0C0C0"), 10)
        painter.setPen(background_pen)
    
        # Draw the ellipse (circle) within the defined rectangle
        painter.drawEllipse(rect)

        # Drawing the progression curve
        progress_pen = QPen(QColor("#007aff"), 8)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        angle = 360 * self.value / 100
        painter.drawArc(rect, -90 * 16, int(angle * 16))

        # Calculate the position of the ball on the curve
        end_angle_rad = radians(90 - (360 * self.value / 100))
        center = rect.center()  # Rectangle center
        radius = (size - padding * 2) / 2  # Radius of the circle on which the ball moves
        ball_x = center.x() + radius * cos(end_angle_rad)  # Calculating the x position of the ball
        ball_y = center.y() + radius * sin(end_angle_rad)  # Calculating the y position of the ball
        ball_radius = 8  # Ball radius
        painter.setBrush(QColor("#009aff"))  

        # Draw the ball
        painter.drawEllipse(QPointF(ball_x, ball_y), ball_radius, ball_radius)


class CustomLineEdit(QLineEdit):
    """
    A QLineEdit with customized placeholder behavior. It changes its text color
    based on focus to visually distinguish between placeholder and input text.
    """
    
    def __init__(self, placeholder_text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText(placeholder_text)
        self.normal_style = "QLineEdit { color: black; }"  # Style for normal input
        self.placeholder_style = "QLineEdit { color: gray; }" # Style for placeholder
        self.setStyleSheet(self.placeholder_style)

    def focusInEvent(self, event):
        """
        Overridden method to change the line edit's style on focus, making the text color black.
        """
        super().focusInEvent(event)
        self.setStyleSheet(self.normal_style)
        if self.text() == self.placeholderText():
            self.clear()

    def focusOutEvent(self, event):
        """
        Overridden method to revert the line edit's style when it loses focus, displaying the placeholder.
        """
        super().focusOutEvent(event)
        if not self.text():
            self.setStyleSheet(self.placeholder_style)

class PomodoroApp(QWidget):
    """
    The main application window for the Pomodoro timer, providing UI for time management
    using the Pomodoro technique. It includes functionality to start, pause, reset timers,
    and customize time settings for work, break, and long break periods.
    """
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.timer = PomodoroTimer()
        self.is_night_mode = False
        self.initUI()  
        self.timer.update_signal.connect(self.update_label)
        self.timer.update_signal.connect(self.update_progress)
        self.timer.finish_signal.connect(self.timer_finished)
        self.timer.session_change_signal.connect(self.update_history)
        self.timer.reset_goal_signal.connect(self.unlock_goal_input)
        self.timer.notify_user_signal.connect(self.notify_user)
        self.timer.session_change_signal.connect(self.update_history)


    def initUI(self):
        """
        Initializes the user interface components and layouts for the Pomodoro app.
        """
        self.setWindowTitle("Pomodoro Timer")
        self.setGeometry(100, 100, 500, 550)
        
        
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.toggle_theme_button = self.create_toggle_button()  
        top_layout.addWidget(self.toggle_theme_button)
        top_layout.addSpacing(2) 

        main_layout.addLayout(top_layout)

        progress_layout = QHBoxLayout()
        self.progress_bar = CircularProgressBar()
        progress_layout.addWidget(self.progress_bar, 0, Qt.AlignCenter)

        main_layout.addLayout(progress_layout)

        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("QLabel { font-size: 30px; color: black; }")
        main_layout.addWidget(self.timer_label, 0, Qt.AlignCenter)

        control_layout = QHBoxLayout()
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_timer)
        control_layout.addWidget(self.start_stop_button)
        self.apply_shadow(self.start_stop_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        control_layout.addWidget(self.reset_button)
        self.apply_shadow(self.reset_button)

        self.set_time_button = QPushButton("Set Time")
        self.set_time_button.clicked.connect(self.set_custom_time)
        control_layout.addWidget(self.set_time_button)
        self.apply_shadow(self.set_time_button)

        main_layout.addLayout(control_layout)

        time_settings_layout = QHBoxLayout()
        intValidator = QIntValidator(1, 999)
        self.work_time_entry = QLineEdit("25")
        self.work_time_entry.setValidator(intValidator)
        time_settings_layout.addWidget(QLabel("Work:"))
        time_settings_layout.addWidget(self.work_time_entry)

        self.break_time_entry = QLineEdit("5")
        self.break_time_entry.setValidator(intValidator)
        time_settings_layout.addWidget(QLabel("Break:"))
        time_settings_layout.addWidget(self.break_time_entry)

        self.long_break_time_entry = QLineEdit("15")
        self.long_break_time_entry.setValidator(intValidator)
        time_settings_layout.addWidget(QLabel("Long Break:"))
        time_settings_layout.addWidget(self.long_break_time_entry)

        main_layout.addLayout(time_settings_layout)
        
        self.goal_entry = QLineEdit()
        self.goal_entry.setPlaceholderText("Enter your goal here...")  
        main_layout.addWidget(self.goal_entry)
        


        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        main_layout.addWidget(self.history_text)



        self.setLayout(main_layout)
        self.apply_stylesheet()

    def create_toggle_button(self):
        """
        Creates a toggle button for switching themes.

        Returns:
            QPushButton: The created toggle theme button.
        """
        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon('sun_icon.png'))
        toggle_button.setIconSize(QSize(32, 32))
        toggle_button.setFixedSize(50, 50)
        toggle_button.setStyleSheet("QPushButton {border: none;}")
        toggle_button.clicked.connect(self.toggle_theme)
        return toggle_button

    def toggle_theme(self):
        """
        Toggles the application theme between light and dark mode.
        """
        self.is_night_mode = not self.is_night_mode
        if self.is_night_mode:
            self.toggle_theme_button.setIcon(QIcon('moon_icon.png'))
        else:
            self.toggle_theme_button.setIcon(QIcon('sun_icon.png'))
        self.apply_stylesheet()


    def apply_stylesheet(self):
        """
        Applies the stylesheet to the widget based on the current theme mode.
        """
        if self.is_night_mode:
            self.setStyleSheet("""
            QWidget {
                font-family: 'Helvetica Neue';
                font-size: 16px;
                background-color: #333;
                color: #ccc;
            }
            QPushButton {
                font-size: 17px;
                border: 1px solid #555;
                border-radius: 10px;
                background-color: #555;
                color: white;
                padding: 10px 20px;
                margin: 5px;
                min-height: 44px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #777;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #555;
                border-radius: 10px; 
                background-color: #555;
                font-size: 17px;
                color: #ccc;
                margin: 5px;
                padding: 8px;
            }
            """)
        else:
            self.setStyleSheet("""
            QWidget {
                font-family: 'Helvetica Neue';
                font-size: 16px;
                background-color: #f2f2f7;
            }
            QPushButton {
                font-size: 17px;
                border: none;
                border-radius: 10px;
                background-color: #007aff;
                color: white;
                padding: 10px 20px;
                margin: 5px;
                min-height: 44px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #005ecb;
            }
            QPushButton:pressed {
                background-color: #004ba0;
            }
            QPushButton:disabled {
                background-color: #a7a7a7;
            }
            QLineEdit {
                border: none;
                border-radius: 8px;
                background-color: #fff;
                font-size: 17px;
                margin: 5px;
                padding: 8px;
            }
            QLabel {
                font-size: 18px;
                color: #000;
                margin: 10px 0;
            }
            QLineEdit, QTextEdit {
                background-color: #fff;
                border: none;
                border-radius: 10px; /* Assurer la cohérence */
                margin: 5px;
                padding: 8px;
                font-size: 17px;
            }
            """)

    def apply_shadow(self, widget):
        """
        Applies a drop shadow effect to a widget.

        Args:
            widget (QWidget): The widget to apply the shadow effect to.
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(2)
        widget.setGraphicsEffect(shadow)

    def toggle_timer(self):
        if not self.timer.is_running:
            current_goal = self.goal_entry.text()
            self.timer.start_timer(current_goal)  # Pass the goal to the timer
            self.start_stop_button.setText("Stop")
            self.lock_goal_input()
        else:
            self.timer.toggle()
            self.start_stop_button.setText("Start")
            self.unlock_goal_input()

    def reset_timer(self):
        self.timer.reset()
        self.update_label(self.timer.format_duration(self.timer.work_duration))
        self.progress_bar.set_value(0)
        self.unlock_goal_input()

    def calculate_time_fraction(self, time_str):
        # Dummy implementation. Replace this with your actual logic.
        # This is just an example assuming 'time_str' is in the format 'mm:ss'.
        total_time = 25 * 60  # Total time for a Pomodoro session in seconds.
        minutes, seconds = map(int, time_str.split(':'))
        elapsed_time = minutes * 60 + seconds
        return elapsed_time / total_time
        
    def update_progress(self, time_str):
        # Check if it's a work or break period
        if self.timer.is_work_period:
            total_time = self.timer.work_duration
        else:
            if self.timer.session_count % 4 == 0:
                total_time = self.timer.long_break_duration
            else:
                total_time = self.timer.short_break_duration

        minutes, seconds = map(int, time_str.split(':'))
        remaining_time = minutes * 60 + seconds
        time_fraction = remaining_time / total_time

        # For pauses, we want the bar to decrease, so we invert the fraction
        if not self.timer.is_work_period:
            time_fraction = 1 - time_fraction

        self.progress_bar.set_value(time_fraction * 100)



    def update_label(self, time_str, time_fraction=None):
        self.timer_label.setText(time_str)
        if time_fraction is not None:
            self.progress_bar.set_value(time_fraction * 100)

    def timer_finished(self):
        if not self.timer.is_running:
            self.start_stop_button.setText("Start")
        self.timer.load_encoded_mp3()

    def update_history(self, session_type=None):
        history_text = ""
        for session in self.timer.session_history:
            session_icon = "🍅" if session["type"] == "Work" else "☕"
            timestamp_str = datetime.strptime(session["timestamp"], '%a %b %d %H:%M:%S %Y').strftime('%Y-%m-%d %H:%M:%S')
            goal_text = f" - Goal: {session['goal']}" if session["goal"] else ""  # Display the goal if present
            history_text += f"<b>{session_icon} {session['type'].capitalize()}:</b> {timestamp_str}{goal_text}<br>"
        self.history_text.setHtml(history_text)



    def test_sound(self):
        self.timer.load_encoded_mp3()

    def set_custom_time(self):
        """
        Sets custom times for work, short break, and long break periods based on user input.
        """
        try:
            # Attempt to convert input values to seconds, using default values if necessary
            work_time_seconds = max(int(self.work_time_entry.text() or "25"), 1) * 60
            short_break_seconds = max(int(self.break_time_entry.text() or "5"), 1) * 60
            long_break_seconds = max(int(self.long_break_time_entry.text() or "15"), 1) * 60
        except ValueError:
            # Handle cases where inputs are not valid numbers
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for all time fields.")
            return

        # Apply custom durations
        self.timer.set_durations(work_time_seconds, short_break_seconds, long_break_seconds)
    
        # Reset timer to reflect new settings
        self.reset_timer()
        # Update display to reflect new initial working time
        self.update_label(self.timer.format_duration(work_time_seconds))
        # Reset progress bar
        self.progress_bar.set_value(0)


    def lock_goal_input(self):
        """Locks the lens input, preventing any modification"""
        self.goal_entry.setDisabled(True)
        self.goal_entry.setStyleSheet("QLineEdit { background-color: #e9e9e9; color: #646464; }")

    def unlock_goal_input(self, clear_goal=False):
        """Unlocks the lens input, allowing modification."""
        self.goal_entry.setDisabled(False)
        self.goal_entry.setStyleSheet("QLineEdit { background-color: white; color: black; }")
        if clear_goal:
            self.goal_entry.clear()

        
    def notify_user(self):
        # Display a notification or message on the interface
        QMessageBox.information(self, "Ready?", "Your next work session starts in a minute. Please set your new goal.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PomodoroApp()
    ex.apply_stylesheet()  
    ex.show()
    pygame.mixer.quit()
    pygame.quit()
    sys.exit(app.exec_())