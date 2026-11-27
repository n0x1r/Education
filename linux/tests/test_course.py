import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from rooted.app import create_server, lesson_action
from rooted.curriculum import LESSONS, MODULES, public_curriculum
from rooted.simulator import Terminal, initial_state
from rooted.storage import Store

class CurriculumTests(unittest.TestCase):
    def test_content_and_all_guided_tasks(self):
        self.assertEqual(len(LESSONS),56)
        self.assertEqual(len({l['id'] for l in LESSONS}),56)
        self.assertEqual(sum(l['capstone'] for l in LESSONS),8)
        for module in MODULES:
            self.assertEqual(sum(l['module']==module[0] for l in LESSONS),7)
        for lesson in LESSONS:
            with self.subTest(lesson=lesson['id']):
                terminal=Terminal()
                self.assertGreaterEqual(len(lesson['sections']),2)
                for task in lesson['tasks']:
                    result=terminal.run(task['command'])
                    self.assertIn(result['status'],(0,1),msg=(task,result))
                self.assertEqual(len(lesson['questions']),2)
    def test_public_questions_hide_grading(self):
        for lesson in public_curriculum()['lessons']:
            for q in lesson['questions']:
                self.assertNotIn('answer',q)
                self.assertNotIn('explanation',q)

class SimulatorTests(unittest.TestCase):
    def test_virtual_paths_cannot_read_host(self):
        t=Terminal()
        for command in ('cat /etc/passwd','cat /proc/self/environ','sudo id','python3 -c "print(123)"','echo $(id)'):
            self.assertGreater(t.run(command)['status'],1)
        self.assertEqual(t.s['files'],initial_state()['files'])
    def test_pipeline_redirect_and_quoting(self):
        t=Terminal()
        self.assertEqual(t.run('grep ERROR logs/app.log | wc -l')['output'],'2\n')
        self.assertEqual(t.run("printf '%s\\n' 'hello world' > 'my notes.txt'")['status'],0)
        self.assertEqual(t.run('cat "my notes.txt"')['output'],'hello world\n')
        t.run("printf '%s\\n' 'second' >> 'my notes.txt'")
        self.assertEqual(t.run('cat "my notes.txt"')['output'],'hello world\nsecond\n')
        t.run('export TOPIC=Linux')
        self.assertEqual(t.run("echo '$TOPIC'")['output'],'$TOPIC\n')
        self.assertEqual(t.run('echo "$TOPIC"')['output'],'Linux\n')
    def test_hashes_and_modes(self):
        t=Terminal();t.run('cp notes.txt backup.txt')
        a=t.run('sha256sum notes.txt')['output'].split()[0]
        b=t.run('sha256sum backup.txt')['output'].split()[0]
        self.assertEqual(a,b)
        t.run('chmod 600 backup.txt');self.assertIn('(0600)',t.run('stat backup.txt')['output'])
        t.run('touch backup.txt');self.assertEqual(t.read('backup.txt'),t.read('notes.txt'))
    def test_failures_and_truncation(self):
        t=Terminal();self.assertEqual(t.run('grep MISSING notes.txt')['status'],1)
        self.assertEqual(t.run('echo $?')['output'],'1\n')
        self.assertEqual(t.run('cat notes.txt > notes.txt')['status'],0)
        self.assertEqual(t.read('notes.txt'),'')
        self.assertGreater(t.run("grep '(a+)+' names.txt")['status'],1)
    def test_git_snapshots_are_not_live_references(self):
        t=Terminal();t.run('git init');t.run('git add notes.txt')
        t.run("printf '%s\\n' changed > notes.txt")
        t.run('git commit -m "initial"')
        snapshot=t.s['git']['commits'][0]['snapshot']
        self.assertEqual(snapshot['/home/learner/notes.txt'],initial_state()['files']['/home/learner/notes.txt'])
        self.assertIn('changed:',t.run('git diff')['output'])
    def test_demo_rejects_modified_code(self):
        t=Terminal();t.run("echo 'arbitrary code' > scripts/analyze.py")
        self.assertGreater(t.run('python3 scripts/analyze.py')['status'],1)

class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'progress.sqlite3';self.store=Store(self.path)
    def tearDown(self): self.tmp.cleanup()
    def test_completion_requires_all_checkpoints_and_survives_restart(self):
        lesson=LESSONS[0];lid=lesson['id']
        with self.assertRaises(ValueError): lesson_action(self.store,lid,{'action':'complete'})
        for task in lesson['tasks']:lesson_action(self.store,lid,{'action':'terminal','command':task['command']})
        wrong=[(q['answer']+1)%3 for q in lesson['questions']]
        result=lesson_action(self.store,lid,{'action':'quiz','answers':wrong})
        self.assertFalse(result['result']['passed'])
        self.assertFalse(self.store.get(lid)['quiz_pass'])
        lesson_action(self.store,lid,{'action':'read'})
        lesson_action(self.store,lid,{'action':'note','notes':'A useful observation'})
        lesson_action(self.store,lid,{'action':'quiz','answers':[q['answer'] for q in lesson['questions']]})
        lesson_action(self.store,lid,{'action':'complete'})
        reopened=Store(self.path).get(lid)
        self.assertTrue(reopened['completed']);self.assertEqual(reopened['notes'],'A useful observation')
        self.assertEqual(reopened['attempts'],2)
        lesson_action(self.store,lid,{'action':'reset_lab'})
        self.assertTrue(self.store.get(lid)['completed'])
        self.assertEqual(self.store.get(lid)['lab']['done'],[])
    def test_invalid_quiz_rolls_back(self):
        with self.assertRaises(ValueError):lesson_action(self.store,LESSONS[0]['id'],{'action':'quiz','answers':[True,0]})
        self.assertEqual(self.store.all(),{})
    def test_every_lesson_can_complete_via_service(self):
        for lesson in LESSONS:
            lid=lesson['id']
            for task in lesson['tasks']: lesson_action(self.store,lid,{'action':'terminal','command':task['command']})
            lesson_action(self.store,lid,{'action':'read'})
            lesson_action(self.store,lid,{'action':'quiz','answers':[q['answer'] for q in lesson['questions']]})
            lesson_action(self.store,lid,{'action':'complete'})
        self.assertEqual(sum(s['completed'] for s in self.store.all().values()),56)

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.server=create_server(port=0,data_dir=self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.base=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def test_api_and_static_path_sandbox(self):
        with urllib.request.urlopen(self.base+'/api/course') as r:self.assertEqual(len(json.load(r)['lessons']),56)
        for path in ('/../app.py','/%2e%2e/app.py','/missing.js'):
            with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(self.base+path)
            self.assertEqual(caught.exception.code,404)
        with urllib.request.urlopen(self.base+'/original-guide.js') as r:self.assertIn(b'const D=',r.read())
    def test_cross_origin_and_form_writes_rejected(self):
        target=self.base+'/api/lesson/'+LESSONS[0]['id'];body=json.dumps({'action':'read'}).encode()
        for headers in ({'Content-Type':'application/json'},{'Content-Type':'application/json','X-Rooted-Client':'1','Origin':'https://untrusted.example'}):
            req=urllib.request.Request(target,data=body,headers=headers)
            with self.assertRaises(urllib.error.HTTPError) as caught:urllib.request.urlopen(req)
            self.assertEqual(caught.exception.code,403)
        req=urllib.request.Request(target,data=body,headers={'Content-Type':'application/json','X-Rooted-Client':'1','Origin':self.base})
        with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['state']['read'])

if __name__=='__main__':unittest.main()
