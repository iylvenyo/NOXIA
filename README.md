
you will need python3, git, and GTK4

clone it:

```bash
git clone https://github.com/iylvenyo/NOXIA.git
cd NOXIA
```

Install python if you don't have it then install the requirements

windows / powershell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py main.py
```

mac or linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

if `python3` does not work, try `python` instead.

if `py` does not work on windows, install python from https://www.python.org/downloads/ and make sure “Add Python to PATH” is checked.

to upload changes:

```bash
git add .
git commit -m "what you changed"
git push
```
