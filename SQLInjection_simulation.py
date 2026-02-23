import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading

# --- Xüsusi SQL Funksiyaları ---

# 1. TIME-BASED: Bazanı yatızdırmaq
def db_sleep(seconds):
    time.sleep(float(seconds))
    return float(seconds)

# 2. FILE READ: Serverdən fayl oxumaq (Simulyasiya)
# Bu funksiya MySQL-dəki LOAD_FILE() əmrini təqlid edir.
def db_load_file(filename):
    # Real fayl sistemini qorumuruq, sadəcə simulyasiya edirik
    fake_files = {
        "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/sh",
        "c:/windows/win.ini": "[fonts]\nArial=arial.ttf\n[extensions]\nfont=font.drv",
        "config.php": "<?php\n$db_password = 'SUPER_HARD_PASSWORD_2025';\n?>"
    }
    return fake_files.get(filename, "NULL (File not found or permission denied)")

# --- Verilənlər Bazası ---
def init_db():
    global connection, cursor
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    
    # Python funksiyalarını SQL daxilində qeydiyyatdan keçiririk
    connection.create_function("sleep", 1, db_sleep)
    connection.create_function("load_file", 1, db_load_file) # Yeni funksiya!
    
    cursor = connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    
    # Məlumatları təmizlə
    cursor.execute("DELETE FROM users")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '12345')")
    cursor.execute("INSERT INTO users (username, password) VALUES ('user', 'abcde')")
    connection.commit()

init_db()

# --- WAF (Firewall) Məntiqi ---
def waf_check(payload):
    # Əgər WAF aktivdirsə, təhlükəli sözləri axtarır
    blacklist = ["UNION", "SELECT", "SLEEP", "BENCHMARK", "--", "DROP"]
    
    payload_upper = payload.upper()
    
    for word in blacklist:
        if word in payload_upper:
            return False, f"WAF BLOCKED: '{word}' sözü qadağandır!"
    return True, ""

# --- Login Funksiyası ---
def insecure_login(username, password, use_waf):
    start_time = time.time()
    
    # 1. WAF Yoxlaması (Əgər aktivdirsə)
    if use_waf:
        is_safe, message = waf_check(username + password)
        if not is_safe:
            return None, message, 0

    # 2. SQL Sorğusu
    query = f"SELECT id, username, password FROM users WHERE username='{username}' AND password='{password}'"
    
    # GUI-də sorğunu göstər
    label_query_display.config(text=f"Sorğu:\n{query}", fg="#0000aa")

    try:
        # Stacked Query Simulation
        if ";" in query:
            cursor.executescript(query)
            duration = time.time() - start_time
            return None, f"Script icra edildi! (Müddət: {duration:.2f}s)", duration
        
        cursor.execute(query)
        result = cursor.fetchall()
        duration = time.time() - start_time
        return result, None, duration

    except Exception as e:
        duration = time.time() - start_time
        return None, str(e), duration

# --- UI Hadisələri ---
def on_login_button_click():
    threading.Thread(target=process_login).start()

def process_login():
    username = entry_username.get()
    password = entry_password.get()
    use_waf = waf_var.get() # Checkbox vəziyyəti

    btn_login.config(state="disabled", text="Gözləyin...")
    
    users, error, duration = insecure_login(username, password, use_waf)

    btn_login.config(state="normal", text="Giriş (Login)")

    # Nəticələrin analizi
    if error:
        if "WAF BLOCKED" in error:
            messagebox.showwarning("Hücum Təsbit Edildi!", error)
        elif "no such table" in str(error):
            messagebox.showinfo("Stacked Query", "Cədvəl silindi! (Stacked Query Uğurlu)")
        else:
            messagebox.showerror("SQL Xətası", f"Verilənlər bazası xətası:\n{error}")
    
    elif duration > 2.0:
        messagebox.showwarning("Time-Based Injection", f"DİQQƏT! Sorğu {duration:.2f} saniyə çəkdi.")

    elif users:
        # Nəticəni gözəl formatda göstərək
        res_str = ""
        for u in users:
            # 3-cü element password və ya bizim oğurladığımız fayl ola bilər
            res_str += f"User: {u[1]} | Data: {u[2]}\n"
        messagebox.showinfo("Uğurlu", f"Tapılan məlumatlar:\n\n{res_str}")
    else:
        messagebox.showerror("Uğursuz", "Giriş rədd edildi.")

# --- GUI ---
root = tk.Tk()
root.title("Ultimate SQLi Lab: WAF & Files")
root.geometry("600x550")

# Başlıq
tk.Label(root, text="SQL Injection Laboratory", font=("Impact", 18)).pack(pady=10)

# WAF Seçimi
waf_frame = tk.Frame(root, relief="groove", borderwidth=2)
waf_frame.pack(pady=5, padx=10, fill="x")
waf_var = tk.BooleanVar()
chk_waf = tk.Checkbutton(waf_frame, text="WAF (Firewall) Aktiv et", variable=waf_var, font=("Arial", 10, "bold"), fg="red")
chk_waf.pack(pady=5)
tk.Label(waf_frame, text="(Aktiv olduqda 'UNION', 'SELECT' kimi sözlər bloklanır)").pack()

# Form
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="e")
entry_username = tk.Entry(form_frame, width=50)
entry_username.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="e")
entry_password = tk.Entry(form_frame, width=50)
entry_password.grid(row=1, column=1, padx=5, pady=5)

btn_login = tk.Button(root, text="Giriş (Login)", command=on_login_button_click, bg="#2196F3", fg="white", font=("Arial", 11))
btn_login.pack(pady=10)

# Sorğu Paneli
label_query_title = tk.Label(root, text="Serverdə icra olunan sorğu:", font=("Arial", 10, "italic"))
label_query_title.pack()

label_query_display = tk.Label(root, text="...", wraplength=550, justify="left", relief="sunken", bg="#f0f0f0", font=("Consolas", 9))
label_query_display.pack(pady=5, ipady=10, fill="x", padx=20)

# Cheat Sheet (Köməkçi)
lbl_help = tk.Label(root, text="Kömək: Fayl oxumaq üçün 'load_file' istifadə edin.", fg="gray")
lbl_help.pack(side="bottom", pady=10)

root.mainloop()
