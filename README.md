WMemPy - WinApi Memory Application
==================================
WMempy allows users to quickly manipulate with memory of other processes using WinApi. The application provides CLI as well as Python modules to work with most processes.

Features
--------
List processes and get process handle
Retrieve modules and memory pages (called Scannables)
Read and analyze Scannables
Run AOB and ASCII scans on Scannables
List ASCII strings of Scannables
Read and Write Process Memory (both Scannables and Process is supported)
View memory blocks in CLI

Examples
--------
### bad_code_detection
Shows how to look for good/bad code in running processes

### config_dump
Example configuration file for CSGO offset dump (using the CLI wmempy --dump)

### cpp_apps
Very simple applications written in C++ to experiment on with the app. Source code included where possible. To compile the C++ code, you need at least C++14 and Windows compiler (MSVC or MinGW GCC)

### csgo_primitive_wallhack
Shows how to use the tool to read and alter memory of other processes to gain an advantage

### password_grabber
Shows how to use the tool to look for strings that are hardcoded into the app as well as live memory strings

Install
-------
To install the project, download the package:

<pre>
python -m pip install wmempy
</pre>

Documentation
-------------

To check out the sources and documentation, download the source from:

<pre>
https://github.com/fitancinpet/WMemPy
https://pypi.org/project/wmempy/#files
</pre>

Extract the sources if needed and go into the WMemPy folder (main project folder). From there, to build documentations, just do:

<pre>
cd docs
.\make.bat html
</pre>

The HTML pages are in _build/html.

Tests
-----

To run tests, make sure you are on Windows as the application only supports that and in the project directory run:

<pre>
python setup.py test
</pre>

There are two types of tests, non-live and live. The live tests work with live Windows memory and have _live at the end.

CLI Usage
---------
<pre>
wmempy --help

# List running processes
wmempy -l

# Show all modules loaded into dwm.exe
wmempy -n dwm.exe --modules

# Show all valid pages of dwm.exe
wmempy -n dwm.exe --pages

# Scan dwm.exe for a memory pattern
wmempy -n dwm.exe --aob 'b0,aa,4a,2f,3d,00,00,00,d0,ac,4a,2f'

# Scan dwm.exe for a memory pattern with wildcards
wmempy -n dwm.exe --aob 'b0,aa,4a,2f,3d,?,?,?,d0,ac,4a,2f'
wmempy -n dwm.exe --aob 'b0,aa,4a,2f,3d,*,*,*,d0,ac,4a,2f'

# Scan dwm.exe for a memory pattern different options
wmempy -n dwm.exe --aob 'b0 aa 4a 2f 3d * * * d0 ac 4a 2f' --separator ' '
wmempy -n dwm.exe --aob '176:170:74:47:61:?:?:?:208:172:74:47' --separator ':' --base 10

# Scan kernel32 module loaded into dwm.exe for a memory pattern
wmempy -n dwm.exe --aob '82 9b ? ? ? c6 03' --separator ' ' --where kernel32.dll

# Scan all modules loaded into dwm.exe for a memory pattern
wmempy -n dwm.exe --aob '82 9b ? ? ? c6 03' --separator ' ' --where modules

# Scan all pages (live memory) of dwm.exe for a memory pattern
wmempy -n dwm.exe --aob 'b0 aa 4a 2f 3d * * * d0 ac 4a 2f' --separator ' ' --where pages

# Find address of 'Microsoft' in memory of dwm.exe
wmempy -n dwm.exe --text Microsoft

# Find address of 'padding' according to Microsoft in modules of dwm.exe
wmempy -n dwm.exe --text PADDINGXXPADDING --where modules

# Find address of 'LoadLibrary' string in kernel32 module loaded into dwm.exe
wmempy -n dwm.exe --text LoadLibrary --where kernel32.dll

# List all strings in dwm.exe
wmempy -n dwm.exe --list-text 'all'

# List all strings in dwm.exe that do not contain symbols and are at least 20 chars long
wmempy -n dwm.exe --list-text 'c20'

# List all strings in dwm.exe that can contain symbols and are at least 40 chars long
wmempy -n dwm.exe --list-text 's40'

# List all strings in modules of dwm.exe
wmempy -n dwm.exe --list-text 'all' --where modules

# List all strings in kernel32 module loaded into dwm.exe
wmempy -n dwm.exe --list-text 'all' --where kernel32.dll

# List strings with symbols longer than 3 chars in dwm.exe that contain the word 'auth'
wmempy -n dwm.exe --list-text 's3' --hint auth

# List strings with symbols longer than 3 chars in kernel32.dll module of dwm.exe that contain the word 'security'
wmempy -n dwm.exe --list-text 's3' --hint security --where kernel32.dll

# Dump the entire memory of dwm.exe into console
wmempy -n dwm.exe --view 'all'

# Dump the memory of dwm.exe's modules into console
wmempy -n dwm.exe --view 'modules'

# Dump the memory of dwm.exe's kernel32.dll module into console
wmempy -n dwm.exe --view 'kernel32.dll'

# Dump the memory of dwm.exe's kernel32.dll module into console starting at address 0xa3045 of the module
wmempy -n dwm.exe --view 'kernel32.dll' --hint 0xa3045

# Check how similar are dwm.exe and explorer.exe (when it comes to long strings)
wmempy --compare dwm.exe explorer.exe

# Dump CSGO offsets from config file
wmempy -n csgo.exe --dump 'examples/config_dump/cs.cfg'
</pre>
