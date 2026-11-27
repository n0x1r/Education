"""Build the real Linux exercise pack; creation does not execute its examples."""
from io import BytesIO
from pathlib import Path
import zipfile
from .curriculum import LESSONS, MODULES
from .simulator import SEEDS


def build_pack():
    buffer=BytesIO()
    # The reference solution is also packaged inside rooted for pip installations.
    analyzer=Path(__file__).with_name('analyze_example.py').read_text()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('rooted-practice/README.txt','''ROOTED — REAL LINUX PRACTICE PACK

Extract into a NEW directory in a disposable Linux VM. This pack creates no
services, installs no packages and sends no traffic. You choose which real
commands to run. Paths inside this archive are relative to rooted-practice/.

Quick start (from rooted-practice/):
  python3 --version
  python3 analyze.py sample-data --log logs/app.log --output report.json
  cat report.json
  sha256sum sample-data/notes.txt

analyze.py is a runnable Python reference solution for the final project. It
uses only the standard library, streams file hashes and logs, skips symlinks,
records per-file read errors and refuses existing output unless --force is
explicitly supplied. It refuses replacing existing input files even with force.
It is a learning example, not a validated forensic acquisition tool. Input
files changing during a scan can make a report inconsistent; use stable copies.

A successful report has complete=true and returns exit status 0. An input or
output error, invalid UTF-8 log or partial file read produces exit status 2.
No arbitrary shell command or network request is executed by analyze.py.

worksheets/ contains all 56 lesson exercises in module order. Most commands
use standard GNU/Linux tools; apt examples target Debian/Ubuntu, and service
examples require systemd. Package names and permissions vary by distribution.
The app does not automatically grade these independent exercises.

sample-data contains only synthetic TEXT fixtures. Files named photo.jpg,
sample.pcap and sample.tar in the simulator are not real binary files; they are
omitted here. Obtain a trusted training image or capture for actual parsers.
Use chmod, cp and other mutations only on your disposable extracted copies.
Record your command, prediction, result and explanation for each exercise.
''')
        archive.writestr('rooted-practice/analyze.py',analyzer)
        for name,value in SEEDS.items():
            if name.startswith('/') or name in ('photo.jpg','sample.pcap','sample.tar'):continue
            archive.writestr('rooted-practice/sample-data/'+name,value)
        for i,module in enumerate(MODULES,1):
            text=f'{i:02d}. {module[1]}\n'+('='*60)+'\n\n'
            for lesson in LESSONS:
                if lesson['module']!=module[0]:continue
                text+=lesson['title']+'\n'+'-'*len(lesson['title'])+'\n'+lesson['summary']+'\n\n'
                for section in lesson['sections']:text+=section['title']+'\n'+section['text']+'\n\n'
                text+='REFERENCE COMMANDS (adapt to your own disposable VM paths):\n'+lesson['example']+'\n\n'
                text+='INDEPENDENT EXERCISE:\n'+lesson['real_practice']+'\n\n'
                text+='SELF-CHECK:\n'
                for question in lesson['questions']:
                    text+=question['prompt']+'\nAnswer: '+question['options'][question['answer']]+'\nWhy: '+question['explanation']+'\n\n'
                text+='LAB NOTES:\nPrediction:\nCommand or code:\nObserved result:\nExplanation:\nLimitations / next question:\n\n'
            archive.writestr(f'rooted-practice/worksheets/{i:02d}-{module[0]}.txt',text)
    return buffer.getvalue()
