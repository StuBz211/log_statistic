import unittest

import log_statistic


class TestLogStatistic(unittest.TestCase):
    def setUp(self):
        self.file = open('test_file')
        self.ls = log_statistic.LogStatisticParse(self.file)

    def tearDown(self):
        pass

    def test_file(self):
        self.assertTrue(hasattr(self.file, 'readlines'))

    def test_extract_task_id(self):
        lines = [
            '7DABFDF0519: from=<krasteplokomplekt@yandex.ru>, size=617938, nrcpt=1 (queue active)',
            'warning: 178.140.204.161: hostname broadband-178-140-204-161.nationalcablenetworks.ru verification',
            'connect from unknown[178.140.204.161]',
            'lost connection after AUTH from unknown[61.141.72.43]',
            'B8B04DF04FC: from=<kvadrat5@abama-sprint.ru>, size=441137, nrcpt=3 (queue active)',
            'ABFDF0519: to=<arta_krsk@mail.ru>, relay=mxs.mail.ru[94.100.176.20]:25,',
            '43695DF050B'
        ]

        self.assertEqual(self.ls._extract_task_id(lines[0]), '7DABFDF0519')
        self.assertEqual(self.ls._extract_task_id(lines[1]), None)
        self.assertEqual(self.ls._extract_task_id(lines[2]), None)
        self.assertEqual(self.ls._extract_task_id(lines[3]), None)
        self.assertEqual(self.ls._extract_task_id(lines[4]), 'B8B04DF04FC')
        self.assertEqual(self.ls._extract_task_id(lines[5]), None)
        self.assertEqual(self.ls._extract_task_id(lines[6]), '43695DF050B')

    def test_extract_email(self):
        lines = ['connect from unknown[61.141.72.43]',
                 'EFA03DF0506: message-id=<20120710061219.EFA03DF0506@smtp.jino.ru>',
                 'lost connection after AUTH from unknown[113.17.23.97]',
                 'disconnect from unknown[113.17.23.97] ',
                 'EFA03DF0506: from=<>, size=9301, nrcpt=1 (queue active)',
                 '67BDBDF0503: sender non-delivery notification: EFA03DF0506',
                 'EFA03DF0506: to=<info@auraltc.ru>, relay=mail.auraltc.ru[217.107.34.202]:25',
                 'warning: unknown[178.140.204.161]: SASL LOGIN authentication failed: UGFzc3dvcmQ6',
                 'disconnect from unknown[178.140.204.161]',
                 'sasl_method=CRAM-MD5, sasl_username=a.bezusov@midglengroup.ru',
                 'from=<info@lsst.ru>, size=1386940, nrcpt=1 (queue active)',
                 'to=<volkova@lsst.ru>, relay=mail.lsst.ru[81.177.140.163]:25',
        ]

        self.assertEqual(self.ls._extract_email(lines[0]), None)
        self.assertEqual(self.ls._extract_email(lines[1]), '20120710061219.EFA03DF0506@smtp.jino.ru')
        self.assertEqual(self.ls._extract_email(lines[2]), None)
        self.assertEqual(self.ls._extract_email(lines[3]), None)
        self.assertEqual(self.ls._extract_email(lines[4]), None)
        self.assertEqual(self.ls._extract_email(lines[5]), None)
        self.assertEqual(self.ls._extract_email(lines[6]), 'info@auraltc.ru')
        self.assertEqual(self.ls._extract_email(lines[7]), None)
        self.assertEqual(self.ls._extract_email(lines[8]), None)
        self.assertEqual(self.ls._extract_email(lines[9]), 'a.bezusov@midglengroup.ru')
        self.assertEqual(self.ls._extract_email(lines[10]), 'info@lsst.ru')
        self.assertEqual(self.ls._extract_email(lines[11]), 'volkova@lsst.ru')

    def test_work_status(self):
        self.ls.parse()
        result = self.ls.work_statistic
        self.assertEqual(result['success'], 7)
        self.assertEqual(result['unsuccess'], 2)

    def test_collect_mail_activity(self):
        self.ls.parse()
        res = self.ls.users_statistic
        self.assertEqual(res['tduds@webmess.ru'], 1)
        self.assertEqual(res['krasnova@fbmse.msk.ru'], 2)
        self.assertEqual(res['tduds@wmess.ru'], 1)
        self.assertEqual(res['info@lsst.ru'], 1)
