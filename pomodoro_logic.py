import pygame
import time
import io
import base64
from threading import Thread, Lock
from PyQt5.QtCore import QObject, pyqtSignal
from encoded_mp3 import mp3_base64  # Ensure this is a valid import in your project

pygame.mixer.init()
reset_goal_signal = pyqtSignal()
timer_lock = Lock()

class PomodoroTimer(QObject):
    """
    A timer that alternates between work and break periods, emitting signals for UI updates.
    """
    update_signal = pyqtSignal(str, float)
    finish_signal = pyqtSignal()
    session_change_signal = pyqtSignal(str)
    reset_goal_signal = pyqtSignal()
    notify_user_signal = pyqtSignal()

    def __init__(self, work_duration: int = 1500, short_break_duration: int = 300, long_break_duration: int = 900, parent: QObject = None):
        """
        Initializes the PomodoroTimer with durations and sets up the initial state.

        Args:
            work_duration (int): Duration of the work period in seconds.
            short_break_duration (int): Duration of the short break in seconds.
            long_break_duration (int): Duration of the long break in seconds.
            parent (QObject): Parent QObject for this timer.
        """
        super().__init__(parent)
        self.work_duration = work_duration
        self.short_break_duration = short_break_duration
        self.long_break_duration = long_break_duration
        self.is_running = False
        self.goal = ""
        self.session_history = []
        self.current_time = 0
        self.is_work_period = True
        self.session_count = 0
        self.reset()
        
    def load_encoded_mp3(self) -> None:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        mp3_data = base64.b64decode(mp3_base64)
        mp3_io = io.BytesIO(mp3_data)
        pygame.mixer.music.load(mp3_io)
        pygame.mixer.music.play()


    def reset(self) -> None:
        """
        Resets the timer to its initial state, ready for a new work period.
        """
        self.current_time = self.work_duration
        self.session_count = 0
        self.is_work_period = True
        self.update_time()

    def set_durations(self, work_duration: int, short_break_duration: int, long_break_duration: int) -> None:
        """
        Sets the durations for work, short break, and long break periods.

        Args:
            work_duration (int): New duration for work periods.
            short_break_duration (int): New duration for short breaks.
            long_break_duration (int): New duration for long breaks.
        """
        self.work_duration = work_duration
        self.short_break_duration = short_break_duration
        self.long_break_duration = long_break_duration
        self.reset()

    def toggle(self) -> None:
        """
        Toggles the timer's running state. If the timer is running, it stops; if it's stopped, it starts.
        """
        self.is_running = not self.is_running
        if self.is_running:
            self.start_timer()

    def start_timer(self, goal: str) -> None:
        """
        Starts the timer's countdown process with a specific goal.
    
        Args:
            goal (str): The goal for the current work session.
        """
        self.is_running = True
        self.goal = goal
        # Store the initial work session with the goal in session_history
        self.session_history.append({"type": "Work", "timestamp": time.ctime(), "goal": self.goal})
        # Emit signal to update the history in the UI immediately
        self.session_change_signal.emit("Work")
        self.update_time()
    
        # Start the timer in a new thread
        with timer_lock:
            Thread(target=self.run_timer).start()


    def run_timer(self) -> None:
        """
        The timer's countdown logic, running in a separate thread.
        """
        with timer_lock:
            while self.current_time > 0 and self.is_running:
                time.sleep(1)
                self.current_time -= 1
                if self.current_time == 60 and not self.is_work_period:
                    self.notify_user_signal.emit()
                self.update_time()
            if self.current_time == 0 and self.is_running:
                self.finish_signal.emit()
                self.switch_period()

    def switch_period(self) -> None:
        """
        Basculer entre les périodes de travail et de pause, en mettant à jour le temps actuel en conséquence.
        Après chaque période de travail, un signal est émis pour réinitialiser l'objectif de l'utilisateur.
        """
        self.is_work_period = not self.is_work_period
        self.session_count += 1
        session_type = "Work" if self.is_work_period else "Break"
        self.session_history.append({"type": session_type, "timestamp": time.ctime(), "goal": self.goal})

        if not self.is_work_period:
            self.current_time = self.short_break_duration if self.session_count % 4 != 0 else self.long_break_duration
        else:
            self.current_time = self.work_duration

        self.update_time()

        if self.is_running:
            Thread(target=self.run_timer).start()

        self.session_change_signal.emit(session_type)

        if self.is_work_period:
            self.reset_goal_signal.emit()


    def update_time(self) -> None:
        """
        Émet le temps actuel et la fraction du temps écoulé comme signaux pour les mises à jour de l'interface utilisateur.
        """
        mins, secs = divmod(self.current_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        if self.is_work_period:
            time_fraction = (self.work_duration - self.current_time) / self.work_duration
        else:
            current_break_duration = self.short_break_duration if self.session_count % 4 != 0 else self.long_break_duration
            time_fraction = 1 - (self.current_time / current_break_duration)
        self.update_signal.emit(time_str, time_fraction)


    def format_duration(self, duration: int) -> str:
        """
        Formats a duration in seconds into a mm:ss string.

        Args:
            duration (int): Duration in seconds to format.

        Returns:
            str: The formatted duration as a mm:ss string.
        """
        mins, secs = divmod(duration, 60)
        return f"{mins:02d}:{secs:02d}"

