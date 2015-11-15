import platypus.io.logs
import os
from unittest import TestCase

TEST_LOG_V4_0_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'airboat_20130807_063622.txt')


class LogsTest(TestCase):
    def test_load(self):
        log_v4_0_0 = platypus.io.logs.load(TEST_LOG_V4_0_0_FILENAME)

        # Test that the correct ES2 entries were loaded.
        self.assertEqual(log_v4_0_0['es2'].shape, (22, 2))
        self.assertEqual(log_v4_0_0['es2']['temperature'][-1], 10.0)
        self.assertEqual(log_v4_0_0['es2']['ec'][-1], 9.0)

        # Test that the correct number of pose entries were loaded.
        self.assertEqual(log_v4_0_0['pose'].shape, (95, 7))
        self.assertAlmostEqual(log_v4_0_0['pose']['longitude'][-1],
                               -79.917394651365555)
        self.assertAlmostEqual(log_v4_0_0['pose']['latitude'][-1],
                               40.490316940191633)

    def test_read(self):
        log_v4_0_0_str = open(TEST_LOG_V4_0_0_FILENAME).readlines()
        log_v4_0_0 = platypus.io.logs.read(
            log_v4_0_0_str, filename=TEST_LOG_V4_0_0_FILENAME)

        # Test that the correct number of ES2 entries were loaded.
        self.assertEqual(log_v4_0_0['es2'].shape, (22, 2))
        self.assertEqual(log_v4_0_0['es2']['temperature'][-1], 10.0)
        self.assertEqual(log_v4_0_0['es2']['ec'][-1], 9.0)

        # Test that the correct pose entries were loaded.
        self.assertEqual(log_v4_0_0['pose'].shape, (95, 7))
        self.assertAlmostEqual(log_v4_0_0['pose']['longitude'][-1],
                               -79.917394651365555)
        self.assertAlmostEqual(log_v4_0_0['pose']['latitude'][-1],
                               40.490316940191633)
