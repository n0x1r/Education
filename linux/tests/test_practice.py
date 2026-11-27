import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from rooted.workbook import build_pack

class RealPracticeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.zip=zipfile.ZipFile(io.BytesIO(build_pack()))
        self.zip.extractall(self.root);self.pack=self.root/'rooted-practice'
    def tearDown(self):self.zip.close();self.tmp.cleanup()
    def run_cli(self,*extra):
        return subprocess.run([sys.executable,str(self.pack/'analyze.py'),str(self.pack/'sample-data'),'--output',str(self.root/'report.json'),*extra],text=True,capture_output=True,timeout=10)
    def test_pack_paths_and_worksheets(self):
        self.assertTrue(all(name.startswith('rooted-practice/') and '..' not in Path(name).parts for name in self.zip.namelist()))
        self.assertEqual(len(list((self.pack/'worksheets').glob('*.txt'))),8)
        self.assertFalse((self.pack/'sample-data/sample.pcap').exists())
    def test_real_analyzer_and_output_protection(self):
        first=self.run_cli();self.assertEqual(first.returncode,0,first.stderr)
        output=self.root/'report.json';original=output.read_bytes();report=json.loads(original)
        self.assertEqual(report['log']['error_records'],2);self.assertTrue(report['complete'])
        self.assertTrue(all(len(row['sha256'])==64 for row in report['files']))
        self.assertEqual(self.run_cli().returncode,2);self.assertEqual(output.read_bytes(),original)
        self.assertEqual(self.run_cli('--force').returncode,0);self.assertEqual(output.read_bytes(),original)
    def test_missing_input_and_invalid_utf8_fail_without_report(self):
        self.assertEqual(self.run_cli('--log','missing.txt').returncode,2)
        self.assertFalse((self.root/'report.json').exists())
        (self.pack/'sample-data/logs/app.log').write_bytes(b'\xff')
        self.assertEqual(self.run_cli().returncode,2);self.assertFalse((self.root/'report.json').exists())
    def test_existing_source_never_replaced(self):
        source=self.pack/'sample-data/notes.txt';original=source.read_bytes()
        result=subprocess.run([sys.executable,str(self.pack/'analyze.py'),str(self.pack/'sample-data'),'--output',str(source),'--force'],capture_output=True,timeout=10)
        self.assertEqual(result.returncode,2);self.assertEqual(source.read_bytes(),original)
    def test_symlink_directory_is_skipped(self):
        outside=self.root/'outside';outside.mkdir();(outside/'hidden.txt').write_text('do not collect')
        (self.pack/'sample-data/linked').symlink_to(outside,target_is_directory=True)
        self.assertEqual(self.run_cli().returncode,0)
        report=json.loads((self.root/'report.json').read_text())
        self.assertFalse(any('linked' in row['path'] for row in report['files']))

if __name__=='__main__':unittest.main()
