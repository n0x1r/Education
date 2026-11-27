#!/usr/bin/env python3
"""Reference solution: read a practice directory, hash files, summarize a UTF-8 log.
No network, package installation, subprocesses or changes to input files.
The output path is created exclusively unless --force is explicitly supplied.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def sha256_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def analyze(root,log,output):
    """Return a deterministic report and collect per-file read errors."""
    root=root.resolve(strict=True)
    if not root.is_dir(): raise ValueError('Input must be a directory')
    log_path=(root/log).resolve(strict=True)
    if not log_path.is_relative_to(root): raise ValueError('Log must be inside the input directory')
    errors=[];inventory=[]
    # os.walk with followlinks=False avoids traversing symlink directories.
    def walk_error(error):
        errors.append({'path':str(error.filename),'error':type(error).__name__})
    for directory,subdirs,files in os.walk(root,followlinks=False,onerror=walk_error):
        subdirs[:]=sorted(d for d in subdirs if not (Path(directory)/d).is_symlink())
        for name in sorted(files):
            path=Path(directory)/name
            if path.is_symlink() or not path.is_file() or path.resolve()==output.resolve():continue
            relative=str(path.relative_to(root))
            try: inventory.append({'path':relative,'bytes':path.stat().st_size,'sha256':sha256_file(path)})
            except OSError as error: errors.append({'path':relative,'error':type(error).__name__})
    count=0;error_count=0
    # Streaming keeps memory bounded for large text logs.
    with log_path.open(encoding='utf-8') as stream:
        for line in stream:
            count+=1;error_count+=('ERROR' in line)
    return {'schema_version':1,'complete':not errors,'files':sorted(inventory,key=lambda row:row['path']),
            'log':{'path':str(log_path.relative_to(root)),'records':count,'error_records':error_count},'read_errors':errors}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path,help='A directory of your own practice files')
    parser.add_argument('--log',type=Path,default=Path('logs/app.log'),help='UTF-8 log, relative to input directory')
    parser.add_argument('--output',type=Path,required=True,help='New JSON report path, preferably outside input')
    parser.add_argument('--force',action='store_true',help='Replace an existing report after successful analysis')
    args=parser.parse_args(argv)
    try:
        root=args.directory.resolve(strict=True)
        output=args.output.absolute()
        if output.is_symlink():raise ValueError('Refusing a symbolic-link output')
        if output.exists() and (output.resolve()==(root/args.log).resolve() or output.resolve().is_relative_to(root)):
            raise ValueError('Refusing to replace any existing file inside the input directory')
        if output.exists() and not args.force:raise FileExistsError('Output exists; choose a new path or use --force for a report outside the input directory')
        report=analyze(root,args.log,output)
        payload=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
        if args.force:
            # Write a complete temporary result on the same filesystem, then atomically replace.
            fd,temp=tempfile.mkstemp(prefix='.rooted-report-',dir=output.parent)
            try:
                with os.fdopen(fd,'w',encoding='utf-8') as stream:stream.write(payload)
                os.replace(temp,output)
            finally:
                if os.path.exists(temp):os.unlink(temp)
        else:
            with output.open('x',encoding='utf-8') as stream:stream.write(payload)
        print(f'Report: {output} | files={len(report["files"])} | errors={report["log"]["error_records"]} | complete={report["complete"]}')
        return 0 if report['complete'] else 2
    except (OSError,UnicodeError,ValueError) as error:
        print(f'Analysis failed: {error}',file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
