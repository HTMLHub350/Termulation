# Termulation

**Termulation** is a lightweight, Python-based terminal emulator built using Tkinter.  
It simulates a mini operating system environment, complete with users, a filesystem, package management, and basic system utilities.  

It’s designed for learning, experimentation, and fun, giving you a sandbox to explore terminal commands, file management, and user administration — all in a safe Python environment.  

---

## Key Features

### Multi-User System
- Supports multiple users with username/password login.
- Admin user (`admin`) has full system privileges.
- Non-admin users have restricted permissions.

### Filesystem & Trash
- Create, remove, and navigate directories.
- Move files to Trash, restore them, or empty Trash.

### Package Management (TPM)
- Install, remove, and list packages.
- Only admin can install/remove packages.

### Processes & Networking
- Simulate running processes and killing them.
- Simulate pinging and connecting to hosts.

### User Administration
- Admin can create, delete, and manage users.
- Change usernames and passwords (with restrictions).

### Customization & Utilities
- Clear screen, check disk storage.
- Change terminal background color.
- Open websites in a browser.

### Session Management
- `logout` command allows switching users without restarting.

---

## Why Termulation?

Termulation is more than a terminal emulator — it’s an educational tool to:
- Learn command-line workflows in a controlled environment.
- Understand user permissions and admin access.
- Experiment with filesystem operations and process management.
- Practice Python programming concepts like Tkinter UI, JSON storage, and event handling.

---

## Installation & Usage

1. Ensure Python 3.x is installed.
2. Run `termulation.py` using:

```bash
python termulation.py
