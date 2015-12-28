import platypus.io.logs
import os
from unittest import TestCase

TEST_LOG_V4_0_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'airboat_20130807_063622.txt')

TEST_LOG_V4_2_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'airboat_20151220_043848.txt')


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

    def test_read_v4_0_0(self):
        """ Test reading a v4.0.0 logfile. """
        with open(TEST_LOG_V4_0_0_FILENAME) as log_file:
            log_v4_0_0_str = log_file.readlines()
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

    def test_read_v4_2_0(self):
        """ Test reading a v4.2.0 logfile. """
        import numpy

        with open(TEST_LOG_V4_2_0_FILENAME) as log_file:
            log_v4_2_0_str = log_file.readlines()
        log_v4_2_0 = platypus.io.logs.read(
            log_v4_2_0_str, filename=TEST_LOG_V4_2_0_FILENAME)

        # Test that the correct battery sensor entries were loaded.
        self.assertTrue(numpy.allclose(
            log_v4_2_0['battery'].as_matrix(),
            numpy.array([[12.463, 9045.454102, 0.],
                         [12.463, 0.,          15.151515]])
        ))

        # Test that the correct atlas_do sensor entries were loaded.
        self.assertTrue(numpy.allclose(
            log_v4_2_0['atlas_do'].as_matrix(),
            numpy.array([[7.78]])
        ))

        # Test that the correct pose entries were loaded.
        self.assertEqual(log_v4_2_0['pose'].shape, (15, 7))
        self.assertAlmostEqual(log_v4_2_0['pose']['longitude'][0],
                               -81.283304250310977)
        self.assertAlmostEqual(log_v4_2_0['pose']['latitude'][0],
                               42.192733443703723)
        self.assertAlmostEqual(log_v4_2_0['pose']['longitude'][-1],
                               -81.2833041314601)
        self.assertAlmostEqual(log_v4_2_0['pose']['latitude'][-1],
                               42.192734344628192)
