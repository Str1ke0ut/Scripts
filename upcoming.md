# Upcoming

Roadmap for the next Kaivaz development passes.

## 1. KaivazOS

- Finish the modular project structure.
- Implement the filesystem layer and startup initialization.
- Build the shared app framework.
- Add File Manager, Terminal, Settings, and System Info as separate apps.
- Finish the `games.py` app/module.
- Add application icons.
- Add the shutdown flow and button.
- Finish the browser experience without making the OS depend on a fragile setup.
- Test the full boot sequence from `boot.py`.
- Add `requirements.txt` and setup instructions.
- Add a clean README with screenshots once the UI is stable.

## 2. Rune

- Refine the local AI chat interface.
- Improve memory handling.
- Improve voice output behavior.
- Add a cleaner startup/status check for Ollama.
- Expand the built-in coding helpers.
- Separate the app into maintainable modules instead of keeping everything in one script.

## 3. Game Projects

### Elemental Legends
- Continue the playable prototype.
- Separate game systems into modules.
- Add clearer player/avatar state handling.
- Add project documentation and dependencies.

### Kaivaz Racing
- Rebuild/organize the lane-based racing prototype.
- Separate gameplay, rendering, input, and track logic.
- Add a README and dependency list.
- Add a simple release build once the prototype is stable.

## 4. Creative Tools

### FrameBoard
- Keep the current tool organized as a standalone animation utility.
- Add dependency/setup documentation.
- Add example project files when available.

### ArtWatch
- Finish the desktop art-monitoring workflow.
- Document the drawing-app integration requirements.
- Add setup and troubleshooting notes.

### Creator Studio
- Continue the older creator-app code as a legacy project.
- Keep the historical STR!KE_0UT name in the source history where appropriate, while using Kaivaz for current creator branding.
- Refactor large UI sections into modules when the project is actively developed again.

## 5. GitHub Organization

- Keep one project per directory when projects are related.
- Use clear project names instead of `Pasted text` or `Pasted code`.
- Add a README to every substantial project.
- Add `LICENSE` only when the intended licensing is decided.
- Keep experimental prototypes clearly labeled.
- Use commits that describe what changed instead of generic messages.

## Priority

**Now:** KaivazOS structure and missing modules  
**Next:** Rune cleanup and Kaivaz Racing organization  
**Then:** Elemental Legends, ArtWatch, and additional archived projects  
**Later:** Larger production-ready releases
