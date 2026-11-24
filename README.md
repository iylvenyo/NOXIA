
you will need python, git, gtk4, and MSYS2 (If on windows)

> [!NOTE]
> pip can't install PyGoObject on powershell on windows without having an aneurysm. I'd recommend installing
and using MSYS2 UCRT64 or maybe use WSL...

windows / MSYS2:

install MSYS2 from https://www.msys2.org/

open **MSYS2 UCRT64** (not PowerShell) and run:

```bash
pacman -Syu
```

if it tells you to close the terminal, close it, reopen **MSYS2 UCRT64**, and run the update command again:

```bash
pacman -Syu
```

then install the stuff NOXIA needs:

```bash
pacman -S --needed \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-gtk4 \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-cairo \
  mingw-w64-ucrt-x86_64-python-numpy \
  mingw-w64-ucrt-x86_64-python-pyopengl \
  mingw-w64-ucrt-x86_64-gst-plugins-base \
  mingw-w64-ucrt-x86_64-gst-plugins-good \
  mingw-w64-ucrt-x86_64-pyinstaller
```
clone and cd into the project, then run it

```bash
git clone https://github.com/iylvenyo/NOXIA.git
cd NOXIA
python main.py
```

mac / linux:

>[!NOTE]
> if pip install for the dependencies fail it's because you need to install some extra dependencies needed for pycairo or PyGObject to work.
> Inspect the error message to install what's needed from your package manager. 
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

if `python3` does not work, try `python` instead.

to upload changes:

```bash
git add .
git commit -m "what you changed"
git push
```
