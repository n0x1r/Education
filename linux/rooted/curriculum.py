"""Authored curriculum. All examples target the bundled simulator or a disposable VM."""
import hashlib

MODULES = [
    ('fundamentals', 'Linux fundamentals', 'Understand the system beneath the prompt.', 'Operating systems, shells, terminals & directories', '◈', '#96c97e'),
    ('structure', 'Command structure', 'Turn a line of text into a precise instruction.', 'Flags, arguments, parameters & special characters', '⌘', '#b5a3e5'),
    ('files', 'File management', 'Make the filesystem work for you.', 'Create, read, move & search your files', '▤', '#e4bd78'),
    ('administration', 'System administration', 'Understand what is running and who can do what.', 'Processes, permissions, users & packages', '⚙', '#86b9df'),
    ('networking', 'Networking', 'Follow data from your device to its destination.', 'IP, MAC, TCP, UDP, DNS, ports & packets', '◎', '#7dcbbf'),
    ('security', 'Cybersecurity', 'Learn to assess, protect and verify.', 'Vulnerabilities, authentication & encryption', '◇', '#dc9baf'),
    ('forensics', 'Digital forensics', 'Build a repeatable, evidence-led investigation.', 'Metadata, hashing, acquisition & artifacts', '⌕', '#b9b7ed'),
    ('automation', 'Scripting & automation', 'Make good work repeatable.', 'Bash, Python, Git & automated workflows', '⟐', '#d1c875'),
]
LESSONS = []

def Q(prompt, correct, wrong1, wrong2, why):
    options = [correct, wrong1, wrong2]
    # Stable rotation avoids teaching learners to always choose the first answer.
    shift = hashlib.sha256(prompt.encode()).digest()[0] % 3
    options = options[shift:] + options[:shift]
    return {'prompt': prompt, 'options': options, 'answer': options.index(correct), 'explanation': why}

def L(module, slug, title, summary, sections, example, tasks, questions, real, capstone=False):
    mid = MODULES[module-1][0]
    LESSONS.append(dict(id=f'{mid}-{slug}', module=mid, title=title, summary=summary,
        minutes=45 if capstone else 25, capstone=capstone,
        sections=[dict(title=a.strip(), text=b.strip()) for a,b in (s.split('::',1) for s in sections.split('\n\n'))],
        example=example.strip(), tasks=[{'instruction':a,'command':b} for a,b in tasks], questions=questions,
        real_practice=real, takeaway=summary))

L(1,'operating-system','Meet your operating system','Separate the kernel, distribution and applications.',
'''The layers of Linux::An operating system manages CPU time, memory, storage and devices so applications can share one machine. Linux is the kernel: the core that talks to hardware and provides system calls. A usable distribution adds libraries, a package manager, utilities and often a desktop. Ubuntu, Debian and Fedora package these pieces differently; they are not different shells.

A system you can identify::Kernel version and distribution version answer different questions. uname reports the kernel. /etc/os-release describes the distribution. A container shares its host kernel, so its uname result may not match the distribution in its filesystem. This matters when choosing packages or troubleshooting a driver.

Observe before changing::Start an investigation with read-only commands. Record the environment and the exact error before attempting a fix. In this course, command output is a teaching fixture rather than a measurement of the computer hosting the app.''',
'uname -a\ncat /etc/os-release', [('Inspect the lab kernel information.','uname -a'),('Read the lab distribution identity.','cat /etc/os-release')],
[Q('Which component schedules CPU time?', 'The kernel','The terminal window','The file manager','The kernel allocates resources and exposes system calls.'),Q('Why can a container show an unexpected kernel?', 'It shares the host kernel','Its shell renames the kernel','It has no operating system','Containers isolate processes while sharing the host kernel.')],
'On a Linux VM, compare uname -r with cat /etc/os-release. Write down which is the kernel version and which is the distribution version.')
L(1,'shell-terminal','Terminal, shell and command','Know where you type, what interprets it and what runs.',
'''Three distinct jobs::A terminal is an input/output interface. A shell is a program that parses your command line, expands variables and starts programs. A command may be a shell built-in, a function or an executable found through PATH. Bash is a shell; GNOME Terminal is a terminal emulator; ls is usually an executable.

Why cd is special::A process inherits its parent's environment, but cannot change the parent's working directory. cd therefore needs to run inside the current shell as a built-in. Launching a child program to change directories would leave the parent shell in the same place.

Read the prompt::A prompt often includes user, host and current directory, followed by $ for a normal user. A # prompt commonly indicates root, but prompts can be customized. Do not paste prompt symbols from documentation. This app's terminal is a limited Python simulator; use help to see its supported commands.''',
'whoami\nprintf "%s\\n" "$SHELL"\ncommand -v python3', [('Identify the simulated account.','whoami'),('Find the lab Python executable.','command -v python3')],
[Q('What interprets pipes and variables?', 'The shell','The monitor','The kernel version string','The shell parses syntax before invoking programs.'),Q('Why is cd normally a built-in?', 'It must change the current shell state','It must download a directory','It encrypts the prompt','A child process cannot change its parent process working directory.')],
'Open a terminal in a Linux VM. Run type cd, type ls and printf "%s\\n" "$SHELL". Compare a built-in with an executable.')
L(1,'filesystem','The filesystem map','Navigate one directory tree without guessing.',
'''One rooted tree::Linux paths form one tree beginning at /. /home contains ordinary user homes, /etc contains much system configuration, /var holds changing data such as logs, and /tmp is temporary space. /root is the root account home; it is not the root directory /. Modern distributions often link /bin to /usr/bin.

Where you are matters::Every process has a current working directory. pwd prints yours. ls lists a directory without moving into it. cd changes your shell directory. Names are case-sensitive on typical Linux filesystems: Notes.txt and notes.txt can be different files.

Mounted storage::Other disks and network shares are attached at mount points within this same tree. A path does not tell you whether the underlying storage is local, removable or remote. Use mount information or findmnt on a real system before assuming a file lives on a particular disk.''',
'pwd\nls /\ncd /home/learner\nls -a', [('List the top level of the lab.','ls /'),('Move into the sample case directory.','cd /home/learner/case')],
[Q('What does / identify?', 'The root directory','The root account home','The current user','All absolute paths start at the root directory.'),Q('Does ls /etc change your working directory?', 'No, it lists a target path','Yes, permanently','Only if run as root','Listing and navigating are separate operations.')],
'Draw a small tree of /, /home, /etc and /var. Use ls on each; avoid editing system files.')
L(1,'paths','Absolute and relative paths','Resolve paths from a reliable starting point.',
'''Two ways to name a location::An absolute path begins with / and is resolved from the filesystem root. A relative path is resolved from the working directory. If you are in /home/learner, case/evidence.txt and /home/learner/case/evidence.txt name the same file. Relative paths make projects portable, while absolute paths remove ambiguity.

Dot, dot-dot and home::. means the current directory and .. means its parent. The shell expands an unquoted ~ at the start of a word into your home directory. Hidden names conventionally begin with a dot; they are not encrypted or protected merely because ls hides them by default.

Quote the path::A name with spaces must reach the command as one argument. Use quotes such as "my notes.txt". Quoting does not make the file safer; it changes how the shell groups text. Before modifying a relative path, check pwd so the operation reaches the intended directory.''',
'cd ~/case\npwd\ncd ..\nls ./case', [('Use a home-relative path to enter the case.','cd ~/case'),('Return to its parent.','cd ..')],
[Q('Which path is absolute?', '/var/log/auth.log','var/log/auth.log','../auth.log','A leading slash makes a path absolute.'),Q('What does .. refer to?', 'The parent directory','All hidden files','Your home directory','Dot-dot moves one level toward the root.')],
'Create a practice directory in your VM home and reach it using absolute, relative and home-relative paths. Verify with pwd each time.')
L(1,'help','Get help without guessing','Use built-in help and manuals to understand a command.',
'''Help has several levels::A program often accepts --help for a short usage summary. man opens a full manual when installed. Shell built-ins use help in Bash. A synopsis uses conventions: [OPTION] means optional, FILE is a placeholder and ... indicates repetition. These characters are documentation unless explicitly part of an example.

Read the exact option::Options are not universal. -h means human-readable sizes in ls but help in some other programs. Case also matters. Read documentation for the version installed on your machine; a web example may describe a different implementation.

A useful learning loop::Read the purpose, inspect a minimal example, predict its effect, then run it against disposable data and compare the result. When reporting a problem, include the command, version, relevant output and what you expected. Do not include passwords, private keys or session tokens.''',
'help\nls --help\nman pwd', [('Read the simulator command help.','help'),('Inspect the pwd manual entry.','man pwd')],
[Q('What does [FILE] normally mean in a synopsis?', 'An optional file argument','A literal name including brackets','Every file on the system','Brackets conventionally mark optional syntax in documentation.'),Q('Is -h guaranteed to mean help?', 'No, options are command-specific','Yes, in every program','Only for root','Check the command documentation rather than inferring a flag.')],
'In a real terminal, run ls --help and man ls. Find an option you have not used, then test it on your practice directory.')
L(1,'workflow','Build a dependable terminal workflow','Predict, execute, inspect and keep useful notes.',
'''Small steps build confidence::Before running a command, say what it should read or change. Afterward, inspect the outcome instead of assuming success. A command can succeed silently. History records command text, but it is not a complete audit log and may accidentally contain secrets.

Recover from common mistakes::In a real terminal, Ctrl-C usually interrupts a foreground program; Ctrl-D signals end of input; q exits many pagers. The up arrow recalls history and Tab often completes a name. These shortcuts are terminal-dependent. In the simulator, use the up/down arrows for history and clear to clean the display.

Make work reproducible::Keep a short log of commands, observations and environment details. Separate observation from interpretation. A statement such as "two ERROR lines appeared" is stronger than "the server is broken" unless additional evidence supports that diagnosis.''',
'pwd\nls\nhistory', [('Check your location before acting.','pwd'),('Review commands run in this lab.','history')],
[Q('What should follow a command that changes a file?', 'Inspect the intended result','Assume silence proves correctness','Repeat it with sudo','Verification tests whether the change matched your intention.'),Q('Is shell history a complete audit trail?', 'No, it can be incomplete or changed','Yes, it is tamper-proof','Only if lines are numbered','History is useful for recall, but not a trusted audit mechanism.')],
'Practice interrupting sleep 30 with Ctrl-C on a VM. Write a short log recording what happened and why you interrupted it.')
L(1,'capstone','Field mission: orient yourself','Produce a basic environment inventory.',
'''Your assignment::You have joined a team with an unfamiliar Linux machine. Establish its identity, user context and filesystem location before making changes. Work through the tasks and keep a short note explaining what each output tells you.

Evidence of understanding::Distinguish the lab kernel from its distribution, and distinguish your home from /. Your final note should explain why reading /etc/os-release does not require cd /etc. Use the knowledge check to verify these distinctions.''',
'uname -a\ncat /etc/os-release\nwhoami\npwd', [('Identify the kernel.','uname -a'),('Identify the distribution.','cat /etc/os-release'),('Identify your account.','whoami'),('List your home, including dotfiles.','ls -a ~')],
[Q('Which command reports the working directory?', 'pwd','whoami','uname','pwd prints the current directory.'),Q('Is /root the same as /?', 'No, it is a home directory','Yes, both are the root of the tree','Only on Ubuntu','The root account home is a directory beneath the filesystem root.')],
'On a VM, create an environment inventory with distribution, kernel, user, home and shell. Explain each item in your own words.',True)

L(2,'anatomy','Anatomy of a command','Recognize commands, options and operands.',
'''Parse the line::In ls -lah /home/learner, ls selects the program, -lah supplies options and /home/learner is an operand: the target directory. An argument is any word passed to a command; options and operands are both arguments. A parameter can mean a named variable in shell terminology or a function input in programming.

Short and long options::Many tools support short options such as -a and long options such as --all. Some short flags can be grouped, but options that consume values make grouping less predictable. ls -l -a -h is an easier form to read while learning. Commands have their own conventions.

The end of options::Many programs accept -- to stop option parsing. A filename beginning with a dash can otherwise be mistaken for an option. For portable practice, use a path such as ./-notes rather than assuming every program implements --.''',
'ls -l -a -h /home/learner\nls --all', [('Run a detailed home listing.','ls -lah /home/learner'),('Show a simple long-option listing.','ls --all')],
[Q('In cat notes.txt, what is notes.txt?', 'An operand and argument','A shell interpreter','An option flag','It is an argument naming the input target.'),Q('What does -- often indicate?', 'The end of options','Administrator mode','A background job','Many tools use -- to separate options from operands.')],
'Annotate every word in ls -lah ~/linux-lab. Check the manual for a program that accepts an option value.')
L(2,'quoting','Quoting and spaces','Control which characters the shell interprets.',
'''Words are not separated only by appearance::The shell splits unquoted text into words. touch my notes.txt typically names two files; touch "my notes.txt" names one. Quoting preserves a word boundary. Single quotes preserve literal content. Double quotes preserve spaces while still allowing variable expansion.

Escaping a character::A backslash can prevent a character from having its usual shell meaning. For example, my\\ notes.txt is one word in Bash. Quoting is usually clearer for long paths. Nested languages such as shell plus Python add another layer of quoting, so prefer scripts for complicated logic.

Do not execute data::Never build a command by concatenating untrusted text into a shell string. In Python, subprocess.run with an argument list and shell=False avoids a class of shell injection problems. It does not make the invoked program or its arguments inherently safe.''',
'''touch "my notes.txt"
printf '%s\\n' 'hello Linux' > "my notes.txt"
cat "my notes.txt"''', [('Create a filename containing a space.','touch "my notes.txt"'),('Read the filename as one argument.','cat "my notes.txt"')],
[Q('Which quotes normally allow $HOME expansion in Bash?', 'Double quotes','Single quotes','Neither type','Double quotes retain variable expansion while preserving whitespace.'),Q('Why pass a list to subprocess.run?', 'To avoid shell parsing of an assembled string','To grant root rights','To hide the program name','An argument list with shell=False bypasses shell interpretation.')],
'Create a file with a space in its name in your VM practice directory. Read it using quotes and again using an escaped space.')
L(2,'streams','Input, output and redirection','Route text deliberately between files and programs.',
'''Three standard streams::A process normally has standard input (descriptor 0), standard output (1) and standard error (2). Programs send normal results to stdout and diagnostics to stderr. Keeping these separate lets an automation consume results without confusing them with errors.

Overwrite or append::The shell processes > before the command runs, creating or truncating the destination. >> appends instead. A careless cat notes.txt > notes.txt can destroy its own input. Read into a different output file, inspect it, and only then replace the original when appropriate.

What the simulator supports::The lab implements >, >> and < for text files, plus stdout pipelines. It reports command errors in the terminal, but does not simulate descriptor duplication such as 2>&1. Use a VM for the separate stderr exercise below.''',
'''printf '%s\\n' 'first observation' > report.txt
printf '%s\\n' 'second observation' >> report.txt
cat < report.txt''', [('Write a first observation.','printf \'%s\\n\' \'first observation\' > report.txt'),('Append a second observation.','printf \'%s\\n\' \'second observation\' >> report.txt')],
[Q('What does > do to an existing destination?', 'Truncates it before the program runs','Always appends','Asks for a password','The shell opens and truncates the output destination before execution.'),Q('Which descriptor is standard error?', '2','0','1','Standard input is 0, output is 1, and error is 2.')],
'In a disposable directory, run ls missing-file > output.txt 2> error.txt. Compare the two files and explain why only one contains the diagnostic.')
L(2,'pipes','Pipes and small tools','Build a data flow from focused commands.',
'''A pipe connects streams::The | operator connects the stdout of one program to the stdin of another. It does not pass filenames unless the producer prints filenames and the consumer expects them. A pipeline works best when each tool has a clear contract about its input and output.

Read from left to right::cat logs/app.log | grep ERROR | wc -l reads a file, selects matching lines, then counts newline characters. grep ERROR logs/app.log | wc -l avoids the extra cat process. Both illustrate a useful data flow. Errors normally continue to stderr rather than flowing through the pipe.

Exit status can hide a failure::By default Bash uses the last pipeline command status. An early failure may be masked by a successful final command. In real scripts, consider set -o pipefail and explicit error handling. The simulator models stream output, not the complete Bash job-control or pipeline-status system.''',
'cat logs/app.log | grep ERROR | wc -l\ngrep ERROR logs/app.log | wc -l', [('Filter the application log.','grep ERROR logs/app.log'),('Count matching error lines.','grep ERROR logs/app.log | wc -l')],
[Q('What travels through a normal pipe?', 'The left command standard output','Its executable file','All system memory','A pipe carries a byte stream from stdout to stdin.'),Q('Why can a pipeline hide an earlier failure?', 'Its default status comes from the last command','Pipes always return zero','grep suppresses every error','Bash normally reports the status of the final pipeline command.')],
'Compare a valid grep pipeline and one with a missing input file. Inspect $? with and without set -o pipefail in a disposable Bash shell.')
L(2,'expansion','Variables, wildcards and expansion','Understand transformations before a program starts.',
'''Variables store text::NAME=value assigns a shell variable with no spaces around =. $NAME expands it. export marks a variable for inheritance by child processes; it does not update already-running processes or permanently edit login configuration. Environment variables are not a secure secret store by themselves.

Wildcards match names::An unquoted * matches names, ? matches a character and bracket expressions match sets. The shell usually expands these before starting the program. ls *.txt therefore receives matching names as arguments. A quoted "*.txt" remains literal, which is useful when find should perform its own matching.

Expansion is not regex::Shell globbing and regular expressions have different grammars. In a regex, . means any character and * repeats the preceding expression. In a glob, * itself means any sequence of characters. The lab supports simple variables and wildcard filenames; advanced Bash substitution belongs in VM practice.''',
'export TOPIC=Linux\necho "$TOPIC"\nls *.txt', [('Set a shell environment value.','export TOPIC=Linux'),('Expand the value in output.','echo "$TOPIC"')],
[Q('Who expands an unquoted *.txt in a shell command?', 'The shell','Always the kernel','The file contents','The shell replaces the pattern with matching pathnames before invocation.'),Q('Are glob syntax and regex syntax identical?', 'No, their pattern rules differ','Yes, in every context','Only for files owned by root','For example, glob * matches a sequence, while regex * repeats a prior item.')],
'Compare printf "%s\\n" *.txt with printf "%s\\n" "*.txt" in a VM directory containing several text files.')
L(2,'status','Exit status and conditional execution','Use success and failure as part of a workflow.',
'''Status is a separate result::A program returns an exit status in addition to text output. Zero conventionally means success; nonzero values have command-specific meanings. grep uses 1 for no matches and 2 for errors. A nonzero status is not always a crash.

Conditional operators::In Bash, A && B runs B only if A succeeds. A || B runs B only if A fails. A semicolon separates commands regardless of their status. This simulator deliberately supports one command or pipeline at a time; the conditional example is explained for use in a real shell.

Design for failure::Decide what a script should do when a required input is missing or a remote service is unavailable. Check prerequisites and use meaningful exit codes. Do not blindly retry a mutation, since a first request may have succeeded even if the response was lost.''',
'grep ERROR logs/app.log\necho $?\n# On a real Bash shell: mkdir new-case && cd new-case', [('Search for an absent pattern.','grep MISSING logs/app.log'),('Inspect the previous exit code.','echo $?')],
[Q('What does zero usually mean as an exit status?', 'Success','There was no printed output','Administrator rights','Status is independent of whether a command prints anything.'),Q('When does A && B run B?', 'When A returns success','When A prints a filename','Only when A fails','The && operator conditionally executes the second command on success.')],
'In a VM, run true && echo success, false || echo fallback and false; echo continued. Explain each result.')
L(2,'capstone','Field mission: log pipeline','Turn a log into a focused report.',
'''Your assignment::An application has produced mixed informational and error messages. Inspect its log, count error lines, and save just those errors in a separate report. Keep the original file intact.

Explain your decisions::Your note should describe which program filters, which program counts and which part of the syntax writes a file. Explain why repeating the same command with >> could duplicate a report. A reproducible command should make its overwrite or append behavior deliberate.''',
'grep ERROR logs/app.log > errors.txt\ncat errors.txt\ngrep ERROR logs/app.log | wc -l', [('Save filtered errors to a report.','grep ERROR logs/app.log > errors.txt'),('Read the report.','cat errors.txt'),('Count error events.','grep ERROR logs/app.log | wc -l'),('Check the exit status.','echo $?')],
[Q('Which symbol writes stdout to a file?', '>','|','$','Redirection sends stdout to a named destination.'),Q('Why use a different output filename?', 'To avoid truncating the input','To give the shell root rights','To encrypt the output','Opening the original input for overwrite can destroy it before reading.')],
'Recreate the report in a VM with sample data. Add a no-match case and decide whether it should create an empty report or stop your workflow.',True)

L(3,'create','Create files and directories','Build a workspace with deliberate names and structure.',
'''Directories organize relationships::mkdir creates a directory; mkdir -p also creates missing parents and succeeds if the directory already exists. Choose a small structure such as input, working and reports. Keeping originals separate from derived files reduces accidental overwrites and makes a workflow easier to explain.

Empty is different from missing::touch creates an empty file if the path does not exist. If it does exist, touch updates timestamps without erasing its contents. A zero-byte file can still have ownership, permissions and timestamps. A missing file has no directory entry to inspect.

Write text deliberately::printf gives predictable formatting and is preferable to relying on echo escape behavior. Its format string describes how values are printed. Use a fixed format and pass data as separate arguments; treating untrusted data as the format can produce unexpected output.''',
"mkdir -p project/reports\ntouch project/notes.txt\nprintf '%s\\n' 'case opened' > project/notes.txt",
[('Create a nested report directory.','mkdir -p project/reports'),('Create an empty notes file.','touch project/notes.txt')],
[Q('What happens when touch targets an existing file?', 'It updates timestamps','It erases the contents','It compresses the file','touch normally updates access and modification times.'),Q('What does mkdir -p add?', 'Creation of missing parent directories','Password protection','Printing the directory','The parents option creates needed intermediate directories.')],
'Create input, working and reports directories in a VM practice project. Add a README describing their purpose.')
L(3,'read','Read text without changing it','Choose a reader suited to the size and format of a file.',
'''Use a view that fits::cat prints a file or concatenates multiple files. less is an interactive pager for long text; q exits it. head and tail show a small beginning or end. tail -f follows a growing file on real Linux, but this lab provides a static snapshot.

Text is an interpretation::A filename extension is a clue, not proof of format. file examines signatures and other characteristics. Sending arbitrary binary data directly to a terminal can produce control characters. Use xxd for a hexadecimal view of unfamiliar bytes.

Count carefully::wc -l counts newline characters, which can differ from the number of apparent records when a final line lacks a newline or records span multiple lines. Pick a parser for the data format instead of assuming every line is a complete record.''',
'head -n 2 logs/app.log\ntail -n 2 logs/app.log\nwc -l logs/app.log',
[('Read the first two log lines.','head -n 2 logs/app.log'),('Read the last two log lines.','tail -n 2 logs/app.log')],
[Q('Which tool pages through long text interactively?', 'less','touch','mkdir','less lets a person navigate text without printing it all at once.'),Q('What does wc -l count?', 'Newline characters','Always JSON records','Nonempty words','Its line count is based on newline characters.')],
'Inspect a text file with cat, less, head and tail. Try file and xxd on a copied image without editing the original.')
L(3,'copy-move','Copy, move and remove','Understand what each filesystem change preserves.',
'''Copy creates another file::cp copies content to a destination. Metadata preservation depends on options and filesystem support; cp -p requests preservation of several attributes. Copying is not automatically a verified backup. Confirm the destination and compare hashes when content integrity matters.

Move changes location::mv renames a file within a filesystem, normally without copying the content. A cross-filesystem move generally copies and removes instead. Destination directories change how cp and mv interpret their final argument, so inspect the resulting path.

Removal has consequences::rm unlinks directory entries; ordinary command-line removal normally has no recycle bin. -i asks before each removal in common tools. The simulator only changes its virtual workspace; it implements rm for practice, while recursive deletion and device operations are intentionally unavailable.''',
'cp notes.txt copy.txt\nmv copy.txt renamed.txt\nls',
[('Copy the sample notes.','cp notes.txt copy.txt'),('Rename the copy.','mv copy.txt renamed.txt')],
[Q('Does cp always preserve every metadata field?', 'No, preservation depends on options and support','Yes, always','Only when filenames match','Content copying and metadata preservation are separate concerns.'),Q('What does rm normally do?', 'Unlinks a directory entry','Moves a file to a recycle bin','Encrypts the file','Recovery is not guaranteed, so verify a target before removing it.')],
'Copy and rename disposable files in your VM. Compare inode numbers with ls -i before and after a same-filesystem rename.')
L(3,'search','Find filenames and search contents','Choose find for paths and grep for text.',
'''Two different questions::find walks a directory tree and selects entries by properties such as name or type. grep searches text for matching lines. Looking for a filename is different from looking for a word inside files. Begin with the smallest relevant directory to avoid noise and permission errors.

Patterns need context::find . -type f -name "*.txt" lets find match the quoted glob. grep ERROR logs/app.log searches contents. grep -n adds line numbers; -i ignores case. Basic regular expressions are not the same as shell glob patterns.

Search results need interpretation::A matching line provides context to investigate, not a final diagnosis. Check nearby lines and timestamps. No matches can mean the term is absent, the wrong file was selected, the log rotated, or permissions prevented reading.''',
"find . -type f -name '*.txt'\ngrep -in error logs/app.log",
[('Find text filenames recursively.','find . -type f -name "*.txt"'),('Find error lines with line numbers.','grep -in error logs/app.log')],
[Q('Which tool searches file contents?', 'grep','cd','mkdir','grep selects lines whose text matches a pattern.'),Q('Why quote *.txt in find?', 'So find receives the pattern literally','To encrypt filenames','To search only hidden files','Quoting prevents the shell from expanding the pattern before find runs.')],
'Create several nested text files in a VM. Use find to locate names and grep -rn to locate a chosen phrase in their contents.')
L(3,'transform','Transform and summarize text','Filter fields, sort records and count repeated values.',
'''Build a clear transformation::sort orders lines; uniq removes adjacent duplicates, so sort | uniq is a common combination. uniq -c counts repetitions. Sorting depends on locale on a real system; set a documented locale when reproducible ordering matters.

Fields are a contract::cut selects simple delimiter-separated fields. It is not a full CSV parser: quoted commas and embedded newlines break naive splitting. awk supports field-based transformations, and sed edits streams. For structured CSV or JSON, use a real parser such as Python csv or json.

Keep derived output separate::Write transformations to a new report, inspect the result and record how it was produced. A pipeline that silently loses malformed records can be more dangerous than one that fails clearly. Preserve original inputs for comparison.''',
"sort names.txt | uniq -c\ncut -d ',' -f 1 data.csv",
[('Count repeated names after sorting.','sort names.txt | uniq -c'),('Select the first simple CSV field.','cut -d "," -f 1 data.csv')],
[Q('Why often sort before uniq?', 'uniq compares adjacent lines','sort encrypts duplicates','uniq only accepts sorted filenames','Sorting brings equal lines next to each other.'),Q('Which is appropriate for general CSV parsing?', 'Python csv module','A simple split on every comma','wc -l alone','CSV permits quoted delimiters and multiline fields that require a parser.')],
'Use Python csv.reader on a sample containing a quoted comma. Compare it with cut and explain the difference.')
L(3,'archives','Archives, links and backups','Distinguish packaging, compression and recoverability.',
'''An archive groups; compression shrinks::tar bundles entries and metadata into an archive. gzip compresses a stream. A .tar.gz often combines both operations. List an unfamiliar archive before extracting it, and extract into a fresh directory to avoid overwriting existing work or trusting unexpected paths.

Links are names with different behavior::A hard link is another directory entry for the same underlying file inode, usually within one filesystem. A symbolic link stores a path to a target and may become dangling. Copying or following links can change the scope of a backup or search.

A backup must restore::A second copy on the same disk does not protect against disk loss. Useful backups need appropriate separation, retention and a tested restore procedure. A hash checks content consistency, but not whether the right files were backed up or whether the backup is trustworthy.''',
'ls -l\nsha256sum notes.txt\ncp notes.txt backup.txt\nsha256sum backup.txt',
[('Inspect the sample archive listing.','tar -tf sample.tar'),('Fingerprint the sample notes.','sha256sum notes.txt')],
[Q('What is the difference between tar and gzip?', 'Archiving groups files; compression reduces size','Both always encrypt files','tar is a package manager','These are separate operations that can be combined.'),Q('What proves a backup is usable?', 'A successful tested restore','Its filename contains backup','It is on the same disk','Restoration exercises reveal missing data and broken recovery assumptions.')],
'In a VM, create a tar archive from disposable files, list it, restore it into a fresh directory and compare hashes.')
L(3,'capstone','Field mission: organize a case','Create a working copy and a reproducible error report.',
'''Your assignment::Organize a small case with separate working and report directories. Copy the sample application log into working, then derive a filtered error report. Keep the source log untouched.

Your handover::Record the source path, destination path, filter command and verification method. Another learner should be able to repeat your process and obtain the same report. Explain why a copied log is useful for practice but does not by itself establish a forensic chain of custody.''',
'mkdir -p project/working project/reports\ncp logs/app.log project/working/app.log\ngrep ERROR project/working/app.log > project/reports/errors.txt',
[('Create the working and report directories.','mkdir -p project/working project/reports'),('Copy the input log.','cp logs/app.log project/working/app.log'),('Generate the report.','grep ERROR project/working/app.log > project/reports/errors.txt'),('Inspect the generated report.','cat project/reports/errors.txt')],
[Q('Why keep an unchanged source?', 'To compare and reproduce derived results','To hide all errors','To grant write permission','Original data provides the baseline for checking transformations.'),Q('Which command finds filenames recursively?', 'find','cat','uniq','find walks a tree and tests entry properties.')],
'Rebuild this project on a VM. Write a README containing exact commands and a tested method for restoring the input.',True)

L(4,'identity','Users, groups and privilege','Read identity before interpreting access.',
'''Identity has numbers::Linux accounts have user IDs and group IDs. whoami reports the effective username; id reports identifiers and group memberships. Files store numeric ownership, which a system maps to names. A copied filesystem may show different names if account databases differ.

Groups make shared access manageable::A process has an effective user and group memberships used during access checks. Adding a user to a group does not necessarily update an already-running login session. Least privilege means granting the access needed for a task without making every tool an administrator.

Elevate only with a reason::sudo runs permitted commands under another identity, commonly root. sudo -l lists policy allowances on a configured system. Do not prefix a failing command with sudo before understanding the failure: elevated rights can turn a wrong path into a damaging change.''',
'whoami\nid\ngroups', [('Inspect numeric and named identity.','id'),('Inspect group memberships.','groups')],
[Q('What do files store as ownership identifiers?', 'Numeric user and group IDs','The terminal title','Only an email address','Account databases map numeric IDs to names.'),Q('What is least privilege?', 'Granting only the access needed','Running every tool as root','Removing every account','Limited access reduces accidental and unauthorized effects.')],
'Run id and groups on your VM. Read sudo -l if your account has sudo configured; do not change policy.')
L(4,'permissions','Read and change permissions','Translate read, write and execute into actual access.',
'''Nine bits with context::A listing such as -rw-r----- shows a regular file and permissions for owner, group and other. r is read, w is write and x is execute for a file. On a directory, r lists names, x permits traversal and w permits changing directory entries, usually together with x.

Numeric modes::Read is 4, write is 2 and execute is 1. Add them for each class: 600 gives owner read/write only; 640 adds group read; 755 gives owner full access and everyone else read/execute. chmod changes mode, not ownership. ACLs, mount options and security modules can impose additional rules.

Deletion is a directory operation::A read-only file may still be removable when the containing directory allows entry changes. The sticky bit adds special restrictions in shared directories such as /tmp. Do not use chmod 777 as a generic repair.''',
'ls -l notes.txt\nchmod 640 notes.txt\nstat notes.txt', [('Restrict sample notes to owner read/write.','chmod 600 notes.txt'),('Inspect the resulting metadata.','stat notes.txt')],
[Q('What does 640 grant the group?', 'Read only','Read and write','Execute only','The group digit 4 represents read.'),Q('Which permission allows directory traversal?', 'Execute','Read alone','Write alone','Directory execute permits looking up entries through that directory.')],
'Create a file and directory in your VM. Compare file execute with directory execute using only your own disposable paths.')
L(4,'processes','Processes, PIDs and signals','Connect running programs to their lifecycle.',
'''A process is an executing program::A PID identifies a process at a point in time; PIDs can be reused. A process has a parent, identity, open files and resource usage. ps gives a snapshot; top is a changing view. CPU percentages and memory figures need context and a time interval.

Signals communicate requests::kill sends a signal, despite its name. SIGTERM requests termination so a program can clean up. SIGKILL cannot be caught and prevents graceful cleanup. Check the process identity and ownership before signaling a real PID, especially in scripts where it may have exited and the PID may have been reused.

Foreground and background::A real shell can start a background job with & and manage jobs with jobs, fg and bg. This simulator shows a fixed process table and supports signaling its own teaching process; it does not create operating-system processes.''',
'ps -ef\ntop\nkill -TERM 120', [('Inspect the simulated process table.','ps -ef'),('Request termination of the lab worker.','kill -TERM 120')],
[Q('What does kill send?', 'A signal','Always SIGKILL','A package removal request','Its default signal is typically SIGTERM.'),Q('Why prefer SIGTERM before SIGKILL?', 'It allows graceful cleanup','It guarantees faster shutdown','It changes file ownership','A process may handle SIGTERM and close resources cleanly.')],
'Start sleep 300 in a VM terminal, identify that process in another terminal and send SIGTERM to the verified sleep PID.')
L(4,'resources','Storage, memory and resource pressure','Use the right measurement for the question.',
'''Measure different resources separately::free summarizes memory, df shows filesystem capacity and du estimates usage beneath paths. df and du can disagree because of open deleted files, snapshots, permissions or filesystem accounting. High memory use is not automatically bad: Linux uses available memory for cache.

Disks are not filesystems::lsblk shows block devices and their relationships. A disk can contain partitions; filesystems can live on partitions or other storage layers; mount points connect them to the directory tree. Device names can change between boots.

Diagnose before modifying::Record symptoms and compare multiple read-only observations. Formatting, partition editing and filesystem repair can destroy data and are outside the lab. Resource troubleshooting starts with identifying whether the pressure is CPU, memory, capacity, inode count or I/O latency.''',
'free -h\ndf -h\ndu -sh case\nlsblk', [('Inspect memory accounting.','free -h'),('Inspect filesystem space.','df -h')],
[Q('Which command reports mounted filesystem space?', 'df','whoami','chmod','df summarizes used and available space per filesystem.'),Q('Does high RAM use always indicate a leak?', 'No, cache and workload context matter','Yes, unused RAM is always best','Only on laptops','Linux uses memory for useful cache that can be reclaimed.')],
'Compare free -h, df -h, df -i and du -sh in a VM. Write the distinct question each command answers.')
L(4,'services','Services and system logs','Connect a service state with recorded events.',
'''Services run beyond one terminal::A service manager starts and supervises background programs. Many distributions use systemd; containers and other distributions may use a different init system. systemctl status gives current service information, while journalctl queries recorded events.

Read time and scope::A service can be active while individual requests fail. Logs can rotate or be limited by permissions and retention. Record the time range, service name and timezone when investigating. Avoid treating a single error line as proof of the root cause.

Changes need verification::On a VM, a restart can interrupt clients and erase useful transient context. Read status and recent logs first, make a targeted change, then check both service state and user-visible behavior. This lab only simulates status and log inspection.''',
'systemctl status nginx\njournalctl -n 5', [('Read the simulated service status.','systemctl status nginx'),('Read recent journal events.','journalctl -n 5')],
[Q('Does active service state prove every request works?', 'No, application-level checks are still needed','Yes, always','Only when a service uses TCP','A running process may still fail to serve requests correctly.'),Q('Why record the timezone of logs?', 'To correlate events accurately','To change file permissions','To compress journal files','Different clocks and timezone displays can otherwise misalign events.')],
'On a systemd VM, inspect one service with systemctl status and journalctl -u. Correlate a known event without restarting the service.')
L(4,'packages','Packages, repositories and updates','Understand the distribution software supply chain.',
'''Packages carry more than a binary::A package manager tracks versions, dependencies, installation scripts and file ownership. Debian-family distributions commonly use apt; Fedora uses dnf; Arch uses pacman. Installing a tool by name is not the same as trusting an arbitrary download with that name.

Index versus installed software::On apt systems, apt update refreshes repository metadata; apt upgrade changes installed package versions. Inspect the source repository and proposed changes. Signatures help verify repository authenticity but do not prove software is bug-free.

Keep environments reproducible::Record package versions and use project-specific Python virtual environments. A venv separates Python packages from the operating-system Python, reducing conflicts. The lab supports read-only apt list and apt show fixtures, not installing software on the host.''',
'apt list --installed\napt show python3', [('List simulated installed packages.','apt list --installed'),('Read the simulated Python package information.','apt show python3')],
[Q('What does apt update normally refresh?', 'Repository package metadata','Every installed package version','User passwords','Upgrading installed packages is a separate operation.'),Q('Why use a Python virtual environment?', 'To isolate project dependencies','To replace the Linux kernel','To grant administrator privileges','A venv keeps project package versions separate from system Python packages.')],
'In a disposable VM, inspect package sources and one installed package. Create a venv with python3 -m venv .venv and inspect its Python path.')
L(4,'capstone','Field mission: system triage','Create a read-only snapshot before proposing changes.',
'''Your assignment::A colleague reports that a service seems slow. Gather identity, process, storage and service observations. Resist diagnosing from a single metric. Summarize the next question you would ask based on the outputs.

A careful recommendation::Separate observed facts from hypotheses. Explain what additional evidence would confirm or reject your hypothesis. Your task is complete when another administrator can understand the snapshot without needing to rerun destructive troubleshooting steps.''',
'id\nps -ef\ndf -h\nsystemctl status nginx', [('Record identity.','id'),('Inspect running processes.','ps -ef'),('Inspect storage.','df -h'),('Inspect the service.','systemctl status nginx')],
[Q('What should precede an administrative change?', 'A focused diagnosis and baseline','chmod 777 on all files','A forced kill of every process','A baseline makes it possible to reason about cause and verify outcomes.'),Q('Which tool changes file modes?', 'chmod','chown','df','chmod edits permission bits; chown edits ownership.')],
'Create a VM triage report containing facts, hypotheses and next checks. Include one example of a metric that could be misleading without context.',True)

L(5,'layers','Packets, frames and layers','Follow encapsulation without confusing addresses.',
'''Data travels in layers::An application message is carried by a transport protocol such as TCP or UDP, then by IP packets, then by local-link frames such as Ethernet. Each layer solves a different problem. Encapsulation wraps one layer of data inside another; a packet capture may show several layers together.

Local and routed delivery::MAC addresses identify interfaces on a local link. IP addresses support delivery across routed networks. A router removes one link-layer wrapper and builds another for the next link. The source and destination MACs can change while an IP packet crosses networks.

A model is a tool::OSI and TCP/IP layer models help organize troubleshooting, but real implementations cross neat boundaries. Ask what observation a tool provides instead of memorizing a layer number alone. The lab network is entirely simulated and sends no traffic.''',
'ip addr\nip neigh', [('Inspect lab interface addresses.','ip addr'),('Inspect the local neighbor table.','ip neigh')],
[Q('Which address is used for local Ethernet delivery?', 'MAC address','TCP port','DNS name','Ethernet frames use link-layer source and destination MAC addresses.'),Q('Does a router normally preserve the same Ethernet frame end to end?', 'No, link-layer framing changes at each routed hop','Yes, on every network','Only if DNS is enabled','Routing moves IP packets between links with new link-layer wrappers.')],
'Draw the application, TCP/UDP, IP and Ethernet layers for a web request. Label which addresses belong to each layer.')
L(5,'ip','IP addressing and subnets','Separate host identity, network prefix and route.',
'''An address needs a prefix::IPv4 uses 32-bit addresses, commonly displayed as four decimal octets. A /24 prefix means the first 24 bits identify the network. In a conventional 192.0.2.0/24 subnet, .0 is the network address and .255 the broadcast address. Special cases such as /31 have different rules.

IPv6 and private space::IPv6 uses 128-bit hexadecimal addresses and does not use IPv4-style broadcast. Private IPv4 ranges support internal addressing; they are not a security boundary. Loopback addresses such as 127.0.0.1 refer to the local host.

Routing chooses a next hop::A route table selects a matching destination prefix, generally preferring the longest match. A default route handles destinations without a more specific route. An IP address alone does not prove a service is reachable or that a user has permission to access it.''',
'ip addr\nip route', [('Read the lab IPv4 prefix.','ip addr'),('Read the lab default route.','ip route')],
[Q('How many bits are in an IPv4 address?', '32','128','24','IPv4 has 32 bits; IPv6 has 128.'),Q('What does a default route handle?', 'Destinations without a more specific matching route','Only loopback traffic','Only DNS packets','Route lookup generally favors the longest matching prefix.')],
'Use Python ipaddress.ip_network to examine a documentation subnet such as 192.0.2.0/24. Inspect your VM routes without changing them.')
L(5,'transport','TCP, UDP and ports','Distinguish connection behavior from application meaning.',
'''TCP is a byte stream::TCP establishes a connection and provides ordered, reliable delivery of bytes with flow and congestion control. It does not preserve application message boundaries. Applications must frame their own messages and still handle timeouts and failed connections.

UDP is a datagram service::UDP sends individual messages without transport-level delivery or ordering guarantees. Applications may add their own reliability. DNS commonly uses UDP but also TCP; modern QUIC uses UDP and provides additional transport features. Avoid reducing protocols to one simplistic use case.

Ports identify endpoints::A socket combines protocol, address and port. A TCP connection is distinguished by its endpoint pair. Port 443 often carries HTTPS, but an open port alone does not prove the application or its security. ss -tuln shows numeric listening TCP and UDP sockets.''',
'ss -tuln', [('Inspect numeric listening sockets.','ss -tuln'),('Inspect the process view for context.','ps -ef')],
[Q('What does TCP provide?', 'An ordered reliable byte stream','Guaranteed application success','Encrypted data by default','TCP delivery properties do not imply application correctness or encryption.'),Q('Does port 443 prove a service is HTTPS?', 'No, it is a convention','Yes, ports enforce application types','Only for IPv6','Applications can listen on arbitrary ports.')],
'Inspect ss -tuln on your VM and explain each local listening address. Do not scan other devices.')
L(5,'dns','DNS and name resolution','Trace names to records without treating DNS as a directory.',
'''Names map to records::DNS is a distributed system of records. A records carry IPv4 addresses, AAAA records IPv6 addresses, CNAME records aliases and MX records mail routing information. A name may have multiple addresses or none. DNS does not identify which person operates a service.

Resolvers and caching::A client usually asks a recursive resolver, which uses cached answers or queries the hierarchy. TTL controls cache lifetime but does not guarantee every observer sees a change immediately. Local hosts files and application caches can affect resolution too.

Verify the question::dig shows the question, answers and metadata. Confirm the record type and resolver before drawing conclusions. A successful lookup only proves a resolution step succeeded; it does not test whether a TCP connection or web application works.''',
'dig example.com\ncat /etc/hosts', [('Read a simulated A-record answer.','dig example.com'),('Read local host mappings.','cat /etc/hosts')],
[Q('Which record type carries an IPv6 address?', 'AAAA','A','MX','AAAA records contain IPv6 addresses.'),Q('Does successful DNS resolution prove a website works?', 'No, transport and application checks remain','Yes, DNS checks every web page','Only if TTL is high','Name resolution is just one step in reaching a service.')],
'On your VM, query A and AAAA records for example.com. Note the resolver, answer type and TTL. These are public documentation examples.')
L(5,'http','HTTP, TLS and secure connections','Separate transport reachability from application responses.',
'''HTTP has explicit messages::A request contains a method, target, headers and sometimes a body. A response contains a status, headers and sometimes a body. Status classes summarize outcomes: 2xx success, 3xx redirection, 4xx client-side request issues and 5xx server-side failures.

TLS protects the channel::HTTPS uses TLS for encryption, integrity and server authentication under a trust model. Certificate validation checks identity and trust; disabling it removes a major protection. TLS does not prove that a site is honest or that its application has no vulnerabilities.

Test one layer at a time::curl -I requests headers with HEAD on typical HTTP servers. A timeout, certificate failure and HTTP 404 indicate different points of failure. SSH is a separate secure protocol; verify its host key against a trusted source on first connection.''',
'curl -I https://example.com\nssh -V', [('Inspect simulated HTTP headers.','curl -I https://example.com'),('Inspect the SSH client version without connecting.','ssh -V')],
[Q('What does a 404 response establish?', 'An HTTP server returned a not-found response','DNS must have failed','TLS is always disabled','An HTTP response means the exchange reached the HTTP layer.'),Q('What is lost when TLS certificate validation is disabled?', 'A key server identity check','All TCP sequence numbers','DNS caching','Encryption without trustworthy endpoint authentication can protect the wrong connection.')],
'Use curl -I https://example.com on a VM with internet access. Explain the difference between HTTP status and TLS validation.')
L(5,'packets','Read packet captures','Use saved observations to reconstruct a conversation.',
'''A capture has a viewpoint::A packet capture records traffic visible at a particular interface, time and configuration. Missing packets can reflect capture loss, filters, encryption or a different path. A capture is not an omniscient record of a network.

Read headers before payloads::Identify timestamps, endpoints, transport protocol and flags. A TCP SYN begins connection establishment; SYN-ACK responds; ACK acknowledges. Retransmissions suggest delivery issues but need context. Encrypted payloads do not reveal their application content just because they were captured.

Work from saved data::tcpdump -n -r sample.pcap reads a saved capture without reverse DNS lookups. Wireshark offers interactive decoding. The simulator renders a fixed teaching transcript from a fixture, not a real PCAP decoder. Use a provided or self-owned sample in a VM for actual packet analysis.''',
'tcpdump -n -r sample.pcap', [('Read the simulated saved packet transcript.','tcpdump -n -r sample.pcap'),('Read the capture scenario notes.','cat case/network-notes.txt')],
[Q('What does tcpdump -r do?', 'Reads an existing capture','Resets the router','Repairs a capture interface','The -r option reads packets from a file.'),Q('Can a capture prove no traffic occurred elsewhere?', 'No, its visibility is limited','Yes, if it has timestamps','Only when opened in Wireshark','The observation point and capture configuration constrain the evidence.')],
'Open a trusted public training PCAP in Wireshark or capture only your VM loopback traffic. Identify endpoints and one conversation.')
L(5,'capstone','Field mission: connectivity triage','Build a layered explanation of a connection.',
'''Your assignment::A browser cannot reach an application. Collect interface, route, resolver and HTTP observations in order. State what each successful step would establish and what would remain untested.

Make your diagnosis bounded::This lab provides consistent sample output. In a real incident, test the reported destination and compare the failing client with a working one. Do not infer that every user can connect merely because one request succeeds.''',
'ip addr\nip route\ndig example.com\ncurl -I https://example.com', [('Inspect local addressing.','ip addr'),('Inspect the route.','ip route'),('Inspect DNS.','dig example.com'),('Inspect HTTP headers.','curl -I https://example.com')],
[Q('Which test directly inspects DNS records?', 'dig','chmod','free','dig queries DNS and displays record information.'),Q('Why troubleshoot in layers?', 'To narrow where a failure occurs','To avoid collecting observations','To guarantee the first test fixes it','Layered checks separate local addressing, routing, resolution and application behavior.')],
'Write a troubleshooting decision tree. Include DNS failure, connection refusal, TLS failure and HTTP 500 as distinct branches.',True)

L(6,'risk','Threats, vulnerabilities and risk','Use precise language to prioritize protection.',
'''Different words answer different questions::An asset is something of value. A threat is a possible harmful actor or event. A vulnerability is a weakness. An exploit takes advantage of a weakness. Risk considers likelihood and impact in a specific context; a vulnerability score alone does not describe all business risk.

Exposure changes priorities::An internet-facing service with sensitive data may deserve attention before an isolated training machine with the same software flaw. Existing controls, exploitability and business impact affect remediation priority. Document assumptions instead of inventing certainty.

Scope comes first::A security assessment needs defined systems, methods, timing, authorization and reporting arrangements. This course uses local teaching fixtures. No lesson sends attack traffic or tests external targets; real practice should remain inside systems you own or are explicitly authorized to assess.''',
'cat case/scope.txt\ncat case/findings.txt', [('Read the assessment scope.','cat case/scope.txt'),('Read the sample finding.','cat case/findings.txt')],
[Q('What is a vulnerability?', 'A weakness that could be exploited','Every valuable asset','A guarantee of compromise','A weakness can exist without having been exploited.'),Q('What influences risk besides technical severity?', 'Exposure, likelihood and impact','Only the finding title','Only the number of screenshots','Risk depends on the environment and consequences.')],
'Create a threat model for your own VM: list assets, likely threats, weaknesses, existing controls and residual risks.')
L(6,'authentication','Authentication, authorization and sessions','Separate identity proof from permission.',
'''Identity and access are separate::Authentication checks a claimed identity. Authorization decides what that identity may do. A successful login must not grant access to every record or administrative function. Session management preserves authenticated state and must handle expiry, revocation and token protection.

Stronger factors::Passwords are knowledge factors; hardware tokens are possession factors; biometrics are inherence factors. Two passwords are not two distinct factors. Phishing-resistant authentication uses protocols that bind authentication to the intended service, such as passkeys under appropriate deployment.

Secrets need careful handling::Do not place passwords in shell commands that may enter history or process listings. Use password managers, appropriate storage mechanisms and short-lived credentials where possible. The lab auth log is synthetic and contains no real credentials.''',
'cat logs/auth.log\nid', [('Read the synthetic login events.','cat logs/auth.log'),('Inspect the account identity.','id')],
[Q('What does authorization decide?', 'Which actions an identity may perform','Whether a password was typed correctly','How large a file is','Authentication establishes identity; authorization controls actions.'),Q('Are two passwords two distinct authentication factors?', 'No, both are knowledge factors','Yes, any two secrets qualify','Only if one is long','Multiple secrets of the same factor type are not distinct factor categories.')],
'Write an access matrix for a fictional notes app with reader, editor and administrator roles. Include session expiry behavior.')
L(6,'crypto','Encryption, hashing and signatures','Choose the right primitive for the job.',
'''Confidentiality and fingerprints::Encryption protects confidentiality using a key and can be reversed with the appropriate key. A cryptographic hash maps bytes to a fixed-length digest and is not designed to be reversed. Hashing is not encryption. A bare hash does not prove who supplied the data.

Authenticity needs trust::An HMAC combines a secret key with a hash-based construction to authenticate data among parties sharing that key. Digital signatures use a private key to sign and a public key to verify. Verification still requires a trustworthy association between the public key and its claimed owner.

Passwords are special::Password storage should use a salted password-hashing scheme with an appropriate work factor, such as Argon2id. Fast general-purpose SHA-256 is useful for file integrity, not sufficient by itself for password storage. Do not invent cryptographic protocols.''',
'sha256sum notes.txt\nsha256sum case/evidence.txt', [('Hash a text file.','sha256sum notes.txt'),('Hash the evidence fixture.','sha256sum case/evidence.txt')],
[Q('Is SHA-256 encryption?', 'No, it is a cryptographic hash','Yes, with a public key','Only for text files','A hash is a digest, not a reversible confidentiality mechanism.'),Q('What is appropriate for password storage?', 'A salted password hash with a work factor','Plain SHA-256 without a salt','Reversible encoding such as Base64','Password-specific schemes resist large-scale guessing better than fast bare hashes.')],
'Use Python hashlib to hash two strings differing by one byte. Explain why matching digests alone do not establish authorship.')
L(6,'hardening','Hardening and least privilege','Reduce attack surface with verifiable controls.',
'''Reduce unnecessary exposure::Hardening includes removing unused services, patching supported software, limiting network reachability and using appropriate permissions. A baseline should reflect the machine purpose. Disabling a feature without understanding dependencies can create outages rather than useful protection.

Defense uses multiple layers::File permissions, service identities, network filtering, authentication and monitoring address different failure modes. A firewall does not replace authentication, and authentication does not replace secure application logic. Test controls with both allowed and denied cases.

Record and recover::Back up configuration before changing it, keep a recovery path and verify application behavior afterward. A configuration screenshot alone is weaker than evidence that a control actually works. The simulator changes only file modes in its own virtual state.''',
'ls -l notes.txt\nchmod 600 notes.txt\nss -tuln', [('Apply owner-only permissions to sample notes.','chmod 600 notes.txt'),('Inspect the lab listening sockets.','ss -tuln')],
[Q('Does a firewall replace application authentication?', 'No, they address different controls','Yes, if all ports are documented','Only for HTTPS','Network reachability and user identity are separate security concerns.'),Q('How should a control be verified?', 'With expected allowed and denied behavior','Only by its configuration name','By deleting all logs','Behavioral checks reveal whether policy is actually enforced.')],
'Write a VM hardening checklist with a reason, verification step and rollback step for each proposed change.')
L(6,'assessment','A security assessment workflow','Turn observations into reproducible findings.',
'''Plan, inspect, validate, report::Start with authorized scope and asset inventory. Review configuration and known software versions. Validate suspected weaknesses with the least intrusive method that answers the question. A scanner result is a lead, not automatic proof of exploitability.

A useful finding::Describe the affected asset, condition, evidence, impact, severity rationale and remediation. Include prerequisites and limitations. Avoid including unnecessary personal information or secrets. Reproduction steps should be enough for an authorized maintainer to verify the issue.

Close the loop::After remediation, retest the original condition and relevant regression behavior. Mark the finding fixed, partially fixed, accepted or unresolved with supporting evidence. An assessment is a point-in-time result rather than a promise of permanent security.''',
'cat case/scope.txt\ncat case/findings.txt\ncat case/remediation.txt', [('Read the defined scope.','cat case/scope.txt'),('Review the proposed remediation.','cat case/remediation.txt')],
[Q('Is a scanner alert a fully validated finding?', 'No, it needs contextual verification','Yes, every alert is exploitable','Only when printed in red','Tools can produce false positives and incomplete context.'),Q('What should follow a remediation?', 'Retest the original issue and relevant behavior','Delete the original evidence','Assume the patch name proves success','Retesting verifies whether the fix addressed the demonstrated condition.')],
'Write a finding for a deliberately over-permissive practice file. Include evidence, impact, remediation and a retest plan.')
L(6,'incident','Recognize and respond to incidents','Preserve useful evidence while limiting harm.',
'''Triage is not attribution::A failed login, unusual process or outbound connection may be benign or malicious. Correlate observations against a baseline and document uncertainty. A username or IP address is not sufficient to attribute a real person.

Contain with a plan::Incident response often includes preparation, detection, analysis, containment, eradication, recovery and lessons learned. Actions overlap and depend on the environment. Restarting or deleting suspicious files can remove volatile evidence; balance preservation with business and safety needs under an incident plan.

Make a timeline::Record when an event occurred, when it was observed, the source clock and timezone. Keep original logs, collect necessary context and separate facts from hypotheses. This lesson uses a fictional auth log for interpretation, not a detection product.''',
'grep Failed logs/auth.log\ncat logs/auth.log', [('Find failed-login events.','grep Failed logs/auth.log'),('Read the full context.','cat logs/auth.log')],
[Q('Does a failed login alone prove a breach?', 'No, further evidence is required','Yes, always','Only if it happened at night','A failed attempt is an observation that needs context.'),Q('Why document clock and timezone?', 'To correlate sources without misordering events','To grant administrator access','To make hashes shorter','Time interpretation affects reconstruction of incident sequence.')],
'Build a timeline from the synthetic auth log. Label facts, hypotheses and the extra evidence needed for each hypothesis.')
L(6,'capstone','Field mission: security review','Deliver a scoped, evidence-backed finding.',
'''Your assignment::Review the fictional lab scope, inspect sample notes permissions and read the synthetic authentication events. Apply a limited permission improvement and explain what it addresses.

The review document::Use the notes panel to draft a finding with condition, evidence, impact, fix and verification. State what the change does not establish: owner-only file access does not prove the whole system is secure. Keep incident interpretation distinct from hardening work.''',
'cat case/scope.txt\nls -l notes.txt\nchmod 600 notes.txt\nstat notes.txt', [('Read scope.','cat case/scope.txt'),('Inspect permissions.','ls -l notes.txt'),('Restrict the sample file.','chmod 600 notes.txt'),('Verify the new mode.','stat notes.txt')],
[Q('What makes a finding reproducible?', 'Specific condition, evidence and verification steps','An alarming title alone','An unexplained severity number','Another authorized reviewer should be able to verify the described condition.'),Q('What does chmod 600 establish?', 'Owner read/write permission bits on the file','Complete system security','Encryption at rest','Permissions are one control, subject to other access mechanisms and privileges.')],
'Write a complete review of your disposable VM practice directory. Include one verified issue, a targeted fix and a retest result.',True)

L(7,'principles','Forensic thinking and evidence','Separate preservation, observation and interpretation.',
'''A defensible process::Digital forensics examines data to answer questions with documented methods. Start with authority, scope and a clear question. Preserve source material, record acquisition details and work from verified copies where appropriate. A technically correct observation can still be misleading without context.

Chain of custody::Document who handled an item, when, why, where it was stored and how it was protected. Hashes support integrity checks but do not replace this record. An identical hash does not prove the source was collected lawfully or that the original content was truthful.

State limitations::Tools and fixtures can omit artifacts. A result should describe the method, version, input and uncertainty. Absence of a recovered artifact is not proof an event never occurred. The course fixtures are deliberately small and synthetic, not real case evidence.''',
'cat case/custody.txt\ncat case/scope.txt', [('Read the sample custody record.','cat case/custody.txt'),('Read the case scope.','cat case/scope.txt')],
[Q('Does a hash replace chain-of-custody documentation?', 'No, they answer different questions','Yes, a digest records every handler','Only if it is SHA-256','A hash checks bytes; custody records handling and control.'),Q('What should a forensic conclusion include?', 'Methods, evidence and limitations','Only the strongest suspicion','A tool screenshot without context','Transparent limitations help others assess the reasoning.')],
'Draft an evidence intake form with item identifier, authority, source, handler, timestamps, hashes, storage and transfers.')
L(7,'hashing','Hash and verify evidence','Use digests to test byte-for-byte consistency.',
'''What is actually hashed::A file digest is calculated from file content bytes, not normally its filename or filesystem timestamps. Renaming a file leaves its content hash unchanged. Altering a newline or encoding may change it. Use binary mode in Python to avoid text transformations.

Verification is a comparison::Hash the source and acquired copy using the same algorithm, then compare results. Matching SHA-256 digests provide strong evidence of matching bytes under normal assumptions. They do not establish authenticity without a trusted baseline or acquisition process.

Record the result::Store the algorithm, digest, item identifier, tool and acquisition context. A checksum manifest is useful for collections, but protect the manifest from unauthorized change. Legacy MD5 has collision weaknesses and should not be the sole integrity mechanism for adversarial evidence.''',
'cp case/evidence.txt case/working.txt\nsha256sum case/evidence.txt\nsha256sum case/working.txt',
[('Copy the synthetic evidence.','cp case/evidence.txt case/working.txt'),('Hash the source.','sha256sum case/evidence.txt'),('Hash the copy.','sha256sum case/working.txt')],
[Q('Does renaming a file usually change its content hash?', 'No, the content bytes are unchanged','Yes, the path is always hashed','Only on Linux','A content hash does not normally incorporate the filename.'),Q('Why read evidence in binary mode when hashing in Python?', 'To hash exact bytes without text conversion','To encrypt the file','To ignore all newline bytes','Text decoding and newline translation can change the byte representation.')],
'Hash a disposable file in Python and sha256sum. Rename it, then alter one byte and compare the two kinds of change.')
L(7,'metadata','Metadata, timestamps and file signatures','Treat descriptive fields as clues with limitations.',
'''Metadata has several sources::Filesystem metadata includes size, permissions and timestamps. Embedded metadata may include a document author, camera model or GPS location. These fields can be missing, edited or misleading. file estimates format; exiftool reads many embedded formats.

Times have specific meanings::mtime concerns content modification; ctime concerns inode metadata change, not creation. atime concerns access and may be suppressed or delayed by mount policy. Birth time is filesystem-dependent. Copying, extraction and tool behavior can affect timestamps.

Corroborate instead of overclaiming::A file extension is a name, not a signature. A matching signature is stronger evidence about a format, but a parser still needs to validate structure. Compare metadata with logs, surrounding artifacts and acquisition history before inferring a timeline.''',
'stat case/evidence.txt\nfile case/evidence.txt\nexiftool photo.jpg', [('Inspect filesystem metadata.','stat case/evidence.txt'),('Read synthetic embedded image metadata.','exiftool photo.jpg')],
[Q('What does Linux ctime normally represent?', 'Inode status change time','Guaranteed creation time','Camera capture time','ctime changes with inode metadata changes and is not a general creation timestamp.'),Q('Is embedded metadata always truthful?', 'No, it can be altered or absent','Yes, camera fields are immutable','Only if the extension is JPG','Metadata is evidence to corroborate, not automatic ground truth.')],
'Inspect a copied personal test photo with exiftool if available. List which fields are embedded and which come from the filesystem.')
L(7,'acquisition','Logical and physical acquisition','Choose collection scope without altering the original.',
'''Acquisition has tradeoffs::Logical acquisition collects selected files through filesystem interfaces. Physical imaging attempts to copy addressable storage, potentially including unallocated areas. Encryption, device controllers, permissions and damaged media can limit what is accessible. Neither method automatically captures every relevant state.

Protect source material::Write blockers and read-only handling can reduce changes where appropriate. Live collection changes a running system and may be necessary for volatile data; document those effects. Never run repair tools on original evidence as a casual preparation step.

Practice without devices::The lab copies a synthetic text item and hashes both copies. This demonstrates verification, not block-device imaging. Real imaging tools can overwrite disks if source and destination are reversed. Device acquisition requires supervised planning, validated tooling and disposable training media.''',
'cp case/evidence.txt case/acquired.txt\nsha256sum case/evidence.txt case/acquired.txt', [('Acquire a logical teaching copy.','cp case/evidence.txt case/acquired.txt'),('Verify source and acquired bytes.','sha256sum case/evidence.txt case/acquired.txt')],
[Q('What can physical imaging include beyond selected files?', 'Addressable unallocated storage areas','Every lost byte with certainty','All remote cloud accounts','The scope can include sectors not represented by currently allocated files.'),Q('Does live collection leave a system completely unchanged?', 'No, effects must be documented','Yes, if only one command is run','Only if the terminal is closed','Running tools changes memory and can affect disk and logs.')],
'Write a collection plan for a fictional USB image. Specify authority, source protection, destination capacity, verification and custody without running a device writer.')
L(7,'artifacts','Artifacts and timeline reconstruction','Correlate logs and content without overstating attribution.',
'''An artifact is a trace::Logs, browser databases, shell history and document metadata can record activity. Each has a format, retention policy and interpretation limits. Shell history may omit timestamps or commands; a file access time may not mean a person read it.

Normalize time carefully::Record source timestamp format, timezone, clock drift and precision before merging events. Preserve original timestamps alongside normalized values. Two events with identical displayed seconds may still have an uncertain ordering.

Build and test a hypothesis::Start from observations, propose an explanation and look for corroborating or contradicting evidence. Account names, hostnames and network addresses identify technical contexts, not necessarily human actors. Use precise statements such as "the log records a login for learner" rather than unsupported personal attribution.''',
'cat logs/auth.log\ncat case/timeline.csv\ngrep Accepted logs/auth.log', [('Read the timeline fixture.','cat case/timeline.csv'),('Locate accepted-login artifacts.','grep Accepted logs/auth.log')],
[Q('Why keep original timestamps with normalized ones?', 'To preserve interpretation context and audit conversion','To make all events occur at once','To change file ownership','Normalization can introduce mistakes; original values support review.'),Q('Does a username in a log prove who was at the keyboard?', 'No, attribution requires more evidence','Yes, account names are legal identities','Only if the event is successful','Credentials, automation and shared access can complicate attribution.')],
'Build a timeline from the supplied text fixtures. Include source, original time, normalized time, observation and confidence for each event.')
L(7,'reporting','Analysis tools and a defensible report','Make findings independently reviewable.',
'''Different tools answer different questions::xxd exposes bytes, strings extracts printable sequences and exiftool interprets metadata. Autopsy supports disk-oriented analysis; Volatility supports memory analysis with version and platform constraints. A tool name does not guarantee an artifact is parsed correctly.

Validate important observations::Cross-check critical results with another method or a known test fixture. Record tool versions and relevant settings. A printable string found in binary data does not prove the associated feature ran or that a person typed it.

Write the reasoning chain::A report should state the question, evidence received, methods, observations, interpretation, limitations and conclusions. Include reproducible commands or settings and relevant hashes. Keep sensitive content limited to what the report needs.''',
'xxd -l 64 case/evidence.txt\nstrings case/evidence.txt', [('Inspect a byte-level view.','xxd -l 64 case/evidence.txt'),('Extract printable sequences.','strings case/evidence.txt')],
[Q('Does strings prove a program executed?', 'No, it only extracts printable sequences','Yes, all strings are execution logs','Only for ASCII programs','A byte sequence can exist without being executed or used.'),Q('Why cross-check a critical tool result?', 'To detect parsing or interpretation errors','To guarantee a preferred conclusion','To avoid recording the method','Independent verification improves confidence in the observation.')],
'Write a short report for the synthetic evidence. Include the exact bytes or lines supporting each observation and a limitations paragraph.')
L(7,'capstone','Field mission: evidence handover','Preserve, verify, inspect and document a synthetic item.',
'''Your assignment::Read the custody fixture, acquire a working copy of the evidence item, compare digests and inspect metadata. Keep the original intact. Your notes should provide enough information for a second reviewer to repeat the checks.

Handover package::Include the item path, acquisition method, SHA-256 values, observations and limitations. Explain why the classroom copy is not a physical disk image, and why a digest does not prove who authored the contents.''',
'cat case/custody.txt\ncp case/evidence.txt case/working.txt\nsha256sum case/evidence.txt case/working.txt\nstat case/working.txt', [('Read custody.','cat case/custody.txt'),('Make a working copy.','cp case/evidence.txt case/working.txt'),('Verify both digests.','sha256sum case/evidence.txt case/working.txt'),('Inspect working-copy metadata.','stat case/working.txt')],
[Q('What does a matching SHA-256 comparison support?', 'Consistency of the compared content bytes','The identity of the author','The legality of acquisition','Content integrity and provenance are distinct questions.'),Q('Which should you analyze by default when possible?', 'A verified working copy','The only original with write access','An unrecorded transformed export','Working copies reduce accidental alteration of source material.')],
'Create a complete synthetic case folder on a VM, with original, working copy, checksum manifest, custody log and a concise report.',True)

L(8,'bash','Bash scripts and variables','Turn a sequence of commands into a readable program.',
'''A script is an interface::A Bash script contains commands, variables and control flow. A shebang such as #!/usr/bin/env bash selects an interpreter when an executable script is launched directly. Running bash script.sh selects Bash explicitly. Execution bits and interpreter choice are separate concerns.

Quote data::Use "$variable" when passing a value as one argument. Validate input and make overwrite behavior clear. set -u can catch unset variables and set -o pipefail can surface pipeline failures, but no set option replaces deliberate error handling. set -e has context-dependent behavior.

Learn in two environments::The simulator can display the bundled script and run curated teaching demos. It does not execute arbitrary Bash or provide a complete shell grammar. Write and test your own scripts in a disposable Linux VM using the real-practice instructions.''',
'cat scripts/report.sh\nbash scripts/report.sh', [('Read the bundled Bash example.','cat scripts/report.sh'),('Run the curated report demonstration.','bash scripts/report.sh')],
[Q('What is a shebang used for?', 'Selecting an interpreter for direct execution','Granting root rights','Encrypting a script','The operating system uses the shebang when launching a script directly.'),Q('Why quote "$variable"?', 'To preserve its value as one argument','To disable every expansion','To add execute permission','Double quotes prevent word splitting and glob expansion of the expanded value in ordinary argument contexts.')],
'In a VM, write a Bash script that accepts a log filename, checks readability and reports ERROR lines. Test a path containing spaces and a missing file.')
L(8,'control-flow','Conditions, loops and failure handling','Make repeated work explicit and bounded.',
'''Conditions test assumptions::if chooses a branch using a command exit status. test or [ can check file properties; Bash [[ has additional behavior. Keep conditions readable and account for missing, empty and malformed inputs instead of handling only the happy path.

Loops need safe inputs::for iterates values and while repeats while a condition succeeds. In a real shell, use while IFS= read -r line for line-oriented text, with care for a final line lacking a newline. Do not parse ls output to iterate filenames; filenames can contain spaces and newlines.

Design a failure contract::Choose when to stop, continue, retry or roll back. Log enough context to explain a failure without exposing secrets. A retry must consider whether the action is idempotent, meaning repeated requests have the same intended effect as one.''',
'cat scripts/check-files.sh\nbash scripts/check-files.sh', [('Read a loop and condition example.','cat scripts/check-files.sh'),('Run its curated demonstration.','bash scripts/check-files.sh')],
[Q('What does idempotent mean for an operation?', 'Repeating it has the same intended effect as once','It always runs in parallel','It never returns an error','Idempotence helps make retries safer, though external conditions can still matter.'),Q('Why avoid parsing ls output for filenames?', 'Filenames and formatting can break text assumptions','ls always deletes files','It requires a network connection','Use suitable APIs or safe filename handling instead.')],
'Write a VM Bash script that loops over quoted arguments and reports whether each is a readable regular file. Test spaces, empty inputs and missing paths.')
L(8,'python','Python for filesystem automation','Use standard-library APIs rather than assembling shell strings.',
'''Work with paths as data::pathlib.Path represents filesystem paths and provides methods for reading, writing and iterating. Specify text encodings explicitly. Read binary data for hashing. A script should accept input paths, validate them and avoid silently overwriting valuable output.

Use structured APIs::csv and json parse structured formats. hashlib computes digests. argparse creates a command-line interface. subprocess.run can invoke other tools with an argument list, check=True and a timeout; avoid shell=True for untrusted input.

Test outside this simulator::The lab includes a readable Python script and a curated execution result. Arbitrary code entered in the simulated terminal is not executed. Use your VM venv to edit and run Python, and test malformed data, missing paths and permission errors.''',
'cat scripts/analyze.py\npython3 scripts/analyze.py', [('Read the Python analyzer.','cat scripts/analyze.py'),('Run the curated analyzer demonstration.','python3 scripts/analyze.py')],
[Q('Which module provides object-oriented filesystem paths?', 'pathlib','socket alone','random','pathlib.Path offers filesystem-oriented path operations.'),Q('What does subprocess.run(..., check=True) do on a nonzero exit?', 'Raises CalledProcessError','Silently treats it as success','Automatically retries as root','Explicit failure propagation helps the caller handle unsuccessful commands.')],
'Write a Python CLI using argparse and pathlib to count ERROR lines. Test UTF-8 text, a missing file and an output path that already exists.')
L(8,'data','JSON, CSV and reproducible reports','Preserve data types and schema through automation.',
'''Structure matters::JSON encodes objects, arrays, strings, numbers, booleans and null. CSV is a table-oriented text format with dialect and quoting rules. A parser preserves these rules better than ad hoc text splitting. Validate required fields and handle unexpected types.

Define a report contract::Specify input encoding, columns, filters, timezone assumptions and output schema. Deterministic ordering makes changes easier to review. Include a tool version or schema version when future readers need to interpret the output.

Do not lose errors::Malformed records should be rejected or reported under a documented policy. A report that drops unknown values silently may look clean while hiding important events. Keep source data separate and test edge cases before scheduling the workflow.''',
'cat inventory.json\ncat inventory.json | jq .\ncat data.csv', [('Pretty-print the JSON fixture.','cat inventory.json | jq .'),('Read the CSV fixture.','cat data.csv')],
[Q('What should a report contract specify?', 'Input assumptions and output schema','Only its filename color','Only the editor used','Documented formats and assumptions make outputs reproducible.'),Q('How should malformed records be handled?', 'With an explicit reject or reporting policy','Always ignored silently','Converted to empty successful events','Visible failure handling prevents a misleadingly clean report.')],
'Extend your Python analyzer to emit JSON with a schema version, input path and error count. Add a test for malformed or missing input.')
L(8,'git','Git commits and working trees','Track meaningful snapshots of your project.',
'''Three states to understand::The working tree contains editable files. The index stages the next snapshot. A commit records a snapshot and metadata in repository history. git status shows state; git diff shows unstaged changes; git diff --staged shows staged changes. Git is not a backup of ignored or untracked files.

Commit deliberately::git add selects content for a commit. Review staged changes, then write a message describing the reason for the change. Never commit credentials or private evidence. Removing a secret in a later commit does not erase it from history; rotate exposed credentials.

Simulation limits::The lab models init, status, add, commit and log for its virtual files. It is a teaching model, not the Git implementation. Use real Git in a VM for branches, merges, remotes and collaboration.''',
'git init\ngit status\ngit add notes.txt\ngit commit -m "Record lab notes"\ngit log --oneline',
[('Initialize the virtual repository.','git init'),('Stage sample notes.','git add notes.txt'),('Commit the staged snapshot.','git commit -m "Record lab notes"')],
[Q('What does git add update?', 'The staging index','The remote server automatically','The kernel package list','The index determines the content of the next commit.'),Q('Does deleting a secret in a later commit remove it from history?', 'No, rotate it and address history appropriately','Yes, always','Only if the filename changes','Earlier commits may retain the secret and existing clones may keep it.')],
'Initialize a real Git repository in a VM project. Make two commits, inspect status and diff, create a feature branch and merge a small change.')
L(8,'workflows','Scheduling, testing and repeatable workflows','Automate only a process you can observe and recover.',
'''Scheduling changes the environment::cron jobs and systemd timers may have a different PATH, working directory and environment from your terminal. Use explicit paths, capture diagnostics and prevent unwanted overlapping runs. Timezone and daylight-saving behavior need a documented policy.

Test the failure paths::A useful automation test covers missing input, malformed data, permission failures and partial output. Write temporary output and replace the final result only after successful validation when appropriate. Keep operations idempotent where possible and use bounded retries.

Observe and maintain::A workflow needs success signals, failure alerts, logs and a recovery process. A schedule alone does not prove work completed. Version the code and configuration, record dependency versions and periodically verify that outputs remain useful.''',
'cat scripts/workflow.txt\npython3 scripts/analyze.py', [('Read the workflow plan.','cat scripts/workflow.txt'),('Verify the curated analyzer result.','python3 scripts/analyze.py')],
[Q('Why can a script work interactively but fail under cron?', 'Its environment or working directory may differ','cron always disables Python','Scheduled files have no permissions','Schedulers often supply a minimal environment and different execution context.'),Q('What should be tested besides successful input?', 'Missing data, malformed input and partial failure','Only the button color','Only the shortest filename','Failure-path tests improve reliability when conditions change.')],
'Create a VM workflow plan with explicit input/output paths, logging, a non-overlap strategy, failure behavior and a manual recovery procedure.')
L(8,'capstone','Final project: a repeatable Linux report','Bring the eight modules together in one documented workflow.',
'''Your assignment::Use the bundled Python analyzer, inspect its structured output and record your notes in a virtual Git commit. Relate each action to the earlier modules: paths, streams, permissions, logs, integrity and reproducibility.

Build the real version::For the full independent project, implement a Python CLI on a Linux VM that inventories a chosen practice directory, hashes regular files and summarizes a synthetic log. Produce JSON and a readable report. Exclude secrets, handle errors and document every assumption.

Definition of done::Your project has source code, a README, sample input, expected output and meaningful tests. A fresh venv can run it from documented commands. Include a Git history with focused commits and a scheduling plan with observable success and failure. This app awards completion for its guided work; the independent project is self-assessed.''',
'python3 scripts/analyze.py\ncat report.json\ngit init\ngit add report.json\ngit commit -m "Add reproducible report"',
[('Run the analyzer demonstration.','python3 scripts/analyze.py'),('Inspect the generated JSON report.','cat report.json'),('Initialize version tracking.','git init'),('Stage the generated report.','git add report.json'),('Record a report snapshot.','git commit -m "Add reproducible report"')],
[Q('What makes an automation reproducible?', 'Documented inputs, versions, behavior and verification','A schedule with no logs','Running everything with sudo','Reproducibility requires enough context to repeat and check the result.'),Q('What does this guided certificate demonstrate?', 'Completion of the app lessons, labs and checks','A professional security certification','That every real system is secure','Course completion is a learning milestone, not independent professional accreditation.')],
'Build the full Python CLI described above. Have another person follow the README in a fresh VM and report any missing steps.',True)

BY_ID = {l['id']:l for l in LESSONS}

def public_curriculum():
    return {'modules':[dict(id=m[0],title=m[1],description=m[2],topics=m[3],icon=m[4],color=m[5],number=i+1) for i,m in enumerate(MODULES)],
            'lessons':[{**l,'questions':[{k:v for k,v in q.items() if k not in ('answer','explanation')} for q in l['questions']]} for l in LESSONS]}
