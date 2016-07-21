# NOTICE!

This project is under heavy development, please, use [GoSublime](https://github.com/DisposaBoy/GoSublime) from DisposaBoy while this package is not ready.

# AnacondaGO

AnacondaGO adds autocompletion, inting and IDE features for Golang to your Sublime Text 3 using anaconda's asynchronous engine so it shouldn't freeze your Sublime Text ever.

## Supported Platforms

AnacondaGO has been developed and tested in OS X and for now, it doesn't work at all. The current status in the different platforms is:

   * **GNU/Linux:** WIP
   * **OS X:** WIP
   * **Windows:** WIP

## Dependencies

1. [Anaconda](https://github.com/DamnWidget/anaconda) plugin for Sublime Text 3
2. [Optional] CFFI (Foreign Function Interface for Python calling C code)
2. Go

## Dependencies Installation

AnacondaGO doesn't requires of CFFI library to be installed in your system (and be visible by your
configured Python interpreter) but if present it will speed up things considerably. Anaconda's python
code calls C methods exported from a custom wrapper over Golang's autocompletion tool [gocode](https://github.com/nsf/gocode).

AnacondaGO **is NOT** a fork of **gocode** we just maintain a wrapper that exports some functionallity
of gocode into a C ABI compatible dynamic library that is then used trough **cffi**.

**Note**: AnacondaGO doesn't use the embedded ST3 python interpreter, for more information about
anaconda and the `python_interpreter` take a look at the [anaconda's official documentation](http://damnwidget.github.io/anaconda/anaconda_settings/)

### Installing CFFI

There are many ways of install `cffi`, you can just download an installer for Windows or OS X from the [pypi](https://pypi.python.org/pypi/cffi) (Python Package Index) or use the recommended way:
```bash
pip install cffi
```

**Note**: The **CFFI** package **should** be installed into you system and not as a ST3 dependency

**Note**: If **CFFI** is not available, anconda will use the standard library `ctypes` module instead.

## Plugin Installation

If [Anaconda](https://github.com/DamnWidget/anaconda) is not already installed you should install it using the `Command Palette`, if it is already installed, just skip to the next section

### Install Anaconda plugin

1. Show the Command Palette (`cmd+shift+p` on OS X or `ctrl+shift+p` on Linux/Windows)
2. Type `install`, then select `Package Control: Install package` from the list of options
3. Type `anaconda` and press enter

### Install AnacondaGO plugin

1. Show the Command Palette (`cmd+shift+p` on OS X or `ctrl+shift+p` on Linux/Windows)
2. Type `install`, then select `Package Control: Install package` from the list of options
3. Type `anaconda_go` and press enter
