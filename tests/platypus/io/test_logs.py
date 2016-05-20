import platypus.io.logs
import os
from unittest import TestCase

TEST_LOG_V4_0_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'airboat_20130807_063622.txt')

TEST_LOG_V4_0_0_SENSOR_FILENAME = os.path.join(
    os.path.dirname(__file__), 'airboat_20151220_043848.txt')

TEST_LOG_V4_1_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'platypus_20160426_024734.txt')

TEST_LOG_V4_2_0_FILENAME = os.path.join(
    os.path.dirname(__file__), 'platypus_20160519_013623.txt')


class LogsTest(TestCase):
    def test_load(self):
        """ Test auto-sensing version of log loader. """
        platypus.io.logs.load(TEST_LOG_V4_0_0_FILENAME)
        platypus.io.logs.load(TEST_LOG_V4_1_0_FILENAME)
        platypus.io.logs.load(TEST_LOG_V4_2_0_FILENAME)

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

    def test_read_v4_0_0_sensor(self):
        """ Test reading a v4.0.0 logfile with sensors. """
        import numpy

        with open(TEST_LOG_V4_0_0_SENSOR_FILENAME) as log_file:
            log_v4_0_0_str = log_file.readlines()
        log_v4_0_0 = platypus.io.logs.read(
            log_v4_0_0_str, filename=TEST_LOG_V4_0_0_SENSOR_FILENAME)

        # Test that the correct battery sensor entries were loaded.
        self.assertTrue(numpy.allclose(
            log_v4_0_0['battery'].as_matrix(),
            numpy.array([[12.463, 9045.454102, 0.],
                         [12.463, 0., 15.151515]])
        ))

        # Test that the correct atlas_do sensor entries were loaded.
        self.assertTrue(numpy.allclose(
            log_v4_0_0['atlas_do'].as_matrix(),
            numpy.array([[7.78]])
        ))

        # Test that the correct pose entries were loaded.
        self.assertEqual(log_v4_0_0['pose'].shape, (15, 7))
        self.assertAlmostEqual(log_v4_0_0['pose']['longitude'][0],
                               -81.2833044)
        self.assertAlmostEqual(log_v4_0_0['pose']['latitude'][0],
                               42.1927325)
        self.assertAlmostEqual(log_v4_0_0['pose']['longitude'][-1],
                               -81.2833041)
        self.assertAlmostEqual(log_v4_0_0['pose']['latitude'][-1],
                               42.1927343)

    def test_read_v4_1_0(self):
        """ Test reading a v4.1.0 logfile. """
        with open(TEST_LOG_V4_1_0_FILENAME) as log_file:
            log_str = log_file.readlines()
        log = platypus.io.logs.read_v4_1_0(log_str)

        # Test that the correct battery sensor entries were loaded.
        self.assertEqual(log['BATTERY'].shape, (12, 3))
        self.assertAlmostEqual(log['BATTERY'].as_matrix()[0, 0], 15.263)
        self.assertAlmostEqual(log['BATTERY'].as_matrix()[-1, 0], 15.015)

        # Test that the correct atlas sensor entries were loaded.
        self.assertEqual(log['ATLAS_PH'].shape, (11, 1))
        self.assertAlmostEqual(log['ATLAS_PH'].as_matrix()[0, 0], 7.054)
        self.assertAlmostEqual(log['ATLAS_PH'].as_matrix()[-1, 0], 6.7)

        self.assertEqual(log['ATLAS_DO'].shape, (21, 1))
        self.assertAlmostEqual(log['ATLAS_DO'].as_matrix()[0, 0], 10.15)
        self.assertAlmostEqual(log['ATLAS_DO'].as_matrix()[-1, 0], 10.56)

        # Test that the correct pose entries were loaded.
        self.assertEqual(log['pose'].shape, (211, 7))
        self.assertAlmostEqual(log['pose']['easting'][0], 337185.1208144073)
        self.assertAlmostEqual(log['pose']['northing'][0], 4467663.6643868135)
        self.assertAlmostEqual(log['pose']['easting'][-1], 337679.211030486)
        self.assertAlmostEqual(log['pose']['northing'][-1], 4467651.475327312)

    def test_read_v4_2_0(self):
        """ Test reading a v4.2.0 logfile. """
        with open(TEST_LOG_V4_2_0_FILENAME) as log_file:
            log_str = log_file.readlines()
        log = platypus.io.logs.read_v4_2_0(log_str)

        # Test that the correct battery sensor entries were loaded.
        self.assertEqual(log['BATTERY'].shape, (46, 3))
        self.assertAlmostEqual(log['BATTERY'].as_matrix()[0, 0], 17.075)
        self.assertAlmostEqual(log['BATTERY'].as_matrix()[-1, 0], 17.048)

        # Test that the correct atlas sensor entries were loaded.
        self.assertEqual(log['ATLAS_PH'].shape, (10, 1))
        self.assertAlmostEqual(log['ATLAS_PH'].as_matrix()[0, 0], 4.473)
        self.assertAlmostEqual(log['ATLAS_PH'].as_matrix()[-1, 0], 4.448)

        self.assertEqual(log['ATLAS_DO'].shape, (14, 1))
        self.assertAlmostEqual(log['ATLAS_DO'].as_matrix()[0, 0], 7.49)
        self.assertAlmostEqual(log['ATLAS_DO'].as_matrix()[-1, 0], 7.47)

        # Test that the correct pose entries were loaded.
        self.assertEqual(log['pose'].shape, (571, 7))
        self.assertAlmostEqual(log['pose']['easting'][0], 592295.4032107397),
        self.assertAlmostEqual(log['pose']['northing'][0], 4481766.791869606)
        self.assertAlmostEqual(log['pose']['easting'][-1], 592300.9984074512)
        self.assertAlmostEqual(log['pose']['northing'][-1], 4481762.477492471),
