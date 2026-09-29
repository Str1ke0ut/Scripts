# Error Log

This file tracks known bugs, setup problems, and unfinished pieces from earlier Kaivaz development.

## KaivazOS

### Python version mismatch
**Error:** `python3.12: command not found`

**Context:** The development environment had Python 3.14 available instead of Python 3.12.

**Status:** Open  
**Next step:** Use the Python version actually installed on the target Linux system, or install the required version before creating the virtual environment.

### Externally managed Python environment
**Error:** Python package installation was blocked by the system's externally managed environment.

**Context:** Installing packages directly with pip on Ubuntu triggered the system package-management restriction.

**Status:** Open / environment issue  
**Next step:** Use a project virtual environment and install dependencies inside it.

### pywebview dependency
**Error:** KaivazOS browser work ran into dependency/setup issues around `pywebview`.

**Status:** Open  
**Next step:** Decide whether the browser should use pywebview, a normal system browser, or a self-contained web view that does not add unnecessary dependencies.

### Missing filesystem module/function
**Error:** `filesystem.setup_filesystem` was referenced but was not available.

**Status:** Open  
**Next step:** Add the filesystem module and make initialization happen before the OS UI starts.

### Missing app framework
**Errors:** Missing `apps.base` and missing application classes such as File Manager, Terminal, Settings, and System Info.

**Status:** Open  
**Next step:** Create a consistent app base class/interface and move each built-in app into its own module.

## Rune

### Ollama connection
**Error:** Rune can report that Ollama is not running.

**Status:** Expected when Ollama is offline  
**Next step:** Add clearer startup detection and setup instructions, then test with a lightweight local model.

### Missing Python package
**Error:** `requests` was previously missing from the development environment.

**Status:** Environment issue  
**Next step:** Put runtime dependencies in `requirements.txt` and install them inside the project virtual environment.

## General project cleanup

- Add dependency files where needed.
- Add reproducible setup instructions.
- Separate experimental code from stable project code.
- Add basic smoke tests before calling a project release-ready.
- Record new errors here instead of leaving them buried in terminal output.

## Error Entry Format

Use this format for future entries:

```md
### Error title
**Error:** `exact error or symptom`

**Context:** What was happening when it appeared.

**Status:** Open / In Progress / Fixed / Won't Fix

**Next step:** The intended fix or investigation.
```
