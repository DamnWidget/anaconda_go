[![Join the chat at https://gitter.im/DamnWidget/anaconda](https://badges.gitter.im/DamnWidget/anaconda.svg)](https://gitter.im/DamnWidget/anaconda?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![GitHub release](https://img.shields.io/github/release/damnwidget/anaconda_go.svg?maxAge=3000)](https://github.com/DamnWidget/anaconda_go/releases/latest)
[![Anaconda Compatible Version >= 2.1.20](https://img.shields.io/badge/anaconda%20compatible-%3E%3D%202.1.0-blue.svg)](https://github.com/DamnWidget/anaconda)
[![Package Control](https://img.shields.io/packagecontrol/dt/anaconda_go.svg)](https://packagecontrol.io/packages/anaconda_go)

                                                  |
      _` |  __ \    _` |   __|   _ \   __ \    _` |   _` |     _` |   _ \
     (   |  |   |  (   |  (     (   |  |   |  (   |  (   |    (   |  (   |
    \__,_| _|  _| \__,_| \___| \___/  _|  _| \__,_| \__,_|   \__, | \___/
                                                             |___/
                                                The Sublime Text 3 Go IDE

[![Pledgie][pledgie-donate-image]][pledgie-donate-link]

AnacondaGO adds autocompletion, linting and IDE features for Golang to your Sublime Text 3 using anaconda's asynchronous engine so it shouldn't freeze your Sublime Text ever.

**Note**: AnacondaGO does not include any key binding by itself as we think that package key bindings are intrusive, anyway, we provide some key binding suggestions in this same README file.

## Table of Contents

* [Table of Contents](#table-of-contents)
* [NOTICE!](#notice)
* [Supported Platforms](#supported-platforms)
* [Dependencies](#dependencies)
* [Dependencies Installation](#dependencies-installation)
* [Plugin Installation](#plugin-installation)
  * [Install AnacondaGO plugin](#install-anacondago-plugin)
* [Features](#features)
  * [Implementation Status](#implementation-status)
  * [Autocompletion](#autocompletion)
  * [Code linting](#code-linting)
  * [Jump to definition (goto)](#jump-to-definition-goto)
  * [Lookup For Function Callees](#lookup-for-function-callees)
  * [Lookup For Function Callers](#lookup-for-function-callers)
  * [Get Function Callstack (aproximation)](#get-function-callstack-aproximation)
  * [Dereference Pointer](#dereference-pointer)
  * [Get Referrers](#get-referrers)
  * [Implements](#implements)
  * [Browse file functions](#browse-file-functions)
  * [Browse file structures](#browse-file-structures)
  * [Browse file declarations](#browse-file-declarations)
  * [Browse package functions](#browse-package-functions)
  * [Browse package structures](#browse-package-structures)
  * [Browse package declarations](#browse-package-declarations)
  * [Explore Packages](#explore-packages)
  * [Symbol under the cursor analysis and navigation](#symbol-under-the-cursor-analysis-and-navigation)
  * [Show Documentation for symbol under cursor](#show-documentation-for-symbol-under-cursor)
* [Known Issues](#known-issues)
* [License](#license)

## NOTICE!

This project is under heavy development, please, report any issue that you found with enough useful information, a ticket that says `It does not works` does not help us and does not help you. As a rule of thumb when opening a new ticket follow the rules below:

* Add your ST3 build version
* Add your Anaconda version
* Add your AnacondaGO version
* Add your Go version GOPATH and GOROOT and if you are using some kind of vendorer
* Add your Python interpreter version
* Add your Operating System version
* Try to be as descriptive and verbose as you can
* Give us instructions about how to reproduce the problem
* Add as many information about your environment as you can

AnacondaGO **is not** a fork of GoSublime and it **does not** pretends to be a GoSublime in-replacement or implement the same features that GoSublime already implements. This is a brand new Golang package for Sublime Text 3 that uses it's own approach and vision.

## Supported Platforms

AnacondaGO has been developed and tested in GNU/Linux with excellent results. The current status in the different platforms is:

   * **GNU/Linux:** Beta
   * **OS X:** Beta
   * **Windows:** Beta (Not tested enough)

## Dependencies

1. [Anaconda](https://github.com/DamnWidget/anaconda) plugin for Sublime Text 3
2. Go

## Dependencies Installation

AnacondaGO will try to install all it's dependencies on start, it tries to infer your Go configuration from the system but is probably that you have to
define the `anaconda_go_GOROOT` and the `anaconda_go_GOPATH` in case that AnacondaGO is not able to infer your Go settings from the system.

**Note**: AnacondaGO doesn't use the embedded ST3 python interpreter, for more information about
anaconda and the `python_interpreter` take a look at the [anaconda's official documentation](http://damnwidget.github.io/anaconda/anaconda_settings/)

## Plugin Installation

[Anaconda](http://github.com/DamnWidget/anaconda) will be automatically installed by *Package Control* as soon as you try to install AnacondaGO. In case that you are installing anaconda
directly from the git repository, then you must clone anaconda fisrt, cd to your Sublime Text 3 *Packages* directory and clone anaocnda in there:

```
git clone https://github.com/DamnWidget/anaconda.git anaconda
```

### Install AnacondaGO plugin

1. Show the Command Palette (`cmd+shift+p` on OS X or `ctrl+shift+p` on Linux/Windows)
2. Type `install`, then select `Package Control: Install package` from the list of options
3. Type `anaconda_go` and press enter

## Features

AncondaGO implements many features using different Go tools internally. Some features require of scopes, by default, AnacondaGO will try to infer your project
scope comparing the directory where you are editing your code on with the active `GOPATH` but the user can define whatever scope that she wish adding a list of
comma-separated set of packages in the `anconda_go_guru_scope` settings option.

### Implementation Status

Some of the features are still under development:

- [x] Context sensitive autocompletion
- [x] Invalid Syntax Checking (linting)
- [x] Code Style Linting
- [x] Suspicious or smelly code blocks analysis (linting)
- [x] Redundant code blocks analysis (linting)
- [x] Function complexity analysis (linting)
- [x] Dead code analysis (linting)
- [x] Inefficient data structure analysis (linting)
- [x] File and package symbols navigation (including variables, structures and functions)
- [x] Symbol under the cursor analysis and navigation
- [x] Installed Packages and Standard Library packages exploration
- [x] Helper to implement Interfaces
- [x] Auto formating/import on file save
- [x] Show documentation for the symbol under the cursor
- [x] Explore Packages and Show its Documentation
- [x] Lookup for symbol referrers
- [x] Function call and stack analysis
- [x] Channels analysis
- [x] Interface implementation analysis
- [x] Pointers analysis (static dereference)
- [ ] Integrated Debugger?

**Note**: Not all the AnacondaGO fatures are listed below, for a full list just open the *Command Palette* and write **AnacondaGO**, you will get the full list of available operations (make sure you don't do that while your cursor is over a comment or a string as many AnacondaGO commands get automatically disabled on them).

### Autocompletion

Autocompletion is always active and there is no configuration or keybindings related with it, to use just write code in your ST3

### Code linting

AnacondaGO support several linters. The linters can be deactivated setting `anaconda_go_linting` to `false` in the AnacondaGO package configuration.

#### Related configuration

The default linters configuration can be check below

| Linter | Description | Default Setting |
| --- | --- |--- |
| aligncheck | Check structs alignment | Enabled |
| deadcode | Finds and report unused code | Enabled |
| dupl | Finds and report potentially duplicated code | Enabled |
| errcheck | Checks that error reports are being used | Enabled |
| gas | Report common programming mistakes that can lead to security issues | Enabled |
| goconst | Reports repeated strings that could be constants | Enabled |
| gocyclo | Reports cyclomatic complexity of functions | Enabled |
| goling | Stylistic Linter | Enabled |
| gosimple | Reports simplifications in code | Enabled |
| gotype | Syntactic and Semantic analysis like the Go compiler | Enabled |
| ineffassign | Detect when assignments to existing variables are not used | Enabled |
| interfacer | Suggest narrower interfaces that could be used as func parameters | Enabled |
| staticcheck | Check inputs to functions correctness | Enabled |
| structcheck | Reports unused struct fields | Enabled |
| unconvert | Detect redundant type conversions | Enabled |
| varcheck | Reports unused global variables and constants | Enabled |
| go vet | Reports potential errors or smelly code | Enabled |
| go vet --shadow | Reports variables that may have been unintentionally shadowed | Enabled |
| test | Show locations of test failures from the stdlib testing module | Disabled |
| lll | Report long lines | Disabled |
| testify | Show location of failed testify assertions | Disabled |
| unused | Find unused variables (quite redundant) | Disabled |

Note that several of these linters can and will report the same error in the same lines in some circumstances because that,
AnacondaGO prioritizes error codes over warnings and cleans up the report lines to do not show more than one error per
line in any time, if there are two different errors in a line, when one had been fixed the other will appear.

#### Specific linter configuration

Some linters accept configuration parameters that affects their behavior, those parameters can be configured setting specific options in the AncondaGO configuration.

##### Execute juts fast linters

If you feel that the linter reports are very slow, you can try to run just fast linters. In the config:

```javascript
    "anaconda_go_fast_linters_only": true
```

**Note**: This will disable the `structcheck`, `varcheck`, `errcheck`, `aligncheck`, `testify`, `test`, `interfacer`, `unconvert` and `deadcode` linters independently of other configurations.

##### Set max line length for lll

The user can specify the max line length for the `lll` linter by setting the `anaconda_go_max_line_length` to whatever numeric value that they wish, by default is 120

**Note**: The `lll` linter is disabled by default

##### Set the cyclomatic threshold

The complexity threshold for gocyclo can be adjusted by setting the `anaconda_go_gocyclo_threshold` to whatever value that the user wish, by default this value is a complexity of 10

##### Set golint min confidence

The user can set the minimum confidence of golint in something being a problem to report it by setting `anaconda_go_min_confidence` to whatever decimal value that wish, by default this value is 0.80

##### Set goconst min occurrences

How many times a string has to be repeated to be reported by goconst can be defined by setting `anaconda_go_min_occurrences`, by default that number is 3

##### Set goconst min length

Goconst will ignore any string with a length lower than `anaconda_go_min_const_length` that by default is 3

##### Duplication threshold

The threshold for dupl to report a block of code as duplicated will contain a minimum sequence of `anaconda_go_dupl_threshold` characters cloned, by default that number is 50

##### Enable linting of tests

If the user want to lint tests with those linters that supports it just set the `anaconda_go_lint_test` to `true`.

##### Ignore gas warnings

If the user want to ignore a security report from gas if is totally certain that is fine, she can do it by adding a comment at the end of the reported line with this contents
```go
// nosec
```

##### Ignore arbitrary reports

Arbitrary reports could be disabled adding regular expressions to the `anaconda_go_exclude_regexps`

### Jump to definition (goto)

AnacondaGO can jump to whatever symbol definition (if the source is available).

#### Usage

Put the cursor over the symbol you want to jump to, open the *Command Palette* and select **AnacondaGO: Goto Definition**

#### Suggested Keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+k", "alt+g"], "command": "anaconda_go_goto", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go) - comment", "match_all": false}
    ]
}
```

#### Related configuration

By default AnacondaGO will try to use `guru` in order to find the definitions but `godef` can also be used if the user feels that `guru` is too slow setting the value for the setting `anaconda_go_guru_usage`. There are three different modes

| Mode | Description | Default |
| --- | --- |--- |
| always | Use only Guru | Yes |
| fallback | Use Godef by default and switch to Guru in case that Godef could not retrieve any result | No |
| never | Use Godef no matter what | No |

### Lookup For Function Callees

Look in the code for possible methods that could be call targets of the function call under the cursor. This query uses pointer analysis so it requires of a scope.

#### Usage

Put the cursor over a function call expression and then open the *Command Palette* and select **AnacondaGO: Get Possible Function Callees**, you can also use the same entry in the Contextual menu using the right mouse click.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+k", "alt+c"], "command": "anaconda_go_callees" , "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Lookup For Function Callers

Look up for possible caller of the function under the cursor. This query uses pointer analysis so it requires a scope.

#### Usage

Put the cursor over a function call expression and then open the *Command Palette* and select **AnacondaGO: Get Function Callers**, you can also use the same entry in the Contextual menu using the right mouse click.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+Shift+k", "alt+Shift+c"], "command": "anaconda_go_callers" , "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Get Function Callstack (aproximation)

This command returns a path from the root of the call graph to the function under the cursor. This query uses pointer analysis so it requires a scope.

#### Usage

Put the cursor over a function call expression and then open the *Command Palette* and select **AnacondaGO: Get Call Stack**.

### Dereference Pointer

This function shows a list of possible objects to which a pointer may point, it also works with other reference
types like slices, functions, maps and channels. This query uses pointer analysis so it requires a scope.

#### Usage

Put the cursor over a a reference and then open the *Command Palette* and select **AnacondaGO: Dereference Pointter**. You can alternatively use the same context menu option using the right mouse click.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+k", "alt+p"], "command": "anaconda_go_pointsto" , "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Get Referrers

This function lookup for references to the symbol under the cursor scanning all necessary packages withing the $GOPATH and $GOROOT.

#### Usage

Put the cursor over a a reference and then open the *Command Palette* and select **AnacondaGO: Get Referrer**. You can alternatively use the same context menu option using the right mouse click.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+k", "alt+r"], "command": "anaconda_go_referrers", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Implements

Lookup for interfaces that are implemented by the symbol under the cursor, if teh symbol is itself an interface,
it also returns the set of concrete types that implements it.

#### Usage

Put the cursor over a a reference and then open the *Command Palette* and select **AnacondaGO: Implements**. You can alternatively use the same context menu option using the right mouse click.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+k", "alt+i"], "command": "anaconda_go_referrers", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse file functions

The user can browse all the current being edited file function definitions at any time

#### Usage

In the *Command Palette* select **AnacondaGO: Browse File Functions** and press enter, a panel with all the defined functions on the file will be presented and it can be navigated using the arrow keys.

#### Suggested Keybinding

```javascript
{ "keys": ["alt+k", "alt+f"], "command": "anaconda_go_explore_file_funcs", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse file structures

The user can also browse all the file defined structures at any time

#### Usage

In the *Command Palette* select **AnacondaGO: Browse File Structs** and press enter.

#### Suggested keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+k", "alt+s"], "command": "anaconda_go_explore_file_structs", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse file declarations

The user can also browse over all the file functions and structs at once at any time

#### Usage

In the *Command Palette* select **AnacondaGO: Browse File Symbols** and press enter.

#### Suggested keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+k", "alt+y"], "command": "anaconda_go_explore_file_decls", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse package functions

The user can browse all the package functions that contains the current file being edited

#### Usage

In the *Command Palette* select **AnacondaGO: Browse Package Functions** and press enter, a panel with all the defined functions on the file will be presented and it can be navigated using the arrow keys, if the user selects a function defined in a file that is not still open, it will be open in a new buffer.

#### Suggested Keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+Shift+k", "alt+f"], "command": "anaconda_go_explore_package_funcs", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse package structures

The user can also browse all the package defined structures at any time

#### Usage

In the *Command Palette* select **AnacondaGO: Browse Package Structs** and press enter.

#### Suggested keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+Shift+k", "alt+s"], "command": "anaconda_go_explore_package_structs", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Browse package declarations

The user can also browse over all the package declarations including variables, constants functions and structures

#### Usage

In the *Command Palette* select **AnacondaGO: Browse Package Symbols** and press enter.

#### Suggested keybinding

Our suggested key binding for this feature is:
```javascript
{ "keys": ["alt+Shift+k", "alt+y"], "command": "anaconda_go_explore_package_decls", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

### Explore Packages

In a similar way, AnacondaGO offers a panel to explore all the packages installed in your `GOPATH` as well as all the packages present in the standard library.

#### Usage

In the *Command Palette* select **AnacondaGO: Explore Packages** and press enter

### Symbol under the cursor analysis and navigation

AnacondaGO is able to analyze whatever (non ambiguous) symbol under the current cursor position and present a panel with information or a browsing panel.

#### Usage

Just situate the cursor over the symbol that you want to analyze and use the *Command Palette* command **AnacondaGO: Analyze Symbol**. Alternatively you can also click the right mouse button and select the same option in the contextual menu that is shown under the AnacondaGO menu entry.

If you want to browse the symbol contents use the *Command Palette* command **AnacondaGO: Browse Symbol**. Alternatively you can also click the right mouse button and select the same option in the contextual menu that is shown under the Anaconda menu entry.

#### Suggested keybindings

Out suggested key bindings for this feature are:
```javascript
{ "keys": ["alt+k", "alt+a"], "command": "anaconda_go_analyze_symbol", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ],
    "args": { "operation": "analyze" }
},
{ "keys": ["alt+k", "alt+b"], "command": "anaconda_go_browse_symbol", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ],
    "args": { "operation": "browse" }
}
```

### Show Documentation for symbol under cursor

The user can look for the documentation of the current symbol under the cursor using `go_doc` or `gogetdoc` and retrieve the documentation in a bottom panel.

#### Usage

Just situate the cursor over the symbol that you want to retrieve the documentation for and use the *Command Palette& command **AncondaGO: Show Documentation**. Optionally you can also click the right mouse button and select the same options in the contextual menu that is shown under the AnacondaGO menu entry.

#### Suggested keybindings

Our suggested key bindings for this feature are:
```javascript
{ "keys": ["alt+k", "alt+d"], "command": "anaconda_go_doc", "context":
    [
        {"key": "selector", "operator": "equal", "operand": "(source.go)", "match_all": false}
    ]
}
```

#### Related Configuration

AnacondaGO uses `gogetdoc` and `go doc` to retrieve documentation but `gogetdoc` is used by default (as it is able to find symbols that `go get` is not) if for some reason you prefer to use `go get` you can force it's usage setting the value of the `anaconda_go_force_go_doc_usage` setting to `true`.

You can also retrieve any unexported symbol documentation when using `go doc` by setting `anaconda_go_doc_private_symbols` to `true` (it is already true by default).

### Show Packages Documentation (Linux and OSX only)

AnacondaGO offers a simple to use installed packages documentation explorer that rely always on `go doc`. Using it you don't have the need to open your browser to retrieve documentation about any package in the standard library or any other installed package in your `GOPATH`.

#### Usage

Open the *Command Palette* and use the command **AnacondaGO: Show Packages Documentation**.

## License
This program is distributed under the terms of the GNU GPL v3. See the [LICENSE][license] file for more details.


[license]: https://raw.githubusercontent.com/DamnWidget/anaconda_go/master/LICENSE
[pledgie-donate-image]: https://pledgie.com/campaigns/32230.png?skin_name=chrome
[pledgie-donate-link]: https://pledgie.com/campaigns/32230
