import customtkinter as ctk
import threading
import sys
import os
import queue
import re
import csv

# Import backend modules
import generate_accounts
import signin_accounts
import export_utils
import tag_manager
import csv_utils
from colorama import Fore
from PIL import Image

# Configure global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  # Using built-in dark-blue for specific elements

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Constants & Colors ---
COLOR_PRIMARY = "#2cc985"      # Vibrant Green for primary actions
COLOR_PRIMARY_HOVER = "#23a16a"

COLOR_SECONDARY = "#1f6aa5"    # Ocean Blue for secondary actions
COLOR_SECONDARY_HOVER = "#144870"

COLOR_DANGER = "#c92c2c"       # Red for danger
COLOR_DANGER_HOVER = "#962121"

COLOR_BG_DARK = "#1a1a1a"      # Main Window BG
COLOR_CARD_BG = "#2b2b2b"      # Card/Frame BG
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_SUB = "#cccccc"

FONT_MAIN = ("Roboto", 13)
FONT_HEADER = ("Roboto Medium", 20)
FONT_SUBHEADER = ("Roboto Medium", 15)


class MegaGenGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mega Account Generator GUI")
        self.geometry("900x600")

        # Set icon
        try:
            self.iconbitmap(resource_path("logo.ico"))
        except:
            pass # Icon not found or format issue

        self.configure(fg_color=COLOR_BG_DARK)
        
        # --- Layout Configuration ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.log_queue = queue.Queue()
        self.is_running = False

        # --- Sidebar (Left) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MEGA\nGenerator", font=("Roboto", 26, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_nav_gen = ctk.CTkButton(self.sidebar_frame, text="Generator", command=self.show_generator,
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         anchor="w", width=180, font=FONT_SUBHEADER)
        self.btn_nav_gen.grid(row=1, column=0, padx=10, pady=10)

        self.btn_nav_acc = ctk.CTkButton(self.sidebar_frame, text="Stored Accounts", command=self.show_accounts,
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         anchor="w", width=180, font=FONT_SUBHEADER)
        self.btn_nav_acc.grid(row=2, column=0, padx=10, pady=10)

        # Logo at bottom
        self.sidebar_frame.grid_rowconfigure(3, weight=1) # Spacer
        try:
            pil_image = Image.open(resource_path("logo.png"))
            self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(100, 100))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="", image=self.logo_image)
            self.logo_label.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        except Exception as e:
            print(f"Logo load error: {e}")

        # --- Main Content Area (Right) ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.generator_view = GeneratorView(self.main_frame, self)
        self.accounts_view = AccountsView(self.main_frame, self)
        
        # Default view
        self.show_generator()

        # Redirect backend logs
        generate_accounts.set_log_callback(self.append_log)
        signin_accounts.set_log_callback(self.append_log)
        
        self.status_queue = queue.Queue()
        generate_accounts.set_status_callback(self.append_status)
        
        # Start log poller
        self.after(100, self.poll_log_queue)

    def show_generator(self):
        self.accounts_view.pack_forget()
        self.generator_view.pack(fill="both", expand=True)
        self.btn_nav_gen.configure(fg_color=("gray75", "gray25"))
        self.btn_nav_acc.configure(fg_color="transparent")

    def show_accounts(self):
        self.generator_view.pack_forget()
        self.accounts_view.pack(fill="both", expand=True)
        self.accounts_view.load_accounts() # Auto reload
        self.btn_nav_gen.configure(fg_color="transparent")
        self.btn_nav_acc.configure(fg_color=("gray75", "gray25"))

    def append_log(self, message):
        self.log_queue.put(message)

    def append_status(self, index, email, status):
        self.status_queue.put((index, email, status))

    def poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if self.generator_view.winfo_exists():
                    self.generator_view.log_box.configure(state="normal")
                    clean_msg = re.sub(r'\x1b\[[0-9;]*m', '', str(msg))
                    self.generator_view.log_box.insert("end", clean_msg + "\n")
                    self.generator_view.log_box.see("end")
                    self.generator_view.log_box.configure(state="disabled")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.poll_log_queue)
            
    def confirm_stop(self):
        # Using a simple dialog to confirm
        from tkinter import messagebox
        return messagebox.askyesno("Stop Process", "Are you sure you want to stop the current process?")

# --- Generator View ---
class GeneratorView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Log area expands

        # Settings Card
        self.settings_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10)
        self.settings_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
        self.settings_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self.settings_frame, text="Generation Settings", font=FONT_HEADER, text_color=COLOR_TEXT_MAIN).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=15)

        # Inputs
        self.num_accounts_var = ctk.StringVar(value="3")
        self.num_threads_var = ctk.StringVar(value="3")
        self.password_var = ctk.StringVar(value="")

        self._create_input(self.settings_frame, 1, 0, "Accounts", self.num_accounts_var)
        self._create_input(self.settings_frame, 1, 1, "Threads (Max 8)", self.num_threads_var)
        self._create_input(self.settings_frame, 1, 2, "Common Password (Optional)", self.password_var)

        # Action Buttons
        self.btn_gen = ctk.CTkButton(self.settings_frame, text="Start Generation", font=("Roboto", 14, "bold"),
                                     fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER, height=40,
                                     command=self.start_generation)
        self.btn_gen.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.btn_signin = ctk.CTkButton(self.settings_frame, text="Check Storage / Sign In", font=("Roboto", 14, "bold"),
                                        fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER, height=40,
                                        command=self.start_signin)
        self.btn_signin.grid(row=2, column=2, columnspan=2, padx=20, pady=20, sticky="ew")

        self.btn_stop = ctk.CTkButton(self.settings_frame, text="Stop", font=("Roboto", 14, "bold"),
                                      fg_color="gray", hover_color=COLOR_DANGER_HOVER, height=40,
                                      state="disabled", command=self.stop_process)
        self.btn_stop.grid(row=3, column=0, columnspan=4, padx=20, pady=(0, 20), sticky="ew")

        # Live Status Table (Replaces Log Box)
        self.log_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10)
        self.log_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.log_frame.grid_rowconfigure(1, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.log_frame, text="Activity Log", font=FONT_SUBHEADER, text_color=COLOR_TEXT_SUB).grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.log_box = ctk.CTkTextbox(self.log_frame, font=("Consolas", 12), fg_color="#1e1e1e", text_color="#d4d4d4")
        self.log_box.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_box.configure(state="disabled")

        # Metrics & Log Text (Mini log below table)
        self.metrics_label = ctk.CTkLabel(self.log_frame, text="Ready to start.", font=("Roboto", 12), text_color=COLOR_TEXT_SUB)
        self.metrics_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 0))

        self.progress_bar = ctk.CTkProgressBar(self.log_frame, progress_color=COLOR_PRIMARY)
        self.progress_bar.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.progress_bar.set(0)

    def _create_input(self, parent, row, col, label_text, variable):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame, text=label_text, font=FONT_MAIN, text_color=COLOR_TEXT_SUB).pack(anchor="w", pady=(0, 5))
        ctk.CTkEntry(frame, textvariable=variable, height=35).pack(fill="x")

    def start_generation(self):
        if self.controller.is_running: return
        try:
            num = int(self.num_accounts_var.get())
            threads = int(self.num_threads_var.get())
            password = self.password_var.get() or None
        except ValueError:
            self.controller.append_log("Error: Invalid number input.")
            return

        # Reset stop flags
        generate_accounts.STOP_FLAG = False
        signin_accounts.STOP_FLAG = False

        self.controller.is_running = True
        self._toggle_buttons(False)
        self.progress_bar.set(0)
        
        # Pass password directly based on our previous fix
        threading.Thread(target=self._run_gen_thread, args=(num, threads, password), daemon=True).start()

    def start_signin(self):
        if self.controller.is_running: return
        
        # Reset stop flags
        generate_accounts.STOP_FLAG = False
        signin_accounts.STOP_FLAG = False

        self.controller.is_running = True
        self._toggle_buttons(False)
        self.progress_bar.set(0)
        threading.Thread(target=self._run_signin_thread, daemon=True).start()

    def stop_process(self):
        if not self.controller.is_running: return
        if self.controller.confirm_stop():
            generate_accounts.stop()
            signin_accounts.stop()
            self.controller.append_log("Stopping process...")
            self.btn_stop.configure(state="disabled", text="Stopping...")

    def _toggle_buttons(self, state):
        s = "normal" if state else "disabled"
        self.btn_gen.configure(state=s)
        self.btn_signin.configure(state=s)
        
        # Stop button logic
        if not state: # Running
            self.btn_stop.configure(state="normal", text="STOP", fg_color=COLOR_DANGER)
        else: # Idle
            self.btn_stop.configure(state="disabled", text="Stop", fg_color="gray")

    def _run_gen_thread(self, total, threads, password):
        self.controller.append_log(f"Starting generation of {total} accounts...")
        # Pass controller for thread-safe progress updates
        pbar = ProgressWrapper(self.progress_bar.set, total, self.controller)
        
        success_count = 0
        total_time = 0
        
        try:
            if threads > 1:
                thread_list = []
                result_queue = queue.Queue()
                
                def thread_wrapper(idx, p, pw, q):
                    # We pass 'idx' as index to new_account
                    res = generate_accounts.new_account(idx, p, pw)
                    q.put(res)

                for i in range(total):
                    if generate_accounts.STOP_FLAG: break
                    t = threading.Thread(target=thread_wrapper, args=(i, pbar, password, result_queue))
                    thread_list.append(t)
                    t.start()
                    import time; time.sleep(0.5) # stagger
                
                for t in thread_list: t.join()
                
                # Collect stats
                while not result_queue.empty():
                    res = result_queue.get()
                    if res.get("success"): success_count += 1
                    total_time += res.get("time", 0)
            else:
                for i in range(total):
                    if generate_accounts.STOP_FLAG: break
                    res = generate_accounts.new_account(i, pbar, password)
                    if res.get("success"): success_count += 1
                    total_time += res.get("time", 0)
            
            avg_time = (total_time / total) if total > 0 else 0
            
            msg = f"Completed. Success: {success_count}/{total} | Avg Time: {avg_time:.2f}s"
            if generate_accounts.STOP_FLAG: msg += " (Stopped)"
            
            self.metrics_label.configure(text=msg, text_color=COLOR_PRIMARY if success_count > 0 else COLOR_TEXT_SUB)
            self.controller.append_log(msg)

        except Exception as e:
            self.controller.append_log(f"Error: {e}")
        finally:
            self.controller.is_running = False
            self.progress_bar.set(1.0)
            self._toggle_buttons(True)

    def _run_signin_thread(self):
        try:
            if not csv_utils.csv_exists():
                self.controller.append_log("Error: accounts.csv not found.")
                return
            
            
            # Simple line count for progress
            total = csv_utils.count_accounts()
            
            if total < 1:
                self.controller.append_log("No accounts to sign in.")
                return

            pbar = ProgressWrapper(self.progress_bar.set, total, self.controller)
            signin_accounts.main(pbar, check_only_storage=True)
            
            if signin_accounts.STOP_FLAG:
                self.controller.append_log("Sign In Stopped.")

        except Exception as e:
            self.controller.append_log(f"Error during sign in: {e}")
        finally:
            self.controller.is_running = False
            self.progress_bar.set(1.0)
            self._toggle_buttons(True)

# --- Accounts View ---
class AccountsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.all_accounts = []  # Store all accounts for filtering
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Changed from 1 to 2

        # Header Card
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        
        ctk.CTkLabel(self.header_frame, text="Stored Accounts", font=FONT_HEADER, text_color=COLOR_TEXT_MAIN).pack(side="left", padx=20, pady=15)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(btn_frame, text="Export", width=80, command=self.show_export_menu, 
                     fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Import", width=80, command=self.show_import_menu,
                     fg_color=COLOR_SECONDARY, hover_color=COLOR_SECONDARY_HOVER).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", width=80, command=self.load_accounts, 
                     fg_color="transparent", border_width=1, text_color=COLOR_TEXT_MAIN).pack(side="left", padx=5)
        
        # Search & Filter Bar
        self.search_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10, height=60)
        self.search_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
        
        # Search entry
        ctk.CTkLabel(self.search_frame, text="🔍", font=("Roboto", 18)).pack(side="left", padx=(20, 5))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.apply_filters())
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search by email...", 
                                        textvariable=self.search_var, width=300)
        self.search_entry.pack(side="left", padx=5, pady=15)
        
        # Filter dropdown
        ctk.CTkLabel(self.search_frame, text="Filter:", text_color=COLOR_TEXT_SUB).pack(side="left", padx=(20, 5))
        self.filter_var = ctk.StringVar(value="All")
        self.filter_dropdown = ctk.CTkOptionMenu(self.search_frame, variable=self.filter_var,
                                                values=["All", "Active", "Failed", "Disabled", "Unknown"],
                                                command=lambda x: self.apply_filters(), width=120)
        self.filter_dropdown.pack(side="left", padx=5)

    # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")

    def load_accounts(self):
        """Load all accounts from CSV"""
        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        # Safe read via utils
        rows = csv_utils.read_accounts()
            
        if not rows:
            ctk.CTkLabel(self.scroll_frame, text="No accounts found.", text_color=COLOR_TEXT_SUB).pack(pady=20)
            self.all_accounts = []
            return
        
        # Store all accounts
        self.all_accounts = rows
        
        # Update filter dropdown with Tags
        base_filters = ["All", "Active", "Failed", "Disabled", "Unknown"]
        all_tags = tag_manager.TagManager.get_all_tags()
        
        # Prefix tags to distinguish them or just section them
        # We'll rely on the fact that status are specific words.
        # If a tag matches a status, it might be ambiguous, but unlikely to be an issue for now.
        # To be safe, we can check if selected value is in base_filters.
        
        self.filter_dropdown.configure(values=base_filters + all_tags)
        
        # Display accounts (will be filtered if search/filter active)
        self.apply_filters()
    
    def apply_filters(self):
        """Filter and display accounts based on search and filter criteria"""
        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        if not self.all_accounts:
            ctk.CTkLabel(self.scroll_frame, text="No accounts to display.", text_color=COLOR_TEXT_SUB).pack(pady=20)
            return
        
        search_query = self.search_var.get().lower().strip()
        filter_status = self.filter_var.get()
        
        # Define reserved status keywords
        status_keywords = ["All", "Active", "Failed", "Disabled", "Unknown"]
        
        filtered = []
        for row in self.all_accounts:
            if not row:
                continue
            
            email = row[0].lower() if len(row) > 0 else ""
            status = row[4] if len(row) > 4 else "Unknown"
            
            # Get tags for this account
            # Row index 5 is tags (csv_utils normalization ensures this)
            tags_str = row[5] if len(row) > 5 else ""
            account_tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            
            # Apply search filter
            if search_query and search_query not in email:
                continue
            
            # Apply filter logic
            if filter_status != "All":
                if filter_status in status_keywords:
                    # It's a status filter
                    if filter_status == "Active" and status != "Active":
                        continue
                    elif filter_status == "Failed" and "Failed" not in status:
                        continue
                    elif filter_status == "Disabled" and status != "Disabled":
                        continue
                    elif filter_status == "Unknown" and status not in ["Unknown", ""]:
                        continue
                else:
                    # It's a TAG filter
                    # If the selected filter is NOT in status_keywords, assume it's a tag
                    if filter_status not in account_tags:
                        continue
            
            filtered.append(row)
        
        # Display filtered results
        if filtered:
            for row in filtered:
                AccountRow(self.scroll_frame, row, self.load_accounts).pack(fill="x", padx=10, pady=5)
        else:
            ctk.CTkLabel(self.scroll_frame, text=f"No accounts match your search.", 
                        text_color=COLOR_TEXT_SUB).pack(pady=20)
    
    def show_export_menu(self):
        """Show export format selection dialog"""
        from tkinter import filedialog, messagebox
        
        dialog = ExportDialog(self.winfo_toplevel(), self.controller)
        
    def show_import_menu(self):
        """Show import file selection dialog"""
        from tkinter import filedialog, messagebox
        
        filetypes = [
            ("JSON files", "*.json"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Import Accounts",
            filetypes=filetypes
        )
        
        if not filepath:
            return
        
        try:
            # Detect format and import
            if filepath.endswith('.json'):
                accounts = export_utils.import_from_json(filepath)
            elif filepath.endswith('.xlsx'):
                accounts = export_utils.import_from_excel(filepath)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
            
            # Confirm import
            if messagebox.askyesno("Confirm Import", 
                                  f"Import {len(accounts)} accounts? This will replace accounts.csv"):
                # Write to CSV
                csv_utils.write_accounts(accounts)
                
                messagebox.showinfo("Success", f"Imported {len(accounts)} accounts successfully!")
                self.load_accounts()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {str(e)}")

class AccountRow(ctk.CTkFrame):
    def __init__(self, parent, row_data, reload_cb):
        super().__init__(parent, fg_color="#333333", corner_radius=8)
        self.row_data = row_data
        self.reload_cb = reload_cb
        self.email = row_data[0]
        self.password = row_data[1]
        self.status = row_data[4] if len(row_data) > 4 else "Unknown"
        self.used = row_data[2] if len(row_data) > 2 else "?"
        self.free = row_data[3] if len(row_data) > 3 else "?"

        self.grid_columnconfigure(0, weight=1) # Email expands
        self.pack_propagate(False)
        self.configure(height=60) # Increased height for tags + buttons

        # Email & Tags
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=5)
        
        # Determine color based on status
        email_color = "white"
        if self.status == "Disabled":
            email_color = "gray50"
        elif self.status == "Active":
            email_color = COLOR_PRIMARY
        elif "Failed" in self.status:
            email_color = COLOR_DANGER
            
        ctk.CTkLabel(info_frame, text=self.email, font=("Roboto", 13, "bold"), text_color=email_color).pack(anchor="w")
        
        # Tags display
        tags = tag_manager.TagManager.get_account_tags(self.email)
        tag_text = ""
        if tags:
            tag_text = " ".join([f"[{t}]" for t in tags[:3]])
            if len(tags) > 3: tag_text += f" +{len(tags)-3}"
            
        if tag_text:
            ctk.CTkLabel(info_frame, text=tag_text, font=("Roboto", 10), text_color="gray70").pack(anchor="w")

        # Status/Pass/Storage Info
        # Status/Pass/Storage Info
        # Robust storage display
        used_display = self.used if self.used and self.used != "?" else "N/A"
        free_display = self.free if self.free and self.free != "?" else "N/A"
        
        details = f"Pass: {self.password} | St: {self.status} | Used: {used_display}  Free: {free_display}"
        ctk.CTkLabel(self, text=details, font=("Roboto", 11), text_color="gray60", anchor="w").grid(row=1, column=0, padx=15, pady=(0, 5), sticky="w")
        
        # Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=2, padx=10)

        self._make_btn(btn_frame, "Copy Email", self.copy_email, COLOR_SECONDARY, width=70)
        self._make_btn(btn_frame, "Copy Pass", self.copy_pass, COLOR_SECONDARY, width=70)
        self._make_btn(btn_frame, "Edit", self.edit_pass, "gray40", width=50)
        self._make_btn(btn_frame, "Tags", self.edit_tags, "gray40", width=50)
        
        # Disable/Enable Toggle
        if self.status == "Disabled":
            self._make_btn(btn_frame, "Enable", self.toggle_status, COLOR_PRIMARY, width=60)
        else:
            self._make_btn(btn_frame, "Disable", self.toggle_status, COLOR_DANGER, width=60)

    def _make_btn(self, parent, text, cmd, col, width=80):
        ctk.CTkButton(parent, text=text, command=cmd, fg_color=col, width=width, height=24, font=("Roboto", 11)).pack(side="left", padx=2)

    def copy_email(self):
        self.clipboard_clear()
        self.clipboard_append(self.email)

    def copy_pass(self):
        self.clipboard_clear()
        self.clipboard_append(self.password)

    def edit_pass(self):
        EditPasswordDialog(self.winfo_toplevel(), self.password, self._on_pass_change)

    def edit_tags(self):
        TagEditDialog(self.winfo_toplevel(), self.email, self.reload_cb)

    def _on_pass_change(self, new_pass):
        if new_pass:
            self._update_cell(1, new_pass)
            self.reload_cb()

    def toggle_status(self):
        new_status = "Unknown" if self.status == "Disabled" else "Disabled"
        self._update_cell(4, new_status)
        self.reload_cb()

    def _update_cell(self, col_index, new_value):
        try:
             csv_utils.update_account(self.email, col_index, new_value)
        except Exception as e:
            print(f"Error updating CSV: {e}")

class EditPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_pass, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Edit Password")
        self.geometry("300x150")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Center relative to parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x_pos = parent_x + (parent_width // 2) - (300 // 2)
        y_pos = parent_y + (parent_height // 2) - (150 // 2)
        self.geometry(f"300x150+{x_pos}+{y_pos}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Enter new password:", font=("Roboto", 13)).pack(pady=(20, 10))
        
        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.insert(0, current_pass)
        self.entry.pack(pady=5)
        self.entry.focus()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", width=80, command=self.destroy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save", fg_color=COLOR_PRIMARY, width=80, command=self.save).pack(side="left", padx=5)
        
        # Allow Enter key to save
        self.bind("<Return>", lambda event: self.save())

    def save(self):
        new_pass = self.entry.get()
        if new_pass:
            self.callback(new_pass)
        self.destroy()

# --- Helper ---
class ProgressWrapper:
    def __init__(self, callback, total, controller=None):
        self.callback = callback
        self.total = total
        self.current = 0
        self.controller = controller

    def update(self, n=1):
        self.current += n
        val = self.current / self.total if self.total > 0 else 0
        if self.controller:
            self.controller.after(0, lambda v=val: self.callback(v))
        else:
            self.callback(val)

# --- Export Dialog ---
class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Export Accounts")
        self.geometry("400x300")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        #Center
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x_pos = parent_x + (parent_width // 2) - (400 // 2)
        y_pos = parent_y + (parent_height // 2) - (300 // 2)
        self.geometry(f"400x300+{x_pos}+{y_pos}")
        
        # Content
        ctk.CTkLabel(self, text="Select Export Format", font=FONT_HEADER).pack(pady=(30, 20))
        
        self.format_var = ctk.StringVar(value="json")
        
        ctk.CTkRadioButton(self, text="JSON (Lightweight, Human-readable)", 
                          variable=self.format_var, value="json").pack(pady=10)
        ctk.CTkRadioButton(self, text="Excel (Formatted, Spreadsheet)", 
                          variable=self.format_var, value="excel").pack(pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", width=100, 
                     command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Export", fg_color=COLOR_PRIMARY, width=100, 
                     command=self.export_accounts).pack(side="left", padx=10)
    
    def export_accounts(self):
        from tkinter import filedialog, messagebox
        
        format_type = self.format_var.get()
        
        # File dialog
        if format_type == "json":
            filetypes = [("JSON files", "*.json")]
            default_ext = ".json"
        else:
            filetypes = [("Excel files", "*.xlsx")]
            default_ext = ".xlsx"
        
        filepath = filedialog.asksaveasfilename(
            title="Export Accounts",
            filetypes=filetypes,
            defaultextension=default_ext
        )
        
        if not filepath:
            return
        
        try:
            rows = csv_utils.read_accounts()
            
            # Export
            if format_type == "json":
                count = export_utils.export_to_json(rows, filepath)
            else:
                count = export_utils.export_to_excel(rows, filepath)
            
            messagebox.showinfo("Success", f"Exported {count} accounts to {format_type.upper()}")
            self.destroy()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messagebox.showerror("Export Error", f"Failed to export:\n\n{str(e)}\n\nDetails:\n{error_details}")

# --- Tag Edit Dialog ---
class TagEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, email, reload_cb):
        super().__init__(parent)
        self.email = email
        self.reload_cb = reload_cb
        self.title(f"Edit Tags - {email}")
        self.geometry("400x350")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Center
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x_pos = parent_x + (parent_width // 2) - (400 // 2)
        y_pos = parent_y + (parent_height // 2) - (350 // 2)
        self.geometry(f"400x350+{x_pos}+{y_pos}")
        
        # Get current tags
        self.current_tags = tag_manager.TagManager.get_account_tags(email)
        
        # UI
        ctk.CTkLabel(self, text="Account Tags", font=FONT_HEADER).pack(pady=(20, 10))
        
        # Current tags display
        self.tags_frame = ctk.CTkScrollableFrame(self, height=150)
        self.tags_frame.pack(fill="x", padx=20, pady=10)
        self.refresh_tags_display()
        
        # Add new tag
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        self.tag_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter new tag...")
        self.tag_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.tag_entry.bind("<Return>", lambda e: self.add_tag())
        
        ctk.CTkButton(input_frame, text="Add", width=60, command=self.add_tag,
                     fg_color=COLOR_PRIMARY).pack(side="left")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Done", width=100, command=self.on_done,
                     fg_color=COLOR_PRIMARY).pack(side="left", padx=5)
    
    def refresh_tags_display(self):
        for w in self.tags_frame.winfo_children():
            w.destroy()
        
        if not self.current_tags:
            ctk.CTkLabel(self.tags_frame, text="No tags yet", 
                        text_color=COLOR_TEXT_SUB).pack(pady=10)
            return
        
        for tag in self.current_tags:
            tag_row = ctk.CTkFrame(self.tags_frame, fg_color="#333333")
            tag_row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(tag_row, text=f"🏷️ {tag}", font=("Roboto", 12),
                        text_color="white").pack(side="left", padx=10, pady=5)
            
            ctk.CTkButton(tag_row, text="✖", width=30, height=25,
                         command=lambda t=tag: self.remove_tag(t),
                         fg_color=COLOR_DANGER, hover_color="#C62828").pack(side="right", padx=5)
    
    def add_tag(self):
        tag = self.tag_entry.get().strip()
        if tag and tag not in self.current_tags:
            self.current_tags.append(tag)
            tag_manager.TagManager.set_account_tags(self.email, self.current_tags)
            self.tag_entry.delete(0, 'end')
            self.refresh_tags_display()
    
    def remove_tag(self, tag):
        if tag in self.current_tags:
            self.current_tags.remove(tag)
            tag_manager.TagManager.set_account_tags(self.email, self.current_tags)
            self.refresh_tags_display()
    
    def on_done(self):
        self.reload_cb()
        self.destroy()

if __name__ == "__main__":
    app = MegaGenGUI()
    app.mainloop()
