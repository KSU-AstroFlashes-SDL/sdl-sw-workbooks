# SDL Software Workbooks
This repository contains working examples that are relevant to the efforts of the KSU AstroFlashes SDL Software subsection team.

> [!NOTE]
> By no means are these workbooks exclusive *to* the Software subsection team!
> **Anyone** with an interest in understanding the software concepts presented here is encouraged to try the workbooks!

Please follow the appropriate instructions below to prepare your working environment.  (If you're only interested in Python workbooks, then you only need to follow instructions to install Python, for example.)

## Python
Python must be installed to follow any of the *python-\** workbooks.

### Windows
**Option A (recommended if you plan to participate on the Software subsection team):**
Install the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) and its default Ubuntu distribution.

From within Ubuntu, clone the KSU-AstroFlashes-SDL/sdl-sw-bootstrap repository:
```bash
git clone https://github.com/KSU-AstroFlashes-SDL/sdl-sw-bootstrap.git
```

Now execute the *wsl-ubuntu-bootstrap* script:
```bash
./sdl-sw-bootstrap/wsl-ubuntu-bootstrap | tee wsl-ubuntu-bootstrap.log
```

**Option B (recommended if you just want to complete the workbook as a learning exercise):**
[Download Python](https://www.python.org/downloads/) and install it.  Be sure to **enable** the option to "Add Python to your PATH."

### macOS
**Option A (recommended if you plan to participate on the Software subsection team):**
Download & install [MacPorts](https://www.macports.org/).

From the command line (Terminal app), find the latest stable port (version) of python available:
```bash
port search --line --regex '^python3\d+$'
```
(This should list the available Python versions in version order. At the time of writing, the latest port is python313 (3.13.2).)

> [!NOTE]
> In each of the following three commands. make sure you **replace** "python3XX" with the *latest* version (e.g. "python313").

Install the **latest** Python port.  For example:
```bash
sudo port install python3XX python_select
```

Make the **latest** Python port the default `python3` command. For example:
```bash
sudo port select --set python3 python3XX
```

Make the **latest** Python port the default `python` command. For example:
```bash
sudo port select --set python python3XX
```

**Option B (recommended if you just want to complete the workbook as a learning exercise):**
[Download Python](https://www.python.org/downloads/) and install it.  Be sure to **enable** the option to "Add Python to your PATH."

> [!WARNING]
> "Homebrew" is a popular package manager for macOS.
> The SDL Software subsection does not recommend use of Homebrew (for reasons too lengthy to explain here).
> However, if you are *familiar with and already using* Homebrew, you may choose to use it to install Python.

### Linux
There are too many Linux distributions (and package managers) to account for here.

The assumption is made that if you are using Linux, then you understand how to use your distribution's package manager to find and install the latest stable version of Python 3.

(Members of the SDL Software subsection team can provide additional assistance.)

