"""
Tests for the PomodoroEngine (core timer logic).

Run with:  python -m pytest 1.pomodoro/test_timer.py -v
or:        python 1.pomodoro/test_timer.py
"""

import sys
import os
import time
import threading
import unittest

# Allow importing app.py without tkinter by mocking the module
import unittest.mock as mock

# Provide a minimal tkinter stub so the module-level import succeeds in
# environments where tkinter is not installed (e.g., CI).
_tk_stub = mock.MagicMock()
sys.modules.setdefault("tkinter", _tk_stub)
sys.modules.setdefault("tkinter.ttk", _tk_stub)
sys.modules.setdefault("tkinter.font", _tk_stub)

# Now we can safely import the engine
sys.path.insert(0, os.path.dirname(__file__))
from app import PomodoroEngine, SESSION_WORK, SESSION_BREAK, WORK_TIMES, BREAK_TIMES


class TestPomodoroEngineInitialization(unittest.TestCase):
    def test_default_values(self):
        engine = PomodoroEngine()
        self.assertEqual(engine.work_minutes, 25)
        self.assertEqual(engine.break_minutes, 5)
        self.assertEqual(engine.time_remaining, 25 * 60)
        self.assertEqual(engine.session_type, SESSION_WORK)
        self.assertFalse(engine.running)

    def test_custom_initialization(self):
        engine = PomodoroEngine(work_minutes=15, break_minutes=10)
        self.assertEqual(engine.work_minutes, 15)
        self.assertEqual(engine.break_minutes, 10)
        self.assertEqual(engine.time_remaining, 15 * 60)

    def test_all_work_times_are_valid(self):
        for minutes in WORK_TIMES:
            engine = PomodoroEngine(work_minutes=minutes)
            self.assertEqual(engine.time_remaining, minutes * 60)

    def test_all_break_times_are_valid(self):
        for minutes in BREAK_TIMES:
            engine = PomodoroEngine(break_minutes=minutes)
            self.assertEqual(engine.break_minutes, minutes)


class TestPomodoroEngineSettings(unittest.TestCase):
    def test_set_work_time_when_idle(self):
        engine = PomodoroEngine(work_minutes=25)
        engine.set_work_time(15)
        self.assertEqual(engine.work_minutes, 15)
        self.assertEqual(engine.time_remaining, 15 * 60)

    def test_set_work_time_does_not_change_display_during_break(self):
        engine = PomodoroEngine(work_minutes=25, break_minutes=5)
        engine.session_type = SESSION_BREAK
        engine.time_remaining = 5 * 60
        engine.set_work_time(35)
        # Break session still shows break time
        self.assertEqual(engine.time_remaining, 5 * 60)
        self.assertEqual(engine.work_minutes, 35)

    def test_set_break_time_when_idle(self):
        engine = PomodoroEngine(break_minutes=5)
        engine.set_break_time(10)
        self.assertEqual(engine.break_minutes, 10)

    def test_set_break_time_updates_display_during_break(self):
        engine = PomodoroEngine(break_minutes=5)
        engine.session_type = SESSION_BREAK
        engine.time_remaining = 5 * 60
        engine.set_break_time(15)
        self.assertEqual(engine.time_remaining, 15 * 60)


class TestPomodoroEngineReset(unittest.TestCase):
    def test_reset_restores_work_session(self):
        engine = PomodoroEngine(work_minutes=25, break_minutes=5)
        engine.session_type = SESSION_BREAK
        engine.time_remaining = 3 * 60
        engine.reset()
        self.assertEqual(engine.session_type, SESSION_WORK)
        self.assertEqual(engine.time_remaining, 25 * 60)
        self.assertFalse(engine.running)

    def test_reset_calls_callback(self):
        engine = PomodoroEngine()
        callback = mock.Mock()
        engine.on_reset = callback
        engine.reset()
        callback.assert_called_once()


class TestPomodoroEngineSessionSwitch(unittest.TestCase):
    def test_switch_from_work_to_break(self):
        engine = PomodoroEngine(work_minutes=25, break_minutes=5)
        engine._switch_session()
        self.assertEqual(engine.session_type, SESSION_BREAK)
        self.assertEqual(engine.time_remaining, 5 * 60)

    def test_switch_from_break_to_work(self):
        engine = PomodoroEngine(work_minutes=25, break_minutes=5)
        engine.session_type = SESSION_BREAK
        engine._switch_session()
        self.assertEqual(engine.session_type, SESSION_WORK)
        self.assertEqual(engine.time_remaining, 25 * 60)

    def test_switch_uses_current_work_setting(self):
        engine = PomodoroEngine(work_minutes=25, break_minutes=5)
        engine.work_minutes = 45  # user changed work time
        engine.session_type = SESSION_BREAK
        engine._switch_session()
        self.assertEqual(engine.time_remaining, 45 * 60)


class TestPomodoroEngineRunning(unittest.TestCase):
    def test_start_sets_running(self):
        engine = PomodoroEngine(work_minutes=1)
        on_start = mock.Mock()
        engine.on_start = on_start
        engine.start()
        self.assertTrue(engine.running)
        engine.pause()  # clean up
        on_start.assert_called_once_with(SESSION_WORK)

    def test_pause_stops_running(self):
        engine = PomodoroEngine(work_minutes=1)
        engine.start()
        engine.pause()
        self.assertFalse(engine.running)

    def test_start_ignored_when_already_running(self):
        engine = PomodoroEngine(work_minutes=1)
        on_start = mock.Mock()
        engine.on_start = on_start
        engine.start()
        engine.start()  # second call should be a no-op
        engine.pause()
        on_start.assert_called_once()  # only fired once

    def test_tick_callback_fires(self):
        engine = PomodoroEngine(work_minutes=1)
        ticks = []
        engine.on_tick = ticks.append
        engine.start()
        time.sleep(2.5)
        engine.pause()
        self.assertGreaterEqual(len(ticks), 1)

    def test_session_end_callback_and_switch(self):
        engine = PomodoroEngine(work_minutes=1, break_minutes=1)
        engine.time_remaining = 1  # fast-forward
        ended = threading.Event()
        received = []

        def on_end(nxt):
            received.append(nxt)
            ended.set()

        engine.on_session_end = on_end
        engine.start()
        ended.wait(timeout=5)
        self.assertTrue(ended.is_set(), "session_end callback was not called")
        self.assertEqual(received[0], SESSION_BREAK)
        self.assertEqual(engine.session_type, SESSION_BREAK)


class TestWorkAndBreakTimeConstants(unittest.TestCase):
    def test_work_time_options(self):
        self.assertEqual(WORK_TIMES, [15, 25, 35, 45])

    def test_break_time_options(self):
        self.assertEqual(BREAK_TIMES, [5, 10, 15])


if __name__ == "__main__":
    unittest.main(verbosity=2)
