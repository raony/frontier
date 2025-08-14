from datetime import datetime

from evennia.utils.test_resources import EvenniaTest

from world.time_service import GameTimeService


class FakeSettings:
    TIME_FACTOR = 6.0
    TIME_UNITS = {
        "sec": 1,
        "min": 60,
        "hour": 3600,
        "day": 86400,
        "month": 2592000,
        "year": 31104000,
    }


class TestGameTimeService(EvenniaTest):
    def test_to_custom_seconds_monotonic(self):
        svc = GameTimeService(FakeSettings(), now_provider=lambda: 0.0)
        a = svc.to_custom_seconds(2025, 8, 12, 5, 59, 0)
        b = svc.to_custom_seconds(2025, 8, 12, 6, 0, 0)
        self.assertLess(a, b)

    def test_compute_epoch_from_desired_gregorian(self):
        # Fix real_now to a known value for determinism
        fixed_real = 1_755_141_162.0  # from debug example
        svc = GameTimeService(FakeSettings(), now_provider=lambda: fixed_real)
        desired = datetime(2025, 8, 13, 5, 55, 0)
        epoch = svc.compute_epoch_from_desired_gregorian(desired)
        # Validate inverse relation: epoch + real_now*TF == desired_unix
        desired_unix = int(desired.timestamp())
        reconstructed = int(epoch + fixed_real * FakeSettings().TIME_FACTOR)
        self.assertEqual(reconstructed, desired_unix)

    def test_compute_epoch_from_desired_using_runtime(self):
        # Given a runtime anchor, verify inverse identity holds
        fixed_runtime = 100_000.0
        svc = GameTimeService(FakeSettings(), now_provider=lambda: 0.0, runtime_provider=lambda: fixed_runtime)
        desired = datetime(2025, 8, 13, 22, 0, 0)
        epoch = svc.compute_epoch_from_desired_using_runtime(desired)
        desired_unix = int(desired.timestamp())
        reconstructed = int(epoch + fixed_runtime * FakeSettings().TIME_FACTOR)
        self.assertEqual(reconstructed, desired_unix)

    def test_compute_epoch_shift_same_day_time(self):
        svc = GameTimeService(FakeSettings(), now_provider=lambda: 0.0)
        current = (2025, 8, 12, 5, 50, 0)
        target_time = (6, 0, 0)
        delta = svc.compute_epoch_shift_same_day_time(current, target_time)
        # 10 minutes of in-game time at 6x -> 100 real seconds / 6 = ~100? Wait: 10 min = 600s game, /6 = 100 real
        self.assertEqual(delta, int((10 * 60) / FakeSettings().TIME_FACTOR))
