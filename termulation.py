import tkinter as tk
from tkinter import colorchooser
import time, random, webbrowser, json, os

v = "0.1.0"
root = tk.Tk()
root.title(f"Termulation {v}")
root.geometry("1000x600")
root.configure(bg="black")
font = ("Courier", 12)

terminal = tk.Text(root,bg="black",fg="white",insertbackground="white",font=font,bd=0)
terminal.pack(fill="both",expand=True)
terminal.focus()

# -------- Globals --------
input_start = "1.0"
command_history = []
history_index = -1

total_storage = 10000
used_storage = 0
package_sizes = {}
installed_packages = []
existing_packages = ["xonotic","sudoku","python3.13","python3.9","dolphinemu-2506a","bugsquish","blender50"]

# -------- Filesystem --------
fs = {
    "f": {"users": {}},
    "bin": {},
    "etc": {},
    "var": {"log": {"system.log":{"content":"","owner":"root","permissions":"rw"}}}
}
current_path = []

# Trash per user
trash_bin = {}

# Processes
process_list = []

# Users
users = [{"username":"admin","password":"1234"}]

# Load users from JSON if exists
if os.path.exists("users.json"):
    try:
        with open("users.json","r") as f:
            users = json.load(f)
            for u in users:
                if u["username"] not in fs["f"]["users"]:
                    fs["f"]["users"][u["username"]] = {}
                    trash_bin[u["username"]] = {}
    except:
        pass

# -------- Helpers --------
def write(text, tag=None):
    terminal.insert("end", text, tag if tag else "")
    terminal.see("end")
    root.update()

terminal.tag_configure("bold", font=("Courier",12,"bold"))

def get_input(): return terminal.get(input_start,"insert").strip()
def calculate_size(content): return len(content.encode("utf-8"))
def clamp_storage(): global used_storage; used_storage = max(0,min(total_storage,used_storage))

def get_current_folder():
    folder = fs
    for p in current_path:
        folder = folder[p]
    return folder

def get_path_string(username=None):
    if current_path: return "/" + "/".join(current_path)
    elif username: return f"/f/users/{username}"
    else: return "/"

# -------- Boot --------
boot_lines = [
    "Termulation BIOS v2.0 Release",
    "Initializing Hardware .......... OK",
    f"Checking Memory ................ {total_storage} bytes OK",
    "Starting Termulation OS ........ OK",
    "",
]
boot_index = 0
def boot_screen():
    global boot_index
    if boot_index < len(boot_lines):
        write(boot_lines[boot_index] + "\n")
        boot_index += 1
        root.after(400, boot_screen)
    else:
        write("\nSystem Ready.\n\n")
        start_login()

# -------- Login --------
def start_login():
    global input_start
    write("LOG IN\nUsername(default: admin): ")
    input_start = terminal.index("insert")
    terminal.bind("<Return>", handle_username)

def handle_username(event):
    username = get_input()
    write("\nPassword(default: 1234): ")
    global input_start
    input_start = terminal.index("insert")
    terminal.bind("<Return>", lambda e: handle_password(e,username))
    return "break"

def handle_password(event,username):
    password = get_input()
    write("\n")
    if any(u["username"]==username and u["password"]==password for u in users):
        if username not in fs["f"]["users"]:
            fs["f"]["users"][username] = {}
            trash_bin[username] = {}
        start_terminal(username)
    else:
        write("Invalid credentials.\n\n")
        start_login()
    return "break"

# -------- Terminal --------
def start_terminal(username):
    global input_start
    write(f"@{username}:{get_path_string(username)}> ")
    input_start = terminal.index("insert")
    terminal.bind("<Return>", lambda e: handle_command(e,username))
    terminal.bind("<Up>", lambda e: show_history(e,"up"))
    terminal.bind("<Down>", lambda e: show_history(e,"down"))

def show_history(event,direction):
    global history_index,input_start
    if not command_history: return "break"
    if direction=="up":
        if history_index==-1: history_index=len(command_history)-1
        elif history_index>0: history_index-=1
    elif direction=="down":
        if history_index<len(command_history)-1: history_index+=1
        else: history_index=-1; terminal.delete(input_start,"end"); return "break"
    terminal.delete(input_start,"end")
    if history_index!=-1: terminal.insert("end",command_history[history_index])
    terminal.mark_set("insert","end")
    return "break"

# -------- Storage & Packages --------
def disk_storage():
    clamp_storage()
    free = total_storage-used_storage
    percent=int((used_storage/total_storage)*100)
    bar=int(percent/5)
    write(f"Used: {used_storage} bytes | Free: {free} bytes\n")
    write("["+ "#"*bar + "-"*(20-bar)+f"] {percent}%\n")

def fake_install(package_name):
    global used_storage, installed_packages, package_sizes
    size=random.randint(50,500)
    if used_storage+size>total_storage:
        write(f"Not enough storage to install {package_name} ({size} bytes).\n")
        return
    used_storage+=size
    package_sizes[package_name]=size
    write(f"Installing {package_name} ({size} bytes):\n","bold")
    total=20
    for i in range(total+1):
        percent=int(i/total*100)
        bar="#"*i+"-"*(total-i)
        if i>0: terminal.delete(f"end-{len(bar)+6}c","end")
        write(f"[{bar}] {percent}%\r")
        root.update()
        time.sleep(0.1)
    write(f"[{'#'*total}] 100%\n")
    installed_packages.append(package_name)
    write(f"{package_name} installed successfully!\n")

def tpm_remove(package_name, username):
    if username != "admin":
        write("Permission Denied!\nYou must have administrative access!\n")
        return
    global used_storage, installed_packages
    if package_name in installed_packages:
        used_storage-=package_sizes.get(package_name,0)
        package_sizes.pop(package_name,None)
        installed_packages.remove(package_name)
        write(f"Package '{package_name}' removed.\n")
    else:
        write(f"Package '{package_name}' is not installed.\n")

def tpm_list():
    if not installed_packages:
        write("No packages installed.\n")
        return
    for pkg in installed_packages:
        write(f"{pkg} ({package_sizes.get(pkg,0)} bytes)\n")

# -------- FS & Trash --------
def mkdir(name):
    folder=get_current_folder()
    if name not in folder: folder[name]={}

def rmdir(name):
    folder=get_current_folder()
    if name in folder and isinstance(folder[name],dict) and not folder[name]: del folder[name]

def ls():
    folder=get_current_folder()
    for k,v in folder.items():
        if isinstance(v,dict): write(f"[DIR] {k}\n")
        else: write(f"{k}\n")

def cd(path):
    global current_path
    if path=="/": current_path=["f","users"]; return
    for p in path.split("/"):
        if p=="..": current_path.pop() if current_path else None
        elif p:
            folder=get_current_folder()
            if p in folder and isinstance(folder[p],dict): current_path.append(p)
            else: write("Directory not found.\n"); break

def pwd(username): write(get_path_string(username)+"\n")

def move_to_trash(file_name,username):
    folder=get_current_folder()
    if file_name in folder and not isinstance(folder[file_name],dict):
        trash_bin[username][file_name]=folder.pop(file_name)
        write(f"{file_name} moved to Trash.\n")

def trash_list(username):
    tb=trash_bin.get(username,{})
    if not tb: write("Trash is empty.\n")
    else: [write(f"{name}\n") for name in tb]

def trash_restore(file_name,username):
    tb=trash_bin.get(username,{})
    if file_name in tb:
        get_current_folder()[file_name]=tb.pop(file_name)
        write(f"{file_name} restored.\n")

def trash_empty(username):
    global used_storage
    tb=trash_bin.get(username,{})
    for content in tb.values():
        used_storage-=calculate_size(content)
    trash_bin[username]={}
    clamp_storage()
    write("Trash emptied.\n")

# -------- Processes & Networking --------
def ps(): 
    if not process_list: write("No running processes.\n")
    else: [write(f"{p}\n") for p in process_list]

def kill(proc):
    if proc in process_list: process_list.remove(proc); write(f"{proc} killed.\n")
    else: write("Process not found.\n")

def ping(host): write(f"Pinging {host} ... Success!\n")
def connect(host): write(f"Connecting to {host} ... Connected!\n")

# -------- Utilities --------
def clear_screen(): terminal.delete("1.0","end")
def open_browser(site):
    try: webbrowser.open(site); write(f"Opening {site}...\n")
    except: write("Failed to open browser.\n")
def set_bg_color():
    color=colorchooser.askcolor(title="Choose Terminal Background")[1]
    if color: terminal.config(bg=color); write(f"Background color changed to {color}\n")

# -------- Command Handler --------
def handle_command(event,username):
    global input_start,history_index
    cmd=get_input()
    command_history.append(cmd)
    history_index=-1
    write("\n")
    
    # --- Help & basic ---
    if cmd=="help":
        write("cls,diskstorage,tpm install/remove/list,mkdir,rmdir,ls,cd,pwd,ps,kill,ping,connect,browser open,setcolor,usr create/delete/setname/setpass,logout,notify\n")
    elif cmd=="cls": clear_screen()
    elif cmd=="diskstorage": disk_storage()
    
    # --- TPM ---
    elif cmd.startswith("tpm install "):
        if username != "admin":
            write("Permission Denied!\nYou must have administrative access!\n")
        else:
            parts = cmd.split()[2:]
            if not parts:
                write("Usage: tpm install <package1> [package2 ...]\n")
            else:
                for pkg in parts:
                    if pkg not in existing_packages:
                        write(f"Package '{pkg}' not found.\n")
                    elif pkg in installed_packages:
                        write(f"Package '{pkg}' is already installed.\n")
                    else:
                        write(f"Warning: Installing {pkg} may use storage.\nContinue? (yes/no) ")
                        input_start = terminal.index("insert")
                        def confirm(e, package_name=pkg):
                            answer = get_input().lower()
                            write("\n")
                            if answer == "yes":
                                fake_install(package_name)
                            start_terminal(username)
                            return "break"
                        terminal.bind("<Return>", confirm)
                        return "break"
    elif cmd.startswith("tpm remove "):
        tpm_remove(cmd.split(maxsplit=2)[2], username)
    elif cmd=="tpm list": tpm_list()
    
    # --- FS ---
    elif cmd.startswith("mkdir "): mkdir(cmd.split(maxsplit=1)[1])
    elif cmd.startswith("rmdir "): rmdir(cmd.split(maxsplit=1)[1])
    elif cmd=="ls": ls()
    elif cmd.startswith("cd "): cd(cmd.split(maxsplit=1)[1])
    elif cmd=="pwd": pwd(username)
    
    # --- Processes & network ---
    elif cmd=="ps": ps()
    elif cmd.startswith("kill "): kill(cmd.split(maxsplit=1)[1])
    elif cmd.startswith("ping "): ping(cmd.split(maxsplit=1)[1])
    elif cmd.startswith("connect "): connect(cmd.split(maxsplit=1)[1])
    
    # --- Utilities ---
    elif cmd.startswith("browser open "): open_browser(cmd.split(maxsplit=2)[2])
    elif cmd=="setcolor": set_bg_color()
    
    # --- Trash ---
    elif cmd.startswith("rm "): move_to_trash(cmd.split(maxsplit=1)[1],username)
    elif cmd=="trash list": trash_list(username)
    elif cmd.startswith("trash restore "): trash_restore(cmd.split(maxsplit=2)[2],username)
    elif cmd=="trash empty": trash_empty(username)
    
    # --- User management ---
    elif cmd.startswith("usr create "):
        if username != "admin":
            write("Permission Denied!\nYou must have administrative access!\n")
        else:
            parts = cmd.split(maxsplit=3)
            if len(parts) < 4:
                write("Usage: usr create <username> <password>\n")
            else:
                new_username = parts[2]
                new_password = parts[3]
                if any(u["username"]==new_username for u in users):
                    write(f"User '{new_username}' already exists.\n")
                else:
                    users.append({"username": new_username, "password": new_password})
                    fs["f"]["users"][new_username] = {}
                    trash_bin[new_username] = {}
                    try:
                        with open("users.json", "w") as f:
                            json.dump(users, f, indent=4)
                        write(f"User '{new_username}' created successfully!\n")
                    except Exception as e:
                        write(f"Failed to save user: {e}\n")
                        
    elif cmd.startswith("usr delete "):
        if username != "admin":
            write("Permission Denied!\nYou must have administrative access!\n")
        else:
            parts = cmd.split(maxsplit=2)
            if len(parts) < 3:
                write("Usage: usr delete <username>\n")
            else:
                del_username = parts[2]
                if del_username == "admin":
                    write("Cannot delete admin user.\n")
                elif not any(u["username"]==del_username for u in users):
                    write(f"User '{del_username}' not found.\n")
                else:
                    users[:] = [u for u in users if u["username"] != del_username]
                    fs["f"]["users"].pop(del_username, None)
                    trash_bin.pop(del_username, None)
                    try:
                        with open("users.json", "w") as f:
                            json.dump(users, f, indent=4)
                        write(f"User '{del_username}' deleted successfully.\n")
                    except Exception as e:
                        write(f"Failed to save users: {e}\n")
                        
    elif cmd.startswith("usr setname "):
        if username != "admin":
            write("Permission Denied!\nYou must have administrative access!\n")
        else:
            parts = cmd.split(maxsplit=3)
            if len(parts) < 4:
                write("Usage: usr setname <old_username> <new_username>\n")
            else:
                old_username = parts[2]
                new_username = parts[3]
                if old_username == "admin":
                    write("Cannot change admin username!\n")
                elif old_username == username:
                    write("Cannot change your own username while logged in!\n")
                elif not any(u["username"] == old_username for u in users):
                    write(f"User '{old_username}' not found.\n")
                elif any(u["username"] == new_username for u in users):
                    write(f"Username '{new_username}' already exists.\n")
                else:
                    for u in users:
                        if u["username"] == old_username:
                            u["username"] = new_username
                            break
                    fs["f"]["users"][new_username] = fs["f"]["users"].pop(old_username, {})
                    trash_bin[new_username] = trash_bin.pop(old_username, {})
                    try:
                        with open("users.json", "w") as f:
                            json.dump(users, f, indent=4)
                        write(f"Username changed from '{old_username}' to '{new_username}' successfully!\n")
                    except Exception as e:
                        write(f"Failed to save users: {e}\n")
                        
    elif cmd.startswith("usr setpass "):
        if username != "admin":
            write("Permission Denied!\nYou must have administrative access!\n")
        else:
            parts = cmd.split(maxsplit=3)
            if len(parts) < 4:
                write("Usage: usr setpass <username> <new_password>\n")
            else:
                target_user = parts[2]
                new_password = parts[3]
                if target_user == "admin":
                    write("Cannot change admin password!\n")
                elif target_user == username:
                    write("Cannot change your own password while logged in!\n")
                elif not any(u["username"] == target_user for u in users):
                    write(f"User '{target_user}' not found.\n")
                else:
                    for u in users:
                        if u["username"] == target_user:
                            u["password"] = new_password
                            break
                    try:
                        with open("users.json", "w") as f:
                            json.dump(users, f, indent=4)
                        write(f"Password for '{target_user}' updated successfully!\n")
                    except Exception as e:
                        write(f"Failed to save users: {e}\n")
    
    # --- Logout ---
    elif cmd == "logout":
        write("\nLogging out...\n\n")
        start_login()
        return "break"
    else:
        write("Unknown command.\n")
    
    write(f"@{username}:{get_path_string(username)}> ")
    input_start=terminal.index("insert")
    return "break"

boot_screen()
root.mainloop()
