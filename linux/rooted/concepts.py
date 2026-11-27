"""Interactive concept calculators, all evaluated in Python without host access."""
import hashlib
import ipaddress
import posixpath
import shlex


def calculate(body):
    tool=body.get('tool')
    def text(name,default=''):
        value=body.get(name,default)
        if not isinstance(value,str) or len(value)>4096:raise ValueError('Use text inputs up to 4096 characters')
        return value
    if tool=='permissions':
        mode=text('mode')
        if len(mode)!=3 or any(c not in '01234567' for c in mode):raise ValueError('Enter three octal digits from 0 to 7, for example 640')
        groups=['Owner','Group','Other'];rows=[];symbol=''
        for name,digit in zip(groups,mode):
            bits=int(digit);letters=''.join(letter if bits&value else '-' for letter,value in [('r',4),('w',2),('x',1)])
            symbol+=letters
            rows.append([name,f'{digit} = {letters} · '+(', '.join(label for label,val in [('read',4),('write',2),('execute',1)] if bits&val) or 'no permission bits')])
        rows.insert(0,['Symbolic regular-file mode','-'+symbol])
        return dict(title=f'What chmod {mode} means',rows=rows,explanation='For files, execute permits attempting to run a program. For directories, execute means traversal. ACLs, privileged identities and other controls can affect effective access; these are only the basic mode bits.')
    if tool=='subnet':
        net=ipaddress.ip_network(text('network'),strict=False)
        rows=[['Network',str(net)],['Address family',f'IPv{net.version}'],['Prefix bits',str(net.prefixlen)],['Address bits',str(net.max_prefixlen)],['Total addresses',str(net.num_addresses)],['First address',str(net.network_address)],['Last address',str(net.broadcast_address)]]
        if net.version==4:
            hosts=net.num_addresses-2 if net.prefixlen<31 else net.num_addresses
            rows.extend([['Subnet mask',str(net.netmask)],['Broadcast address',str(net.broadcast_address) if net.prefixlen<31 else 'No conventional broadcast reservation for this /31 or /32 teaching model'],['Conventional host count',str(hosts)]])
        else:rows.append(['Broadcast','IPv6 does not use broadcast'])
        return dict(title='Read the network prefix',rows=rows,explanation='The input is normalized to its network boundary. IPv4 /31 point-to-point links and /32 host routes use different host rules from ordinary subnets. These calculations do not test routes or send traffic. IPv6 address usability depends on network configuration.')
    if tool=='hash':
        original=text('original');changed=text('changed');a=original.encode('utf-8');b=changed.encode('utf-8')
        first=hashlib.sha256(a).hexdigest();second=hashlib.sha256(b).hexdigest()
        return dict(title='Small input change, different fingerprint',rows=[['Original UTF-8 bytes',str(len(a))],['Edited UTF-8 bytes',str(len(b))],['Original SHA-256',first],['Edited SHA-256',second],['Matching content bytes','Yes' if a==b else 'No'],['Changed hexadecimal positions',f'{sum(x!=y for x,y in zip(first,second))} of 64']],explanation='This is a real SHA-256 calculation performed in Python. Whitespace, capitalization, encoding and a final newline affect the input bytes. Matching digests support content consistency; a digest alone does not identify an author or encrypt content.')
    if tool=='paths':
        cwd=text('cwd','/home/learner');path=text('path')
        if not cwd.startswith('/'):raise ValueError('The current directory must be an absolute Linux path')
        if path=='~' or path.startswith('~/'):path='/home/learner'+path[1:]
        resolved=posixpath.normpath(path if path.startswith('/') else posixpath.join(cwd,path))
        return dict(title='Resolve a Linux path',rows=[['Working directory',posixpath.normpath(cwd)],['Input path',text('path')],['Normalized result',resolved],['Parent directory',posixpath.dirname(resolved)],['Final component',posixpath.basename(resolved) or '/']],explanation='This lexical calculation handles /, . and .. with a fixed learner home. It does not access a filesystem, expand arbitrary users, check existence or resolve symbolic links. Real physical path resolution can differ when symlinks are involved.')
    if tool=='command':
        command=text('command');lexer=shlex.shlex(command,posix=True,punctuation_chars='|<>;&');lexer.whitespace_split=True;lexer.commenters=''
        tokens=list(lexer)
        if not tokens:raise ValueError('Enter a command line to inspect')
        rows=[]
        for i,token in enumerate(tokens):
            kind='command word' if i==0 else 'shell operator' if token in ('|','>','>>','<','&&','||',';','&') else 'option-like argument' if token.startswith('-') else 'operand / argument'
            rows.append([f'Word {i+1} · {kind}',token])
        return dict(title='Look inside the command line',rows=rows,explanation='This is a shell-like lexical breakdown, not a complete Bash parser. Quotes group words and are removed. No expansions, command substitution or execution occur. An option value can look like an operand; only a command documentation defines how its arguments are interpreted.')
    raise ValueError('Choose a supported concept tool')
