"""Optional browser verification: pip install playwright && playwright install chromium.
Run from linux/: python3 tests/browser_check.py. Not required to use the app.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import tempfile
import shutil
import threading
from playwright.sync_api import sync_playwright
from rooted.app import create_server
from rooted.curriculum import LESSONS

with tempfile.TemporaryDirectory() as directory:
    server=create_server(port=0,data_dir=directory)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=shutil.which("chromium"))
            page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(base);page.get_by_role('heading',name='Make yourself at home in Linux.').wait_for()
            assert page.locator('.module-card').count()==8
            screenshot=Path('/workspace/rooted-overview.png')
            page.screenshot(path=str(screenshot),full_page=True)
            page.screenshot(path="/workspace/rooted-preview.png",full_page=False)
            page.get_by_role('link',name='Begin your journey').click()
            page.get_by_role('heading',name='Meet your operating system').wait_for()
            page.get_by_role('button',name='Save for later').click()
            page.get_by_role('button',name='Saved lesson').wait_for()
            page.get_by_label('Lesson notes').fill('A kernel and a distribution are different. <script>throw Error("unsafe")</script>')
            page.wait_for_function("() => document.querySelector('#note-status').textContent.startsWith('Saved locally')")
            page.get_by_role('button',name='Mark understood & practice').click()
            page.get_by_label('Terminal command').wait_for()
            for task in LESSONS[0]['tasks']:
                page.get_by_label('Terminal command').fill(task['command'])
                page.get_by_role('button',name='Run',exact=True).click()
                page.wait_for_function("() => document.querySelector('#terminal-input').value === ''")
            assert page.locator('.task.done').count()==2
            page.reload();page.get_by_label('Terminal command').wait_for();assert page.locator('.task.done').count()==2
            page.get_by_role('link',name='Open knowledge check').click()
            for i,q in enumerate(LESSONS[0]['questions']):page.locator(f'input[name="q{i}"][value="{q["answer"]}"]').check()
            page.get_by_role('button',name='Check my answers').click()
            page.get_by_role('heading',name='Knowledge check passed.').wait_for()
            page.get_by_role('button',name='Complete lesson',exact=True).click()
            page.get_by_role('heading',name='One more skill, rooted.').wait_for()
            page.goto(base+'/#/progress');page.get_by_role('heading',name='Look how far you’re growing.').wait_for()
            assert page.locator('.stat strong').first.inner_text()=='1/56'
            page.goto(base+'/#/reference/glossary');page.get_by_label('Search reference').wait_for()
            page.get_by_label('Search reference').fill('Kernel')
            assert page.locator('.reference-card').count()>0
            assert page.locator('.reference-card').first.locator('h3').inner_text()!='0'
            page.goto(base+'/#/notes');page.get_by_role('heading',name='My notebook',exact=True).wait_for()
            assert '<script>' in page.locator('.saved-note p').inner_text()
            page.goto(base+'/#/bookmarks');page.get_by_role('heading',name='Saved for another look.').wait_for();assert page.locator('.lesson-row').count()==1
            page.get_by_label('Search lessons',exact=True).fill('Python')
            page.get_by_label('Search lessons',exact=True).press('Enter')
            page.get_by_label('Filter lessons').wait_for();assert page.get_by_label('Filter lessons').input_value()=='Python'
            assert page.locator('.lesson-row').count()>0
            page.goto(base+'/#/tools/permissions');page.get_by_label('Three-digit mode').fill('600')
            page.get_by_role('button',name='Explore this input').click()
            page.get_by_role('heading',name='What chmod 600 means').wait_for()
            assert '-rw-------' in page.locator('#concept-result').inner_text()
            page.goto(base+'/#/tools/subnet');page.get_by_label('IPv4 or IPv6 network').fill('192.0.2.2/31')
            page.get_by_role('button',name='Explore this input').click()
            page.get_by_role('cell',name='192.0.2.2/31',exact=True).wait_for()
            page.goto(base+'/#/tools/hash');page.get_by_role('heading',name='Small input change, different fingerprint').wait_for()
            page.goto(base+'/#/dashboard');page.get_by_role('heading',name='Make yourself at home in Linux.').wait_for()
            with page.expect_download() as download:
                page.get_by_role('link',name='Download VM practice pack').click()
            assert download.value.suggested_filename=='rooted-linux-practice.zip'
            page.goto(base+'/original-guide.html');page.locator('#cmdlist .tile').first.wait_for();assert page.locator('#cmdlist .tile').count()==104
            page.goto(base+'/#/dashboard');page.get_by_role('heading',name='Make yourself at home in Linux.').wait_for()
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('() => document.documentElement.scrollWidth<=window.innerWidth')
            page.get_by_role('button',name='Toggle navigation').click();assert 'menu-open' in page.locator('body').get_attribute('class')
            page.get_by_role('link',name='Command library',exact=True).click();page.get_by_label('Search reference').wait_for()
            assert page.evaluate('() => document.documentElement.scrollWidth<=window.innerWidth')
            assert not errors,errors
            browser.close()
            print('Browser passed: dashboard, guided lab, reload persistence, quiz grading, completion, notes/XSS, bookmarks, global search, glossary, original guide, 390px mobile layout, concept calculators and practice-pack download. Screenshot:',screenshot)
    finally:
        server.shutdown();server.server_close();thread.join()
