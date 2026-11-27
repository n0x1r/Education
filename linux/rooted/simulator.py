"""Bounded virtual terminal. No host commands, host paths, sockets, eval or exec."""
import fnmatch
import hashlib
import json
import posixpath
import re
import shlex

HOME = '/home/learner'
BASH_REPORT = '''#!/usr/bin/env bash
set -u
log="${1:-logs/app.log}"
if [[ ! -r "$log" ]]; then
  printf 'Unreadable input: %s\\n' "$log" >&2
  exit 2
fi
grep 'ERROR' "$log"  # grep returns 1 when there are no matches
'''
BASH_CHECK = '''#!/usr/bin/env bash
for path in "$@"; do
  if [[ -f "$path" && -r "$path" ]]; then
    printf 'readable: %s\\n' "$path"
  else
    printf 'not a readable file: %s\\n' "$path" >&2
  fi
done
'''
PYTHON_SCRIPT = '''#!/usr/bin/env python3
"""Run from the lab/project root; requires Python 3.10+."""
import json
from pathlib import Path

source = Path("logs/app.log")
try:
    lines = source.read_text(encoding="utf-8").splitlines()
except (OSError, UnicodeError) as error:
    raise SystemExit(f"Cannot read {source}: {error}") from error
report = {"schema_version": 1, "input": str(source),
          "lines": len(lines), "errors": sum("ERROR" in line for line in lines)}
Path("report.json").write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(report, indent=2))
'''
SEEDS = {
    '/etc/os-release': 'NAME="Rooted Training Linux"\nVERSION="1.0 (Teaching fixture)"\nID=rooted\n',
    '/etc/hosts': '127.0.0.1 localhost\n192.0.2.10 lab-host\n',
    'notes.txt': 'hello Linux\npractice log\n', '.welcome': 'A simulated home directory. Nothing here is a host file.\n',
    'logs/app.log': '2026-01-15T10:00:00Z INFO service started\n2026-01-15T10:01:00Z ERROR database timeout\n2026-01-15T10:02:00Z INFO retry started\n2026-01-15T10:03:00Z ERROR retry exhausted\n2026-01-15T10:04:00Z INFO health check passed\n',
    'logs/auth.log': '2026-01-15T09:59:00Z Failed password for learner from 192.0.2.20\n2026-01-15T10:00:00Z Failed password for learner from 192.0.2.20\n2026-01-15T10:02:00Z Accepted publickey for learner from 192.0.2.20\n',
    'names.txt': 'Ada\nLinus\nAda\nGrace\nLinus\n',
    'data.csv': 'name,role\nAda,analyst\nLinus,admin\nGrace,analyst\n',
    'inventory.json': '{"host":"lab-host","os":"Linux","services":["nginx","ssh"]}\n',
    'case/evidence.txt': 'SYNTHETIC EVIDENCE ITEM E-001\nObservation: application reported two timeouts.\nNo real person or incident is represented.\n',
    'case/custody.txt': 'Item E-001 | synthetic teaching text\n2026-01-15T11:00:00Z | training custodian | fixture created\n2026-01-15T11:01:00Z | learner | assigned verified-copy exercise\nStorage: virtual lab only. Record subsequent handling in your lesson notes.\n',
    'case/scope.txt': 'Authorized scope: this simulated lab only.\nMethods: read fixtures, create virtual working copies, inspect modes.\nExcluded: external hosts, real credentials, host disks.\nDeliverable: observations, limitations and a retest plan.\n',
    'case/findings.txt': 'F-001 | Notes readable by other virtual users (mode 644).\nImpact depends on file sensitivity and account context.\nValidate with ls -l; use 600 if owner-only access is required.\n',
    'case/remediation.txt': 'Restrict notes.txt to owner read/write using chmod 600.\nVerify the mode with stat and test intended access on a disposable VM.\nThis control does not encrypt the file or constrain root.\n',
    'case/timeline.csv': 'time_utc,source,observation\n2026-01-15T09:59:00Z,auth.log,failed login\n2026-01-15T10:01:00Z,app.log,database timeout\n2026-01-15T10:02:00Z,auth.log,accepted public key\n',
    'case/network-notes.txt': 'Synthetic capture: TCP connection from 192.0.2.10:49152 to 192.0.2.80:443.\nThree handshake packets are shown. Payload encryption prevents content inspection.\nThe fixture is a text teaching transcript, not a binary PCAP.\n',
    'scripts/report.sh': BASH_REPORT, 'scripts/check-files.sh': BASH_CHECK, 'scripts/analyze.py': PYTHON_SCRIPT,
    'scripts/workflow.txt': 'Input: UTF-8 logs/app.log\nOutput: report.json schema_version 1\nProduction plan: validate input; write temporary output; atomically replace on success.\nSchedule: explicit working directory, interpreter path, UTC policy and non-overlap lock.\nObserve: exit status, error log, last successful run and output validation.\nRecovery: retain prior output and retry only after fixing the input problem.\n',
    'photo.jpg': 'SYNTHETIC JPEG METADATA FIXTURE (not a real image)\n',
    'sample.pcap': 'SYNTHETIC CAPTURE TRANSCRIPT (not a real PCAP)\n',
    'sample.tar': 'SYNTHETIC ARCHIVE LISTING FIXTURE (not a real archive)\n',
}
HELP = '''Rooted virtual terminal — supported teaching subset
Navigation: pwd, cd, ls [-lah|--all], find PATH -type f -name PATTERN
Files: mkdir [-p], touch, cat, cp, mv, rm (single files), stat, file
Text: echo, printf, head, tail, grep [-inv], wc [-lwc], sort, uniq [-c], cut
Integrity: sha256sum, md5sum, xxd [-l N], strings
Fixtures: uname, whoami, id, groups, hostname, free, df, du, lsblk, ps, top,
  kill -TERM 120, systemctl status nginx, journalctl [-n N], apt list/show,
  ip addr/route/neigh, ss, dig example.com, curl -I https://example.com,
  ssh -V, tcpdump -n -r sample.pcap, exiftool photo.jpg, tar -tf sample.tar
Teaching demos: bash scripts/report.sh, bash scripts/check-files.sh,
  python3 scripts/analyze.py, python3 --version, jq .
Git model: git init/status/add/commit/log/diff
Shell subset: $VARIABLE, export, filename globs, |, >, >>, <, echo $?
Tools: help, man COMMAND, command -v NAME, history, clear, true, false
Not a real shell: no sudo, devices, network traffic, arbitrary code, &&, loops,
command substitution, descriptor redirection, job control or interactive editors.
Use the VM exercises to practice those features with real Linux tools.\n'''

class LabError(Exception):
    pass

def initial_state():
    files = {(k if k.startswith('/') else HOME+'/'+k):v for k,v in SEEDS.items()}
    dirs = {'/', '/home', HOME, '/etc', '/var', '/var/log', '/tmp', '/usr', '/usr/bin', '/root'}
    for name in files:
        parent = posixpath.dirname(name)
        while parent != '/':
            dirs.add(parent); parent = posixpath.dirname(parent)
    return dict(cwd=HOME, files=files, dirs=sorted(dirs), modes={}, env={'HOME':HOME,'SHELL':'/bin/bash','USER':'learner','PATH':'/usr/bin:/bin'}, history=[], transcript=[], status=0, done=[], git=None, worker=True)

def canonical(command):
    try:
        return shlex.split(command)
    except ValueError:
        return []

class Terminal:
    def __init__(self, state=None):
        self.s = state or initial_state()
    def path(self, word):
        if word == '~' or word.startswith('~/'): word = HOME + word[1:]
        return posixpath.normpath(word if word.startswith('/') else posixpath.join(self.s['cwd'],word))
    def read(self, name):
        p = self.path(name)
        if p not in self.s['files']: raise LabError(f'{name}: no such regular file')
        return self.s['files'][p]
    def write(self, name, value, append=False):
        p = self.path(name)
        if p in self.s['dirs']: raise LabError(f'{name}: is a directory')
        if posixpath.dirname(p) not in self.s['dirs']: raise LabError(f'{name}: parent directory does not exist')
        value = (self.s['files'].get(p,'') if append else '') + value
        if len(value.encode()) > 100_000: raise LabError('Virtual file limit: 100 KB')
        if p not in self.s['files'] and len(self.s['files']) >= 256: raise LabError('Virtual file limit: 256 entries')
        self.s['files'][p] = value
    def tokens(self, raw):
        # Retain quote context so single quotes preserve $ and quoted globs remain literal.
        lex = shlex.shlex(raw, posix=False, punctuation_chars='|<>')
        lex.whitespace_split=True; lex.commenters='#'
        out=[]
        for item in lex:
            quoted = item.startswith(('"',"'")) and item.endswith(item[0])
            if quoted:
                quote=item[0]; item=item[1:-1]
            else: quote=None
            if quote != "'":
                item=re.sub(r'\$(\?|[A-Za-z_][A-Za-z_0-9]*|\{[A-Za-z_][A-Za-z_0-9]*\})', lambda m: str(self.s['status']) if m[1]=='?' else self.s['env'].get(m[1].strip('{}'),''),item)
            if not quoted and any(c in item for c in '*?['):
                matches=sorted(p for p in list(self.s['files'])+self.s['dirs'] if fnmatch.fnmatchcase(p,self.path(item)) and not posixpath.basename(p).startswith('.'))
                out.extend((p if item.startswith('/') else posixpath.relpath(p,self.s['cwd'])) for p in matches) if matches else out.append(item)
            else: out.append(item)
        return out
    def run(self, command):
        if not isinstance(command,str) or not command.strip(): return {'output':'','status':0,'cwd':self.s['cwd']}
        if len(command)>4096: raise LabError('Command limit: 4096 characters')
        self.s['history'].append(command); self.s['history']=self.s['history'][-100:]
        try:
            if any(x in command for x in ('`','$(','\x00')): raise LabError('Command substitution is not supported in this simulator.')
            tokens=self.tokens(command)
            if any(x in tokens for x in ('&&','||',';','&')): raise LabError('Run one command or pipeline at a time; use a real Bash VM for control operators.')
            parts=[[]]
            for token in tokens:
                if token=='|': parts.append([])
                else: parts[-1].append(token)
            output=''; status=0
            for part in parts:
                target=None; append=False; data=output
                for operator in ('<','>','>>'):
                    if operator in part:
                        idx=part.index(operator)
                        if idx+1>=len(part): raise LabError('A redirection needs a filename.')
                        dest=part[idx+1]
                        del part[idx:idx+2]
                        if operator=='<': data=self.read(dest)
                        else:
                            target=dest; append=(operator=='>>')
                            if not append: self.write(dest,'')
                if not part: raise LabError('Missing command.')
                output,status=self.execute(part,data)
                if target is not None: self.write(target,output,append); output=''
            self.s['status']=status
        except (LabError,ValueError,IndexError,re.error,TypeError) as error:
            output=f'lab: {error}\n'; self.s['status']=2
        output=output[:24000]
        if command.strip()=='clear': self.s['transcript']=[]
        else:
            self.s['transcript'].append({'command':command,'output':output,'status':self.s['status']})
            self.s['transcript']=self.s['transcript'][-60:]
        return dict(output=output,status=self.s['status'],cwd=self.s['cwd'])
    def execute(self, t, stdin=''):
        c,*a=t
        flags=[x for x in a if x.startswith('-')]
        args=[x for x in a if not x.startswith('-')]
        has=lambda ch:any(ch in f[1:] for f in flags if not f.startswith('--'))
        if '--help' in a: return HELP,0
        if c=='help': return HELP,0
        if c=='man':
            manuals={
                'pwd':'PWD(1) — print working directory\nSYNOPSIS: pwd\nDESCRIPTION: Show the absolute path of the shell current directory.\nRELATED: cd changes directory; ls lists directory entries.\n',
                'ls':'LS(1) — list directory contents\nSYNOPSIS: ls [OPTION]... [PATH]...\nOPTIONS: -a/--all includes hidden names; -l detailed listing; -h readable sizes on real GNU ls.\nThe simulator displays byte sizes in a fixed teaching format.\n',
                'grep':'GREP(1) — select matching text lines\nSYNOPSIS: grep [OPTION]... PATTERN [FILE]...\nOPTIONS: -i ignore case; -n show line numbers; -v invert selection.\nSTATUS: 0 match, 1 no match, 2 error. Lab patterns exclude repetitions and groups.\n',
                'chmod':'CHMOD(1) — change file mode bits\nSYNOPSIS: chmod MODE FILE\nLab MODE is three octal digits, e.g. 600 for owner read/write only.\n',
            }
            if not a: raise LabError('Choose a manual entry, for example man pwd')
            return manuals.get(a[0],f'{a[0]}: no dedicated lab manual page. Use real Linux man for the full reference.\n\n'+HELP),0
        if c=='clear': return '',0
        if c=='true': return '',0
        if c=='false': return '',1
        if c=='pwd': return self.s['cwd']+'\n',0
        if c=='cd':
            p=self.path(a[0] if a else '~')
            if p not in self.s['dirs']: raise LabError('Directory does not exist')
            self.s['cwd']=p; return '',0
        if c in ('echo','printf'):
            if c=='echo': return ' '.join(a)+'\n',0
            if not a: raise LabError('printf needs a format')
            fmt=a[0].replace('\\n','\n').replace('\\t','\t')
            values=a[1:]
            if '%s' in fmt: return ''.join(fmt.replace('%s',v,1) for v in values),0
            return fmt.replace('%%','%'),0
        if c=='export':
            for word in a:
                if '=' not in word: raise LabError('Use export NAME=value')
                key,val=word.split('=',1)
                if not re.fullmatch('[A-Za-z_][A-Za-z_0-9]*',key): raise LabError('Invalid variable name')
                self.s['env'][key]=val
            return '',0
        if c in ('command','which'): return '/usr/bin/'+a[-1]+'\n',0
        if c=='history': return ''.join(f'{i+1:3}  {x}\n' for i,x in enumerate(self.s['history'])),0
        if c=='ls':
            targets=args or ['.']; rows=[]
            for target in targets:
                p=self.path(target)
                if p in self.s['files']: entries=[p]
                elif p in self.s['dirs']: entries=sorted(x for x in set(self.s['dirs'])|set(self.s['files']) if posixpath.dirname(x)==p and x!=p)
                else: raise LabError(f'{target}: no such path')
                for x in entries:
                    name=posixpath.basename(x)
                    if name.startswith('.') and not (has('a') or '--all' in flags): continue
                    if has('l'):
                        directory=x in self.s['dirs']; mode=self.s['modes'].get(x,'755' if directory else '644')
                        bits=''.join('rwx'[j] if int(digit)&(4>>j) else '-' for digit in mode for j in range(3))
                        rows.append(f'{"d" if directory else "-"}{bits} 1 learner learners {len(self.s["files"].get(x,"")):5} Jan 15 10:00 {name}')
                    else: rows.append(name+('/' if x in self.s['dirs'] else ''))
            return '\n'.join(rows)+'\n',0
        if c=='mkdir':
            for name in args:
                p=self.path(name)
                if p in self.s['files']: raise LabError('A file exists at that path')
                if len(self.s['dirs'])>=256: raise LabError('Directory limit reached')
                if '-p' not in flags and posixpath.dirname(p) not in self.s['dirs']: raise LabError('Parent missing; try mkdir -p')
                if p in self.s['dirs'] and '-p' not in flags: raise LabError('Directory already exists')
                chain=[p]
                if '-p' in flags:
                    while posixpath.dirname(chain[-1]) not in self.s['dirs']: chain.append(posixpath.dirname(chain[-1]))
                self.s['dirs']=sorted(set(self.s['dirs'])|set(chain))
            return '',0
        if c=='touch':
            for name in a:
                if self.path(name) not in self.s['files']: self.write(name,'')
            return '',0
        if c in ('cp','mv'):
            if len(args)!=2: raise LabError('Use a source file and a destination')
            src,dst=args; value=self.read(src)
            if self.path(dst) in self.s['dirs']: dst=posixpath.join(dst,posixpath.basename(src))
            if self.path(src)==self.path(dst): raise LabError('Source and destination are the same')
            self.write(dst,value)
            if c=='mv': del self.s['files'][self.path(src)]
            return '',0
        if c=='rm':
            if flags: raise LabError('Only unflagged single-file rm is supported; no recursive deletion')
            for name in args: self.read(name); del self.s['files'][self.path(name)]
            return '',0
        if c=='cat': return ''.join(self.read(x) for x in a) if a else stdin,0
        if c in ('head','tail'):
            n=10; inputs=a[:]
            if '-n' in inputs:
                i=inputs.index('-n'); n=int(inputs[i+1]); del inputs[i:i+2]
            if n<0: raise LabError('Use a nonnegative line count')
            data=''.join(self.read(x) for x in inputs) if inputs else stdin
            lines=data.splitlines(keepends=True)
            return ''.join(lines[:n] if c=='head' else (lines[-n:] if n else [])),0
        if c=='grep':
            if not args: raise LabError('grep needs a pattern')
            pattern=args[0]; data=''.join(self.read(x) for x in args[1:]) if len(args)>1 else stdin
            # Small, bounded pattern subset excludes nested quantifiers / expensive constructs.
            if len(pattern)>120 or any(x in pattern for x in ('(',')','{','}','*','+','?','\\1')): raise LabError('Use a simple teaching regex (no groups, repetitions or backreferences)')
            rows=[]
            for i,line in enumerate(data.splitlines()):
                found=bool(re.search(pattern,line,re.I if has('i') else 0))
                if found != has('v'): rows.append((f'{i+1}:' if has('n') else '')+line)
            return '\n'.join(rows)+('\n' if rows else ''),0 if rows else 1
        if c=='wc':
            data=''.join(self.read(x) for x in args) if args else stdin
            if has('l'): out=str(data.count('\n'))
            elif has('w'): out=str(len(data.split()))
            elif has('c'): out=str(len(data.encode()))
            else: out=f'{data.count(chr(10))} {len(data.split())} {len(data.encode())}'
            return out+'\n',0
        if c=='sort':
            data=''.join(self.read(x) for x in args) if args else stdin
            return '\n'.join(sorted(data.splitlines(),reverse=has('r')))+'\n',0
        if c=='uniq':
            data=''.join(self.read(x) for x in args) if args else stdin
            rows=[]
            for line in data.splitlines():
                if rows and rows[-1][0]==line: rows[-1][1]+=1
                else: rows.append([line,1])
            return ''.join((f'{n:4} ' if has('c') else '')+line+'\n' for line,n in rows),0
        if c=='cut':
            delim='\t'; field=1; rest=[]; i=0
            while i<len(a):
                if a[i] in ('-d','-f'):
                    if a[i]=='-d': delim=a[i+1]
                    else: field=int(a[i+1])
                    i+=2
                else: rest.append(a[i]); i+=1
            data=''.join(self.read(x) for x in rest) if rest else stdin
            return ''.join((line.split(delim)[field-1] if 0<field<=len(line.split(delim)) else '')+'\n' for line in data.splitlines()),0
        if c in ('sha256sum','md5sum'):
            algo=hashlib.sha256 if c=='sha256sum' else hashlib.md5
            return ''.join(f'{algo(self.read(x).encode()).hexdigest()}  {x}\n' for x in a),0
        if c=='chmod':
            if len(a)!=2 or not re.fullmatch('[0-7]{3}',a[0]): raise LabError('Use chmod MODE FILE, for example chmod 600 notes.txt')
            p=self.path(a[1])
            if p not in self.s['files'] and p not in self.s['dirs']: raise LabError('Path does not exist')
            self.s['modes'][p]=a[0]; return '',0
        if c=='stat':
            value=self.read(a[0]); mode=self.s['modes'].get(self.path(a[0]),'644')
            return f'File: {a[0]}\nSize: {len(value.encode())} bytes\nAccess: (0{mode})  Uid: (1000/learner) Gid: (1000/learners)\nModify: 2026-01-15 10:00:00 +0000\nChange: 2026-01-15 10:00:00 +0000\n[Fixture timestamps; ctime is not creation time.]\n',0
        if c=='file': self.read(a[0]); return f'{a[0]}: UTF-8 teaching text (all lab items are synthetic)\n',0
        if c=='find':
            base=self.path(a[0] if a else '.'); pattern=a[a.index('-name')+1] if '-name' in a else '*'
            return ''.join(posixpath.relpath(p,self.s['cwd'])+'\n' for p in sorted(self.s['files']) if (p.startswith(base.rstrip('/')+'/')) and fnmatch.fnmatchcase(posixpath.basename(p),pattern)),0
        if c=='xxd':
            n=int(a[a.index('-l')+1]) if '-l' in a else 64; data=self.read(a[-1]).encode()[:max(0,min(n,1000))]
            return ''.join(f'{i:08x}: {data[i:i+16].hex(" "):<48} {"".join(chr(b) if 32<=b<127 else "." for b in data[i:i+16])}\n' for i in range(0,len(data),16)),0
        if c=='strings': return '\n'.join(re.findall(r'[\x20-\x7e]{4,}',self.read(a[0])))+'\n',0
        if c=='jq': return json.dumps(json.loads(stdin or self.read(a[-1])),indent=2)+'\n',0
        if c=='git': return self.git(a)
        if c in ('bash','python3'):
            if '--version' in a: return ('Python 3.12 (teaching fixture)' if c=='python3' else 'GNU bash 5.2 (teaching fixture)')+'\n',0
            if not a: raise LabError('Interactive interpreters are unavailable. Use a bundled demonstration script.')
            p=self.path(a[0]); original=SEEDS.get(posixpath.relpath(p,HOME))
            if original is None or self.read(a[0])!=original: raise LabError('Only unchanged bundled scripts can run as curated demos. Use a real VM for your own code.')
            if c=='bash' and p==HOME+'/scripts/report.sh': return self.execute(['grep','ERROR','logs/app.log'])
            if c=='bash' and p==HOME+'/scripts/check-files.sh': return '[Curated demo for arguments notes.txt missing.txt]\nreadable: notes.txt\nnot a readable file: missing.txt\n',0
            if c=='python3' and p==HOME+'/scripts/analyze.py':
                lines=self.read('logs/app.log').splitlines(); data=dict(schema_version=1,input='logs/app.log',lines=len(lines),errors=sum('ERROR' in line for line in lines))
                result=json.dumps(data,indent=2)+'\n'; self.write('report.json',result); return result,0
            raise LabError('This interpreter only runs its matching bundled demo.')
        if c=='kill':
            if a!=['-TERM','120']: raise LabError('Only kill -TERM 120 is available for the simulated worker')
            if not self.s['worker']: raise LabError('The simulated worker has already exited')
            self.s['worker']=False; return 'Simulated worker 120 received SIGTERM.\n',0
        return self.fixture(c,a)
    def git(self,a):
        if not a: raise LabError('Use git init, status, add, commit, log or diff')
        op=a[0]; g=self.s['git']
        if op=='init':
            if not g: self.s['git']=dict(root=self.s['cwd'],index={},commits=[])
            return 'Initialized virtual Git teaching repository.\n',0
        if not g: raise LabError('Not a virtual repository; run git init first')
        if op=='add':
            for name in a[1:]:
                if name=='.': g['index'].update({p:v for p,v in self.s['files'].items() if p.startswith(g['root']+'/')})
                else: g['index'][self.path(name)]=self.read(name)
            return '',0
        if op=='status':
            staged=[posixpath.relpath(p,g['root']) for p in g['index']]
            snapshot=g['commits'][-1]['snapshot'] if g['commits'] else {}
            changed=[posixpath.relpath(p,g['root']) for p,v in self.s['files'].items() if p.startswith(g['root']+'/') and snapshot.get(p)!=v and p not in g['index']]
            return 'On branch main (virtual model)\nStaged: '+(', '.join(staged) or 'none')+'\nUnstaged/untracked: '+(', '.join(changed) or 'none')+'\n',0
        if op=='commit':
            if not g['index']: raise LabError('Nothing staged; run git add FILE')
            if '-m' not in a: raise LabError('Supply a message with -m')
            message=a[a.index('-m')+1]
            snapshot=dict(g['commits'][-1]['snapshot']) if g['commits'] else {}; snapshot.update(g['index'])
            digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()+message.encode()).hexdigest()[:7]
            g['commits'].append(dict(id=digest,message=message,snapshot=snapshot)); g['index']={}
            return f'[main {digest}] {message}\n',0
        if op=='log': return ''.join(f'{x["id"]} {x["message"]}\n' for x in reversed(g['commits'])) or 'No commits yet.\n',0
        if op=='diff':
            old=g['commits'][-1]['snapshot'] if g['commits'] else {}
            return ''.join(f'changed: {posixpath.relpath(p,g["root"])}\n' for p,v in self.s['files'].items() if p.startswith(g['root']+'/') and p in old and old[p]!=v) or 'No tracked content differences (simplified model).\n',0
        raise LabError('Git teaching subset: init, status, add, commit, log, diff')
    def fixture(self,c,a):
        simple={
            'uname':'Linux lab-host 6.8.0-training x86_64 GNU/Linux', 'whoami':'learner',
            'id':'uid=1000(learner) gid=1000(learners) groups=1000(learners),27(sudo)', 'groups':'learners sudo', 'hostname':'lab-host',
            'free':'               total   used   free  available\nMem:            4Gi   1.2Gi  0.8Gi   2.5Gi\nSwap:           2Gi      0B    2Gi',
            'df':'Filesystem    Size  Used Avail Use% Mounted on\n/dev/vda1      30G   11G   19G  37% /',
            'du':'4.0K\t'+(a[-1] if a else '.'),
            'lsblk':'NAME   SIZE TYPE MOUNTPOINT\nvda     30G disk\n└─vda1  30G part /',
            'ss':'Netid State  Local Address:Port\ntcp   LISTEN 127.0.0.1:8000\ntcp   LISTEN 0.0.0.0:22\nudp   UNCONN 127.0.0.53:53',
        }
        if c in simple: return '[Simulated system snapshot]\n'+simple[c]+'\n',0
        if c in ('ps','top'):
            return 'UID       PID PPID COMMAND\nlearner   100    1 bash\nroot      110    1 nginx\n'+('learner   120  100 lab-worker\n' if self.s['worker'] else ''),0
        if c=='systemctl' and a==['status','nginx']: return 'nginx.service — Lab web server\nActive: active (running) [simulated]\nMain PID: 110\n',0
        if c=='journalctl':
            n=int(a[a.index('-n')+1]) if '-n' in a else 20
            return ''.join(self.s['files'][HOME+'/logs/app.log'].splitlines(keepends=True)[-max(1,min(n,100)):]),0
        if c=='apt' and a==['list','--installed']: return 'Listing... [simulated]\npython3/training 3.12 amd64 [installed]\nbash/training 5.2 amd64 [installed]\n',0
        if c=='apt' and a==['show','python3']: return 'Package: python3\nVersion: 3.12 (fixture)\nSource: trusted training repository\nDescription: Python interpreter\n',0
        if c=='ip':
            if a in (['addr'],['a']): return '1: lo  link/loopback 00:00:00:00:00:00\n    inet 127.0.0.1/8\n2: eth0 link/ether 02:00:00:00:00:10\n    inet 192.0.2.10/24\n[Documentation-only addresses; no traffic sent.]\n',0
            if a==['route']: return 'default via 192.0.2.1 dev eth0\n192.0.2.0/24 dev eth0 src 192.0.2.10\n',0
            if a==['neigh']: return '192.0.2.1 dev eth0 lladdr 02:00:00:00:00:01 REACHABLE\n',0
        if c=='dig' and a==['example.com']: return ';; Simulated DNS answer (not a live query)\nexample.com. 300 IN A 192.0.2.80\n',0
        if c=='curl' and a==['-I','https://example.com']: return 'HTTP/2 200\ncontent-type: text/html\nserver: training-fixture\n[Simulated response; no network request.]\n',0
        if c=='ssh' and a==['-V']: return 'OpenSSH_9.6p1 (teaching fixture; no connection)\n',0
        if c=='tcpdump' and a==['-n','-r','sample.pcap']:
            self.read('sample.pcap'); return '[Synthetic teaching transcript]\n10:00:00.000 IP 192.0.2.10.49152 > 192.0.2.80.443: Flags [S]\n10:00:00.020 IP 192.0.2.80.443 > 192.0.2.10.49152: Flags [S.]\n10:00:00.021 IP 192.0.2.10.49152 > 192.0.2.80.443: Flags [.]\n',0
        if c=='exiftool' and a==['photo.jpg']:
            self.read('photo.jpg'); return '[Synthetic metadata; fixture is not a JPEG]\nFile Name: photo.jpg\nMake: Training Camera\nDate/Time Original: 2026:01:15 09:30:00\nGPS: not present\n',0
        if c=='tar' and a==['-tf','sample.tar']: self.read('sample.tar'); return '[Synthetic archive listing]\nnotes.txt\nlogs/app.log\n',0
        raise LabError(f'{c}: unsupported command or arguments. Run help to see the supported subset.')
