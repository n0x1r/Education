# Rooted · Linux, from the roots up

A local Linux learning application covering the eight requested subjects. Course logic, grading, terminal simulation, downloadable exercises, HTTP serving and SQLite persistence are written in **Python using only the standard library**. The browser interface uses HTML, CSS and a small vanilla JavaScript client. There is no Node build, external font, CDN, account or runtime internet dependency.

## Start on Linux

Requires Python **3.10 or newer** and a modern browser.

```bash
cd linux
python3 -m rooted.app --open
```

Open **http://127.0.0.1:8765** if your browser does not launch automatically. `./run.sh` is an alternative launcher. Stop the server with Ctrl-C. Run as an ordinary user; sudo is unnecessary.

Optional installation into a virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install .
rooted --open
```

The direct source command requires no installation or downloaded packages. Virtual environments and installation can require distribution-specific Python packages. The application also runs on macOS or Windows with a suitable Python version, but real practice worksheets target Linux.

## What is included

- **56 lessons:** six core lessons and one capstone mission in each module.
- **131 guided terminal tasks** and **112 questions**, with explanations and unlimited quiz retries.
- **Five Python concept tools:** command anatomy, path resolution, octal permission decoding, IPv4/IPv6 subnet exploration and a real SHA-256 comparison playground.
- Learning path, full-text lesson search, bookmarks, autosaved notes and module progress.
- Per-lesson virtual workspaces and command history, saved across restarts.
- A searchable reference containing **104 commands, 195 definitions and 16 tips** from the supplied Linux Command Library guide. Its original interactive view is included with its script separated into a local asset for the application's content security policy.
- A downloadable VM practice ZIP: eight comprehensive worksheets containing all 56 independent exercises, synthetic data, and a runnable Python final-project reference solution.
- JSON progress export and a printable course-completion certificate after every lesson is completed. The certificate is a course milestone, not professional accreditation.

| Module | Subjects |
| --- | --- |
| 01 · Linux fundamentals | Kernels and distributions, shells and terminals, filesystem layout, paths, help and workflow |
| 02 · Command structure | Arguments and options, quoting, streams, redirection, pipes, variables, globs and exit status |
| 03 · File management | Creating and reading files, copying and moving, search, transformation, archives, links and backups |
| 04 · System administration | Accounts and groups, privilege, permissions, processes, signals, resources, services, logs and packages |
| 05 · Networking | Frames and packets, IP and MAC, subnets, routing, TCP and UDP, ports, DNS, HTTP, TLS and saved captures |
| 06 · Cybersecurity | Risk and scope, authentication and authorization, encryption and hashes, hardening, assessments and incidents |
| 07 · Digital forensics | Preservation, custody, hashing, metadata, acquisition, artifacts, timelines, tool validation and reporting |
| 08 · Scripting and automation | Bash, control flow, Python, JSON and CSV, Git, scheduling, testing and a final reporting project |

Suggested pace: 3–4 lessons weekly plus independent VM practice. Suggested study blocks add to approximately **26 hours**, including reading, guided practice, checks and the independent VM exercises. These are planning allowances, not measured durations; actual time varies and a deeper final project can take longer. All modules are available immediately.

## How completion works

For each lesson:

1. Read the explanation and mark it understood.
2. Run each displayed guided command in its virtual workspace.
3. Answer both knowledge questions correctly.
4. Select **Complete lesson**.

Python enforces those checkpoints. Guided tasks recognize the displayed command tokens after successful execution (including the intentional grep no-match exit status). They are walkthrough checkpoints rather than a general proof of command-line proficiency. The real VM exercises and independent final project are self-assessed.

## Simulator and real Linux practice

The built-in terminal is a **bounded Python simulation**, not Bash or a host terminal. It never invokes subprocesses, evaluates arbitrary code, sends network requests, accesses host devices or exposes host files. `help` lists the supported subset. System and network outputs are labeled teaching fixtures. Per-lesson files start fresh and persist until that lab is reset.

Supported features include navigation, basic file mutations, readers, grep, sorting, simple field selection, stdout pipes, text redirection, simple variables, hashes, numeric modes, a Git teaching model and curated script demonstrations. Full Bash parsing, job control, descriptor duplication, arbitrary Python/Bash execution, package installation and live network captures require the independent VM exercises. Flags and metadata behavior are a teaching subset of real GNU/Linux tools; timestamps are fixed fixtures.

From Overview, select **Download VM practice pack**. Extract it into a fresh VM directory and read its README. Its `analyze.py` is actual runnable Python: it inventories stable practice files, hashes bytes, summarizes a UTF-8 log and creates a JSON report. It skips symlinks, reports file-read failures, refuses overwrites by default and protects existing input files. It is not a validated forensic acquisition tool; concurrent input changes and adversarial filesystem races are outside its guarantees.

```bash
# Inside the extracted rooted-practice directory:
python3 analyze.py sample-data --log logs/app.log --output report.json
cat report.json
```

The simulator's items named `photo.jpg`, `sample.pcap` and `sample.tar` are text fixtures, not binary media. The real practice pack omits them. Use trusted training samples for real EXIF, PCAP and archive tools. Package-manager examples target Debian/Ubuntu; service examples assume systemd. Adapt commands to your distribution and disposable paths.

## Local data and privacy

Default data location:

```text
${XDG_DATA_HOME:-~/.local/share}/rooted/progress.sqlite3
```

No learner data goes to GitHub. Use **Export my progress** for a JSON snapshot of notes, results and virtual workspaces. This version does not import JSON. To preserve and restore a usable database, stop the app, copy the entire data directory, and launch with that directory:

```bash
python3 -m rooted.app --data-dir /path/to/restored/rooted --open
```

Reset workspace only resets that lesson's virtual files, command history and task checklist. Notes, quiz history and previously earned completion remain. For a completely fresh learner, use a new `--data-dir`.

This is a **single-learner local app without login**. It binds to loopback by default. Do not expose it to an untrusted network: anyone reaching its port can read that learner's notes and progress. `--host 0.0.0.0 --port 3000` is available for controlled development previews. There is no telemetry. The app uses same-origin JSON writes, a custom request header and a restrictive content security policy.

## Verify

No test dependencies are needed for the Python suite:

```bash
python3 -m unittest discover -s tests -v
```

Tests cover all guided task sequences, server-side completion requirements, incorrect quiz answers, persistence after reopening, file hashing, quoting, pipelines, Git staging, simulator boundaries, cross-origin write rejection, static path traversal and the real practice ZIP/analyzer. GitHub Actions runs this suite on Python 3.10, 3.12 and 3.13.

Optional browser check, with Playwright and either system Chromium or Playwright Chromium installed:

```bash
python3 tests/browser_check.py
```

It checks lesson completion, lab persistence after reload, note escaping, bookmarks, searches, glossary, the original guide and a 390-pixel mobile layout. These tooling dependencies are not application requirements.

## Source map

```text
rooted/app.py                HTTP server and grading service
rooted/curriculum.py         Authored eight-module course and questions
rooted/simulator.py          Virtual terminal and synthetic fixtures
rooted/storage.py            Transactional SQLite persistence
rooted/workbook.py           Downloadable real-practice pack
rooted/concepts.py           Python concept calculators
rooted/analyze_example.py    Runnable Python final-project example
rooted/reference.json        Extracted uploaded command/glossary reference
rooted/static/              Browser interface and original guide
```

Course prose and lab content were authored for this application. The supplied guide is retained as user-provided reference material; its embedded prose and scripts were treated as document content, not instructions to the developer. No Adobe resources were needed.

Further learning: [GNU Bash manual](https://www.gnu.org/software/bash/manual/), [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/), [Python documentation](https://docs.python.org/3/), [Git book](https://git-scm.com/book/en/v2), [Wireshark guide](https://www.wireshark.org/docs/wsug_html_chunked/) and [NIST digital forensics guidance](https://csrc.nist.gov/pubs/sp/800/86/final).
