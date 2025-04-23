# --- START OF FILE XS PDF ASSISTANT.py ---

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from tkinter import font as tkFont
import os
import sys
import subprocess

# --- Conditional Import for PDF ---
try:
    from pypdf import PdfReader, PdfWriter
    PDF_LIB_AVAILABLE = True
    PYPDF_VERSION = getattr(__import__("pypdf"), "__version__", "unknown")
    print(f"Info: Using pypdf library version {PYPDF_VERSION}.")
except ImportError:
    PDF_LIB_AVAILABLE = False

# --- Icon Constant (Relative Path) ---
ICON_FILE_ICO = "oonfg-z0zg7-001.ico"

class PdfSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XS PDF ASSISTANT")
        self.root.geometry("600x630") # Keep height for status bar

        # --- Add Application Icon ---
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, ICON_FILE_ICO)
            if sys.platform == "win32" and os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path); print(f"Info: Icône chargée : {icon_path}")
            elif not os.path.exists(icon_path): print(f"Avertissement: Icône non trouvée.")
        except Exception as e: print(f"Erreur chargement icône : {e}")
        # --- End Icon ---

        self.style = ttk.Style()
        theme_used = 'clam'
        available_themes = self.style.theme_names()
        if 'clam' in available_themes: self.style.theme_use('clam'); theme_used = 'clam'
        elif 'vista' in available_themes and sys.platform == "win32": self.style.theme_use('vista'); theme_used = 'vista'
        elif 'aqua' in available_themes and sys.platform == "darwin": self.style.theme_use('aqua'); theme_used = 'aqua'
        print(f"Info: Thème ttk utilisé: {theme_used}")

        self.pdf_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.move_state = {'active': False, 'part_id': None, 'part_text': ""}

        self.initialiser_interface_pdf()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        if not PDF_LIB_AVAILABLE:
            messagebox.showerror("Erreur Dépendance", "Module 'pypdf' manquant.\nInstaller avec: pip install pypdf\nApplication arrêtée.", parent=self.root)
            self.root.quit()

    def initialiser_interface_pdf(self):
        # Fonts
        self.bold_font = tkFont.Font(family="Arial", size=10, weight="bold")
        self.normal_font = tkFont.Font(family="Arial", size=10)
        self.save_button_font = tkFont.Font(family="Arial", size=9)
        self.status_font = tkFont.Font(family="Arial", size=9, weight="bold")
        self.arrow_button_font = tkFont.Font(family="Arial", size=10) # Font for arrow buttons

        # Styles
        self.style.configure("Bold.TLabel", font=self.bold_font)
        self.style.map("Treeview", background=[('selected', '#007bff')], foreground=[('selected', 'white')])
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Save.TButton", font=self.save_button_font, padding=(1, 0))
        self.style.configure("Status.TLabel", font=self.status_font, foreground="blue", padding=(5, 2))
        self.style.configure("Confirm.TButton", foreground="green")
        self.style.configure("Arrow.TButton", font=self.arrow_button_font, padding=(2, 0)) # Style for arrow buttons


        # --- Widget Layout ---
        # Source/Destination Frames (Unchanged)
        frame_source = ttk.LabelFrame(self.root, text="Fichier source")
        frame_source.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        ttk.Label(frame_source, text="PDF source :", style="Bold.TLabel").pack(anchor='w', padx=5, pady=2)
        entry_frame = ttk.Frame(frame_source); entry_frame.pack(fill="x", padx=5, pady=2)
        ttk.Entry(entry_frame, textvariable=self.pdf_path_var).pack(side=tk.LEFT, fill="x", expand=True, padx=(0,5))
        ttk.Button(entry_frame, text="📂", command=self.choisir_fichier_pdf, width=3).pack(side=tk.LEFT)

        frame_dest = ttk.LabelFrame(self.root, text="Dossier de destination")
        frame_dest.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        ttk.Label(frame_dest, text="Dossier :", style="Bold.TLabel").pack(anchor='w', padx=5, pady=2)
        dest_frame = ttk.Frame(frame_dest); dest_frame.pack(fill="x", padx=5, pady=2)
        ttk.Entry(dest_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill="x", expand=True, padx=(0,5))
        ttk.Button(dest_frame, text="📁", command=self.choisir_dossier_sortie, width=3).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(dest_frame, text="↗️", command=self.ouvrir_dossier_destination, width=3).pack(side=tk.LEFT)

        # Status Bar
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side=tk.TOP, fill="x", padx=10, pady=(5, 0))

        # Bottom Area (Footer, Launch Button) (Unchanged)
        footer_frame = ttk.Frame(self.root); footer_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=(5, 5))
        ttk.Label(footer_frame, text="XS PDF ASSISTANT - Learnpls ©", foreground="gray").pack()
        self.launch_btn = tk.Button(self.root, text="🚀 Lancer Traitement", command=self.lancer_traitement, bg="#00C853", fg="white", activebackground="#00A040", activeforeground="white", font=(tkFont.nametofont("TkDefaultFont").actual()["family"], 12, "bold"), relief=tk.RAISED, borderwidth=2, padx=10, pady=5)
        self.launch_btn.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)

        # --- Action Buttons Frame ---
        self.frame_btns = ttk.Frame(self.root)
        self.frame_btns.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)

        # Add/Duplicate/Move Btns
        self.add_group_button = ttk.Button(self.frame_btns, text="➕ Groupe", command=self.ajouter_groupe); self.add_group_button.pack(side=tk.LEFT, padx=2)
        self.add_part_button = ttk.Button(self.frame_btns, text="➕ Partie", command=self.ajouter_partie); self.add_part_button.pack(side=tk.LEFT, padx=2)
        self.duplicate_button = ttk.Button(self.frame_btns, text="➕ Dupliquer", command=self.dupliquer_selection); self.duplicate_button.pack(side=tk.LEFT, padx=2)
        self.move_button = ttk.Button(self.frame_btns, text="➡️ Déplacer Partie", command=self.toggle_move_part_mode); self.move_button.pack(side=tk.LEFT, padx=2)

        # --- UP/DOWN Buttons ---
        self.up_button = ttk.Button(self.frame_btns, text="↑", command=self.move_part_up, width=3, style="Arrow.TButton", state=tk.DISABLED)
        self.up_button.pack(side=tk.LEFT, padx=(10, 2)) # Add padding before
        self.down_button = ttk.Button(self.frame_btns, text="↓", command=self.move_part_down, width=3, style="Arrow.TButton", state=tk.DISABLED)
        self.down_button.pack(side=tk.LEFT, padx=2)

        # Delete/Reset Btns
        self.delete_button = ttk.Button(self.frame_btns, text="❌ Supprimer", command=self.supprimer_selection); self.delete_button.pack(side=tk.LEFT, padx=(10, 2)) # Add padding before
        self.reset_button = ttk.Button(self.frame_btns, text="🧹 Réinitialiser", command=self.tout_supprimer_pdf); self.reset_button.pack(side=tk.LEFT, padx=2)

        # Group buttons for disabling during move mode (incl. Up/Down)
        self.action_buttons_to_disable = [
            self.add_group_button, self.add_part_button, self.duplicate_button,
            self.up_button, self.down_button, # Add up/down buttons here
            self.delete_button, self.reset_button, self.launch_btn
        ]

        # Treeview Frame (Unchanged)
        frame_table = ttk.LabelFrame(self.root, text="Groupes et Parties (Dbl-clic Nom | Simple-clic Page pour éditer)")
        frame_table.pack(side=tk.TOP, fill="both", expand=True, padx=10, pady=10)
        self.table_pdf = ttk.Treeview(frame_table, columns=("Debut", "Fin"), show='tree headings')
        self.table_pdf.heading("#0", text="Nom Groupe / Partie", anchor=tk.W); self.table_pdf.column("#0", width=250, stretch=True, anchor=tk.W)
        self.table_pdf.heading("Debut", text="Page Début", anchor=tk.CENTER); self.table_pdf.column("Debut", width=80, stretch=False, anchor=tk.CENTER)
        self.table_pdf.heading("Fin", text="Page Fin", anchor=tk.CENTER); self.table_pdf.column("Fin", width=80, stretch=False, anchor=tk.CENTER)
        self.table_pdf.tag_configure('group', font=self.bold_font); self.table_pdf.tag_configure('part', font=self.normal_font)
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.table_pdf.yview); self.table_pdf.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.table_pdf.pack(side="left", fill="both", expand=True)

        # --- Event Bindings ---
        self.table_pdf.bind("<Double-Button-1>", self._handle_double_click)
        self.table_pdf.bind("<Button-1>", self._handle_single_click)
        # Bind selection change to update button states
        self.table_pdf.bind("<<TreeviewSelect>>", self._update_move_button_states)


    # === START OF ALL METHODS ===

    # --- Methods like _commit_pending_edit, _on_closing, file/dir choosers, item adders, duplicate, delete, reset, ---
    # --- _close_active_editors, _initiate_edit, lancer_traitement, _handle_single_click, _handle_double_click ---
    # --- toggle_move_part_mode, _update_ui_for_move_mode, _cancel_move_mode ---
    # (Keep these largely the same as the previous version with the move-to-group logic)
    # ... (Paste the existing methods here) ...
    def _commit_pending_edit(self):
        active_editor = None
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Entry, tk.Spinbox)) and hasattr(widget, '_edit_cell_info'):
                active_editor = widget; break
        if active_editor and active_editor.winfo_exists():
            print("Committing pending edit...")
            active_editor.event_generate("<FocusOut>"); self.root.update_idletasks()
            if active_editor.winfo_exists():
                print("Commit failed: Editor still exists (validation error?).")
                active_editor.focus_force(); return 'validation_failed'
            else: print("Commit successful: Editor closed."); return 'ok'
        return 'ok'

    def _on_closing(self):
        if self.move_state['active']: self._cancel_move_mode()
        commit_result = self._commit_pending_edit()
        if commit_result == 'ok': self.root.destroy()
        elif commit_result == 'validation_failed':
            messagebox.showwarning("Édition en Cours", "Veuillez corriger ou annuler l'édition avant de fermer.", parent=self.root)

    def choisir_fichier_pdf(self):
        if self.move_state['active']: self._cancel_move_mode()
        if self._commit_pending_edit() != 'ok': return
        path = filedialog.askopenfilename(title="Sélectionner PDF source", filetypes=[("PDF", "*.pdf"), ("Tous", "*.*")], parent=self.root)
        if path:
            self.pdf_path_var.set(os.path.normpath(path))
            if not self.output_dir_var.get(): self.output_dir_var.set(os.path.join(os.path.dirname(path), "Output_SplitMerge"))

    def choisir_dossier_sortie(self):
        if self.move_state['active']: self._cancel_move_mode()
        if self._commit_pending_edit() != 'ok': return
        path = filedialog.askdirectory(title="Sélectionner dossier destination", parent=self.root)
        if path: self.output_dir_var.set(os.path.normpath(path))

    def ouvrir_dossier_destination(self):
        if self.move_state['active']: self._cancel_move_mode()
        if self._commit_pending_edit() != 'ok': return
        path = self.output_dir_var.get()
        if not path: messagebox.showwarning("Chemin Manquant", "Dossier destination non défini.", parent=self.root); return
        norm_path = os.path.normpath(path)
        if not os.path.isdir(norm_path): messagebox.showerror("Erreur", f"Dossier inexistant:\n{norm_path}", parent=self.root); return
        try:
            if sys.platform == "win32": os.startfile(norm_path)
            elif sys.platform == "darwin": subprocess.call(["open", norm_path])
            else: subprocess.call(["xdg-open", norm_path])
        except Exception as e: messagebox.showerror("Erreur d'Ouverture", f"Impossible d’ouvrir '{norm_path}':\n{e}", parent=self.root)

    def _get_next_item_name(self, base_name="Item", parent='', suffix=""):
        i = 1; existing_items = self.table_pdf.get_children(parent)
        existing_texts = [self.table_pdf.item(child, 'text') for child in existing_items]
        is_group_level = (parent == ''); target_suffix = ".pdf" if is_group_level else ""
        base_name_no_suffix = base_name[:-4] if is_group_level and base_name.lower().endswith(".pdf") else base_name
        while True:
            potential_base = f"{base_name_no_suffix}_{suffix}_{i}" if suffix else f"{base_name_no_suffix}_{i}"
            potential_name = potential_base + target_suffix
            if potential_name not in existing_texts:
                 if not is_group_level and potential_base not in existing_texts: return potential_base
                 elif is_group_level: return potential_name
            i += 1

    def ajouter_groupe(self):
        if self._commit_pending_edit() != 'ok': return
        base_group_name = self._get_next_item_name("Groupe", parent='')
        group_id = self.table_pdf.insert('', 'end', text=base_group_name, values=("-", "-"), tags=('group',))
        self.ajouter_partie(parent_id=group_id)
        self._update_move_button_states() # Update buttons after adding potentially selectable item

    def ajouter_partie(self, parent_id=None):
        if self._commit_pending_edit() != 'ok': return
        original_parent_id = parent_id # Store original request
        if not parent_id:
            selected_items = self.table_pdf.selection()
            if not selected_items: messagebox.showwarning("Sélection Requise", "Sélectionnez un groupe où ajouter la partie.", parent=self.root); return
            item_id = selected_items[0]; tags = self.table_pdf.item(item_id, 'tags')
            if 'group' in tags: parent_id = item_id
            elif 'part' in tags: parent_id = self.table_pdf.parent(item_id)
            if not parent_id: messagebox.showerror("Erreur Interne", "Impossible de déterminer le groupe parent.", parent=self.root); return
            if not self.table_pdf.exists(parent_id) or 'group' not in self.table_pdf.item(parent_id, 'tags'): messagebox.showwarning("Sélection Invalide", "Sélectionnez un groupe ou une partie existante.", parent=self.root); return
        if not self.table_pdf.exists(parent_id): print(f"Erreur: Parent {parent_id} inexistant"); return
        part_name = self._get_next_item_name("Partie", parent=parent_id)
        part_id = self.table_pdf.insert(parent_id, 'end', text=part_name, values=("1", "1"), tags=('part',))
        self.table_pdf.item(parent_id, open=True)
        try:
            # Select the newly added part only if a group wasn't explicitly passed
            # (prevents selection jumping if called from ajouter_groupe)
            if not original_parent_id:
                self.table_pdf.selection_set(part_id)
                self.table_pdf.focus(part_id)
            self.table_pdf.see(part_id)
        except tk.TclError: pass
        self._update_move_button_states() # Update buttons after adding potentially selectable item

    def dupliquer_selection(self):
        if self._commit_pending_edit() != 'ok': return
        selected_items = self.table_pdf.selection()
        if not selected_items: messagebox.showwarning("Sélection Requise", "Sélectionnez un groupe ou une partie à dupliquer.", parent=self.root); return
        if len(selected_items) > 1: messagebox.showwarning("Sélection Multiple", "Veuillez sélectionner un seul élément.", parent=self.root); return
        item_id = selected_items[0]
        if not self.table_pdf.exists(item_id): return
        item_info = self.table_pdf.item(item_id); item_tags = item_info['tags']; item_text = item_info['text']
        try:
            newly_selected_id = None
            if 'group' in item_tags:
                new_group_name = self._get_next_item_name(item_text, parent='', suffix="Copie")
                new_group_id = self.table_pdf.insert('', 'end', text=new_group_name, values=("-", "-"), tags=('group',))
                newly_selected_id = new_group_id
                original_parts = self.table_pdf.get_children(item_id)
                for part_id in original_parts:
                    if not self.table_pdf.exists(part_id): continue
                    part_info = self.table_pdf.item(part_id); part_text = part_info['text']; part_values = part_info['values']
                    new_part_name = self._get_next_item_name(part_text, parent=new_group_id, suffix="Copie")
                    self.table_pdf.insert(new_group_id, 'end', text=new_part_name, values=part_values, tags=('part',))
                self.table_pdf.item(new_group_id, open=True)
            elif 'part' in item_tags:
                parent_id = self.table_pdf.parent(item_id)
                if not parent_id or not self.table_pdf.exists(parent_id): messagebox.showerror("Erreur", "Impossible de trouver le groupe parent.", parent=self.root); return
                item_values = item_info['values']
                new_part_name = self._get_next_item_name(item_text, parent=parent_id, suffix="Copie")
                new_part_id = self.table_pdf.insert(parent_id, 'end', text=new_part_name, values=item_values, tags=('part',))
                newly_selected_id = new_part_id
                self.table_pdf.item(parent_id, open=True)
            else: messagebox.showwarning("Type Inconnu", "Type d'élément non reconnu.", parent=self.root)

            if newly_selected_id:
                self.table_pdf.selection_set(newly_selected_id)
                self.table_pdf.focus(newly_selected_id)
                self.table_pdf.see(newly_selected_id)

        except Exception as e: messagebox.showerror("Erreur Duplication", f"Erreur: {e}", parent=self.root); print(f"Erreur Duplication: {e}")
        self._update_move_button_states() # Update buttons after selection potentially changes

    def supprimer_selection(self):
        if self._commit_pending_edit() != 'ok': return
        selected_items = self.table_pdf.selection()
        if not selected_items: messagebox.showwarning("Sélection Requise", "Sélectionner élément(s) à supprimer.", parent=self.root); return
        item_names = [f"'{self.table_pdf.item(item_id, 'text')}'" for item_id in selected_items if self.table_pdf.exists(item_id)]
        if not item_names: return
        if messagebox.askyesno("Confirmation", f"Supprimer {len(item_names)} élément(s) ?\n({', '.join(item_names)})", parent=self.root):
            # Store parent of first deleted part to potentially re-select later if sensible
            parent_to_focus = None
            if len(selected_items) == 1:
                 item_id = selected_items[0]
                 if self.table_pdf.exists(item_id) and 'part' in self.table_pdf.item(item_id,'tags'):
                     parent_to_focus = self.table_pdf.parent(item_id)

            self.table_pdf.selection_set([]) # Deselect first
            for item in reversed(selected_items):
                if self.table_pdf.exists(item): self.table_pdf.delete(item)

            # Try to focus the parent if a single part was deleted
            if parent_to_focus and self.table_pdf.exists(parent_to_focus):
                try:
                    self.table_pdf.focus(parent_to_focus)
                    self.table_pdf.selection_set(parent_to_focus)
                except tk.TclError: pass # Ignore if focus fails
            # Always update button state after deletion
            self._update_move_button_states()


    def tout_supprimer_pdf(self):
        if self._commit_pending_edit() != 'ok': return
        if not self.table_pdf.get_children(): messagebox.showinfo("Info", "Tableau vide.", parent=self.root); return
        if messagebox.askyesno("Confirmation", "Réinitialiser toute la configuration ?", parent=self.root):
            self.table_pdf.delete(*self.table_pdf.get_children())
            self.pdf_path_var.set(""); self.output_dir_var.set("")
            self._update_move_button_states() # Update buttons after clearing

    def _close_active_editors(self, exclude_cell=None):
         widgets_to_destroy = []
         for w in self.root.winfo_children():
              if isinstance(w, (ttk.Entry, tk.Spinbox)) and hasattr(w, '_edit_cell_info'):
                   cell_info = w._edit_cell_info
                   if exclude_cell and cell_info == exclude_cell: continue
                   widgets_to_destroy.append(w)
                   for btn in self.root.winfo_children():
                        if isinstance(btn, ttk.Button) and hasattr(btn, '_edit_cell_info') and btn._edit_cell_info == cell_info:
                             widgets_to_destroy.append(btn); break
         closed_count = 0
         for widget in widgets_to_destroy:
              if widget.winfo_exists(): widget.destroy(); closed_count += 1

    def _initiate_edit(self, item_id, column_id):
        if self._commit_pending_edit() != 'ok': return
        self._close_active_editors(exclude_cell=(item_id, column_id))
        is_editing_this = any(hasattr(w, '_edit_cell_info') and w._edit_cell_info == (item_id, column_id) for w in self.root.winfo_children())
        if is_editing_this: return
        if not self.table_pdf.exists(item_id): print(f"Warning: Edit non-existent item {item_id}"); return
        try: x, y, width, height = self.table_pdf.bbox(item_id, column_id)
        except tk.TclError: print(f"Warning: bbox fail {item_id}/{column_id}"); return
        if not width or not height: print(f"Warning: Zero bbox {item_id}/{column_id}"); return
        is_group = 'group' in self.table_pdf.item(item_id, 'tags'); is_part = 'part' in self.table_pdf.item(item_id, 'tags')
        value = ""
        if column_id == '#0': value = self.table_pdf.item(item_id, 'text')
        elif is_part and column_id in ['#1', '#2']:
             values_index = int(column_id.replace('#','')) - 1
             try: current_values = self.table_pdf.item(item_id, 'values'); value = current_values[values_index] if len(current_values) > values_index else "1"
             except Exception as e: print(f"Erreur valeur édit: {e}"); return
        else: return
        entry_var = tk.StringVar(value=str(value)); editor = None; save_button = None
        if is_part and column_id in ['#1', '#2']:
            max_page = 9999; pdf_path = self.pdf_path_var.get()
            if pdf_path and os.path.exists(pdf_path) and PDF_LIB_AVAILABLE:
                try: max_page = len(PdfReader(pdf_path).pages)
                except Exception as e: print(f"Avertissement: Lire nb pages échec: {e}")
            editor = tk.Spinbox(self.root, from_=1, to=max(1, max_page), textvariable=entry_var, wrap=False, width=7)
        else: editor = ttk.Entry(self.root, textvariable=entry_var)
        editor._edit_cell_info = (item_id, column_id)
        abs_x = self.table_pdf.winfo_rootx() + x; abs_y = self.table_pdf.winfo_rooty() + y
        root_x = abs_x - self.root.winfo_rootx(); root_y = abs_y - self.root.winfo_rooty()
        editor.place(x=root_x, y=root_y, width=width, height=height, anchor='nw'); editor.focus_force()
        save_button = ttk.Button(self.root, text="✓", width=2, style="Save.TButton")
        save_button._edit_cell_info = (item_id, column_id)
        save_button.place(x=root_x + width + 1, y=root_y, height=height, anchor='nw')
        editor._save_button = save_button
        if isinstance(editor, ttk.Entry): editor.select_range(0, 'end')
        elif isinstance(editor, tk.Spinbox):
             try: editor.selection('range', '0', 'end')
             except tk.TclError: pass
        def save_edit(event=None, cancel=False):
            current_editor = editor; current_save_button = save_button
            if not current_editor.winfo_exists() or not hasattr(current_editor, '_edit_cell_info') or current_editor._edit_cell_info != (item_id, column_id):
                 if current_save_button and current_save_button.winfo_exists(): current_save_button.destroy(); return
            if not self.table_pdf.exists(item_id):
                 if current_editor.winfo_exists(): current_editor.destroy()
                 if current_save_button and current_save_button.winfo_exists(): current_save_button.destroy(); return
            validation_passed = True
            if not cancel:
                try:
                    new_value_str = entry_var.get().strip()
                    if not new_value_str and column_id != '#0': messagebox.showerror("Erreur", "La valeur ne peut pas être vide.", parent=self.root); validation_passed = False
                    elif column_id == '#0':
                        invalid_chars = '/\\:*?"<>|'; name_to_check = new_value_str; is_group_edit = 'group' in self.table_pdf.item(item_id, 'tags')
                        name_to_check_base = name_to_check[:-4].strip() if is_group_edit and name_to_check.lower().endswith('.pdf') else name_to_check
                        if not name_to_check_base: messagebox.showerror("Erreur Nom", "Le nom ne peut pas être vide.", parent=self.root); validation_passed = False
                        elif any(char in name_to_check_base for char in invalid_chars) or name_to_check_base in ['.', '..']: messagebox.showerror("Erreur Nom", f"Nom invalide.", parent=self.root); validation_passed = False
                        elif len(name_to_check_base) > 200: messagebox.showerror("Erreur Nom", "Nom trop long.", parent=self.root); validation_passed = False
                        if validation_passed:
                            final_name = new_value_str; final_name += ".pdf" if is_group_edit and not final_name.lower().endswith('.pdf') else ""
                            self.table_pdf.item(item_id, text=final_name)
                    elif is_part and column_id in ['#1', '#2']:
                        values_index = int(column_id.replace('#','')) - 1
                        try:
                            page_num = int(new_value_str);
                            if page_num <= 0: raise ValueError("Page > 0.")
                            current_values_str = self.table_pdf.item(item_id, "values"); current_values_int = [0, 0]
                            try: current_values_int[0] = int(current_values_str[0])
                            except: pass
                            try: current_values_int[1] = int(current_values_str[1])
                            except: pass
                            other_page_index = 1 - values_index; other_page_num = current_values_int[other_page_index]
                            if values_index == 0 and other_page_num > 0 and page_num > other_page_num: messagebox.showwarning("Validation", f"Début ({page_num}) > Fin ({other_page_num}).", parent=self.root)
                            elif values_index == 1 and other_page_num > 0 and page_num < other_page_num: messagebox.showwarning("Validation", f"Fin ({page_num}) < Début ({other_page_num}).", parent=self.root)
                            new_values = list(current_values_str);
                            while len(new_values) < 2: new_values.append("1")
                            new_values[values_index] = str(page_num)
                            self.table_pdf.item(item_id, values=tuple(new_values))
                        except ValueError as ve: messagebox.showerror("Erreur Page", f"{ve}", parent=self.root); validation_passed = False
                except Exception as e: print(f"Erreur sauvegarde: {e}"); messagebox.showerror("Erreur", f"Sauvegarde impossible: {e}", parent=self.root); validation_passed = False
            if validation_passed or cancel:
                 if current_editor.winfo_exists(): current_editor.destroy()
                 if current_save_button and current_save_button.winfo_exists(): current_save_button.destroy()
                 self.table_pdf.focus_set()
            else:
                 if current_editor.winfo_exists(): current_editor.focus_force()
        editor.bind("<FocusOut>", lambda e: save_edit(e, cancel=False))
        editor.bind("<Return>", lambda e: save_edit(e, cancel=False))
        editor.bind("<KP_Enter>", lambda e: save_edit(e, cancel=False))
        editor.bind("<Escape>", lambda e: save_edit(e, cancel=True))
        save_button.config(command=lambda: save_edit(cancel=False))

    def lancer_traitement(self):
        if self.move_state['active']: self._cancel_move_mode()
        if self._commit_pending_edit() != 'ok': return
        # --- rest of lancer_traitement method is unchanged ---
        pdf_path = self.pdf_path_var.get(); output_dir = self.output_dir_var.get(); groups = self.table_pdf.get_children('')
        if not pdf_path or not output_dir: messagebox.showerror("Erreur Config", "Spécifier PDF source ET dossier destination.", parent=self.root); return
        if not os.path.exists(pdf_path) or not os.path.isfile(pdf_path): messagebox.showerror("Erreur Source", f"Fichier PDF source invalide:\n{pdf_path}", parent=self.root); return
        if not os.path.isdir(output_dir):
            if messagebox.askyesno("Dossier Inexistant", f"Dossier destination '{os.path.basename(output_dir)}' inexistant.\nCréer ?", parent=self.root):
                try: os.makedirs(output_dir); print(f"Info: Dossier créé : {output_dir}")
                except Exception as e: messagebox.showerror("Erreur Création Dossier", f"Impossible de créer:\n{e}", parent=self.root); return
            else: return
        if not groups: messagebox.showwarning("Aucun Groupe", "Aucun groupe défini.", parent=self.root); return
        errors = []; success_count = 0; processed_groups = 0; reader = None
        self.launch_btn.config(state=tk.DISABLED, text="Traitement..."); self.root.update_idletasks()
        try:
            reader = PdfReader(pdf_path); total_pages_source = len(reader.pages)
            print(f"Info: PDF source '{os.path.basename(pdf_path)}' {total_pages_source} pages.")
            # Make sure to process parts in the order they appear in the treeview
            for group_id in groups:
                processed_groups += 1;
                if not self.table_pdf.exists(group_id): continue
                group_item = self.table_pdf.item(group_id); group_name_raw = group_item['text'].strip()
                if not group_name_raw: errors.append(f"Groupe #{processed_groups}: Nom manquant."); continue
                group_name_base = group_name_raw[:-4] if group_name_raw.lower().endswith('.pdf') else group_name_raw
                if not group_name_base: errors.append(f"Groupe '{group_name_raw}': Nom base vide."); continue
                invalid_chars = '/\\:*?"<>|'; safe_group_name_base = "".join(c if c not in invalid_chars and ord(c) > 31 else '_' for c in group_name_base).strip()
                if not safe_group_name_base or safe_group_name_base in ['.', '..']: errors.append(f"Groupe '{group_name_raw}': Nom fichier invalide."); continue
                group_filename = f"{safe_group_name_base}.pdf"; output_path = os.path.join(output_dir, group_filename)
                parts = self.table_pdf.get_children(group_id) # This gets children in their current display order
                if not parts: errors.append(f"Groupe '{group_filename}': Aucune partie."); continue
                group_writer = PdfWriter(); pages_added_this_group = 0; group_has_part_errors = False
                print(f"Info: Traitement Groupe '{group_filename}', Ordre des parties: {[self.table_pdf.item(p, 'text') for p in parts]}") # Log part order
                for part_idx, part_id in enumerate(parts): # Iterate in current order
                    if not self.table_pdf.exists(part_id): continue
                    part_item = self.table_pdf.item(part_id); part_name = part_item['text']; part_values_str = part_item['values']
                    try:
                        if len(part_values_str) < 2: raise ValueError("Données page incomplètes")
                        start = int(part_values_str[0]); end = int(part_values_str[1])
                        if not (0 < start <= end): raise ValueError(f"Plage invalide ({start}-{end})")
                        adjusted_start = start; adjusted_end = min(end, total_pages_source)
                        if adjusted_start > total_pages_source: print(f"Avert: Grp '{group_filename}', Part '{part_name}': Début ({start}) > Total ({total_pages_source}). Ignorée."); continue
                        part_pages_added = 0
                        for i in range(adjusted_start - 1, adjusted_end):
                            if 0 <= i < total_pages_source: group_writer.add_page(reader.pages[i]); part_pages_added += 1
                            else: print(f"Err Logique: Index page hors limites ({i}) part '{part_name}'")
                        if part_pages_added > 0: pages_added_this_group += part_pages_added
                        else: print(f"Avert: Aucune page ajoutée part '{part_name}' (demandée {start}-{end}, ajustée {adjusted_start}-{adjusted_end}).")
                    except (ValueError, IndexError, TypeError) as e_part:
                        part_name_err = part_name or f"Partie #{part_idx+1}"
                        errors.append(f"Grp '{group_filename}', Partie '{part_name_err}': Erreur données - {e_part}.")
                        group_has_part_errors = True
                    except Exception as e_generic_part:
                         part_name_err = part_name or f"Partie #{part_idx+1}"
                         errors.append(f"Grp '{group_filename}', Partie '{part_name_err}': Erreur - {e_generic_part}.")
                         group_has_part_errors = True
                if pages_added_this_group > 0:
                    if os.path.exists(output_path):
                        if not messagebox.askyesno("Fichier Existant", f"Remplacer '{group_filename}'?", parent=self.root, icon='warning'):
                            errors.append(f"Groupe '{group_filename}': Non remplacé."); continue
                    try:
                        with open(output_path, "wb") as f_out: group_writer.write(f_out)
                        success_count += 1; print(f"Info: Groupe '{group_filename}' créé ({pages_added_this_group} pages).")
                    except Exception as e_write: errors.append(f"Groupe '{group_filename}': Échec écriture - {e_write}")
                elif not group_has_part_errors: errors.append(f"Groupe '{group_filename}': Aucune page valide ajoutée.")
            if errors:
                error_details = "\n - ".join(errors); msg = f"Terminé.\n\n{success_count} fichier(s) créé(s).\n\nErreurs/Infos ({len(errors)}):\n - {error_details}"
                messagebox.showwarning("Résultat avec Erreurs/Infos", msg, parent=self.root)
            elif success_count > 0: messagebox.showinfo("Succès", f"Terminé ! ✅\n\n{success_count} fichier(s) créé(s) dans '{output_dir}'.", parent=self.root)
            else: messagebox.showinfo("Info", "Terminé, aucun fichier créé (vérifiez config/erreurs).", parent=self.root)
        except FileNotFoundError: messagebox.showerror("Erreur Source", f"Fichier PDF source introuvable:\n{pdf_path}", parent=self.root)
        except ImportError: messagebox.showerror("Erreur Librairie", "Erreur usage pypdf.", parent=self.root)
        except Exception as e_main: messagebox.showerror("Erreur Inattendue", f"Erreur majeure:\n{e_main}", parent=self.root); print(f"ERREUR MAJEURE: {e_main}")
        finally: self.launch_btn.config(state=tk.NORMAL, text="🚀 Lancer Traitement"); self.root.update_idletasks(); reader = None

    def _handle_single_click(self, event):
        if self.move_state['active']: self.status_var.set("Mode Déplacement Actif: Sélectionnez un groupe destination."); return
        if self._commit_pending_edit() != 'ok': return
        region = self.table_pdf.identify_region(event.x, event.y)
        if region == "heading": self._update_move_button_states(); return # Update state even on heading click
        item_id = self.table_pdf.identify_row(event.y); column_id = self.table_pdf.identify_column(event.x)
        if not item_id: self._close_active_editors(); self._update_move_button_states(); return
        self._close_active_editors(exclude_cell=(item_id, column_id))
        tags = self.table_pdf.item(item_id, 'tags')
        if 'part' in tags and column_id in ['#1', '#2']: self._initiate_edit(item_id, column_id)
        # No else needed, selection happens anyway, button state update is handled by <<TreeviewSelect>>

    def _handle_double_click(self, event):
        if self.move_state['active']: self.status_var.set("Mode Déplacement Actif: Sélectionnez un groupe destination."); return
        if self._commit_pending_edit() != 'ok': return
        self._close_active_editors()
        region = self.table_pdf.identify_region(event.x, event.y); item_id = self.table_pdf.identify_row(event.y); column_id = self.table_pdf.identify_column(event.x)
        if region == "heading" or not item_id : return
        if column_id == '#0': self._initiate_edit(item_id, column_id)

    def toggle_move_part_mode(self):
        if not self.move_state['active']:
            if self._commit_pending_edit() != 'ok': messagebox.showwarning("Édition en Cours", "Terminez l'édition avant de déplacer.", parent=self.root); return
            selected_items = self.table_pdf.selection()
            if not selected_items or len(selected_items) > 1: messagebox.showwarning("Sélection Requise", "Sélectionnez la partie unique à déplacer.", parent=self.root); return
            part_id = selected_items[0]
            if 'part' not in self.table_pdf.item(part_id, 'tags'): messagebox.showwarning("Sélection Invalide", "Seule une 'Partie' peut être déplacée.", parent=self.root); return
            self.move_state['active'] = True; self.move_state['part_id'] = part_id; self.move_state['part_text'] = self.table_pdf.item(part_id, 'text')
            self._update_ui_for_move_mode(True); self.status_var.set(f"Déplacer '{self.move_state['part_text']}': Sélectionnez le groupe destination et confirmez.")
        else:
            target_selection = self.table_pdf.selection()
            if not target_selection or len(target_selection) > 1: messagebox.showerror("Sélection Cible Manquante", "Sélectionnez un groupe destination avant de confirmer.", parent=self.root); return
            target_group_id = target_selection[0]; part_id_to_move = self.move_state['part_id']
            if not self.table_pdf.exists(target_group_id) or not self.table_pdf.exists(part_id_to_move): messagebox.showerror("Erreur", "La partie ou le groupe cible n'existe plus.", parent=self.root); self._cancel_move_mode(); return
            if 'group' not in self.table_pdf.item(target_group_id, 'tags'): messagebox.showerror("Sélection Cible Invalide", "La destination n'est pas un 'Groupe'.", parent=self.root); return
            original_parent_id = self.table_pdf.parent(part_id_to_move)
            if target_group_id == original_parent_id: messagebox.showinfo("Information", "La partie est déjà dans ce groupe.", parent=self.root); self._cancel_move_mode(); return
            try:
                self.table_pdf.move(part_id_to_move, target_group_id, 'end'); self.table_pdf.item(target_group_id, open=True); self.table_pdf.see(part_id_to_move)
                print(f"Info: Partie '{self.move_state['part_text']}' déplacée vers '{self.table_pdf.item(target_group_id, 'text')}'."); self._cancel_move_mode()
            except tk.TclError as e: messagebox.showerror("Erreur Déplacement", f"Impossible de déplacer:\n{e}", parent=self.root); self._cancel_move_mode()
            except Exception as e: messagebox.showerror("Erreur Inattendue", f"Erreur déplacement:\n{e}", parent=self.root); self._cancel_move_mode()

    def _update_ui_for_move_mode(self, is_active):
        if is_active: new_text = "✅ Confirmer Destination"; new_style = "Confirm.TButton"; button_state = tk.DISABLED
        else: new_text = "➡️ Déplacer Partie"; new_style = ""; button_state = tk.NORMAL
        self.move_button.config(text=new_text, style=new_style)
        for btn in self.action_buttons_to_disable:
            try:
                 if btn.winfo_exists(): btn.config(state=button_state)
            except: pass
        # Special handling for Up/Down buttons - they should ALSO be disabled in move mode
        if is_active:
             self.up_button.config(state=tk.DISABLED)
             self.down_button.config(state=tk.DISABLED)
        else:
             # When exiting move mode, re-evaluate Up/Down based on current selection
             self._update_move_button_states()


    def _cancel_move_mode(self):
        print("Debug: Cancelling move mode.")
        self.move_state = {'active': False, 'part_id': None, 'part_text': ""}
        self.status_var.set("")
        self._update_ui_for_move_mode(False) # Restores buttons including calling _update_move_button_states


    # --- New Methods for Moving Parts Up/Down ---

    def move_part_up(self):
        """Moves the selected part one position up within its group."""
        if self.move_state['active']: return # Ignore if moving between groups
        if self._commit_pending_edit() != 'ok': return

        selected_items = self.table_pdf.selection()
        if not selected_items or len(selected_items) > 1: return # Should be disabled anyway

        item_id = selected_items[0]
        if 'part' not in self.table_pdf.item(item_id, 'tags'): return # Should be disabled

        parent_id = self.table_pdf.parent(item_id)
        if not parent_id: return # Part without parent? Error.

        try:
            siblings = self.table_pdf.get_children(parent_id)
            current_index = siblings.index(item_id)

            if current_index > 0:
                self.table_pdf.move(item_id, parent_id, current_index - 1)
                # Keep selected and visible
                self.table_pdf.selection_set(item_id)
                self.table_pdf.focus(item_id)
                self.table_pdf.see(item_id)
                self._update_move_button_states() # Re-evaluate after move
        except ValueError:
            print(f"Erreur: item {item_id} non trouvé parmi les enfants de {parent_id}")
        except tk.TclError as e:
            print(f"Erreur Tcl move up: {e}")
            messagebox.showerror("Erreur Déplacement", f"Impossible de monter la partie:\n{e}", parent=self.root)

    def move_part_down(self):
        """Moves the selected part one position down within its group."""
        if self.move_state['active']: return # Ignore if moving between groups
        if self._commit_pending_edit() != 'ok': return

        selected_items = self.table_pdf.selection()
        if not selected_items or len(selected_items) > 1: return # Should be disabled anyway

        item_id = selected_items[0]
        if 'part' not in self.table_pdf.item(item_id, 'tags'): return # Should be disabled

        parent_id = self.table_pdf.parent(item_id)
        if not parent_id: return # Part without parent? Error.

        try:
            siblings = self.table_pdf.get_children(parent_id)
            current_index = siblings.index(item_id)

            if current_index < len(siblings) - 1:
                self.table_pdf.move(item_id, parent_id, current_index + 1)
                # Keep selected and visible
                self.table_pdf.selection_set(item_id)
                self.table_pdf.focus(item_id)
                self.table_pdf.see(item_id)
                self._update_move_button_states() # Re-evaluate after move
        except ValueError:
            print(f"Erreur: item {item_id} non trouvé parmi les enfants de {parent_id}")
        except tk.TclError as e:
            print(f"Erreur Tcl move down: {e}")
            messagebox.showerror("Erreur Déplacement", f"Impossible de descendre la partie:\n{e}", parent=self.root)


    def _update_move_button_states(self, event=None):
        """Updates the state of the Up/Down buttons based on selection."""
        # Always disable if move-to-group mode is active
        if self.move_state['active']:
            self.up_button.config(state=tk.DISABLED)
            self.down_button.config(state=tk.DISABLED)
            return

        selected_items = self.table_pdf.selection()

        can_move_up = False
        can_move_down = False

        if len(selected_items) == 1:
            item_id = selected_items[0]
            # Check if item still exists before proceeding
            if self.table_pdf.exists(item_id) and 'part' in self.table_pdf.item(item_id, 'tags'):
                parent_id = self.table_pdf.parent(item_id)
                if parent_id: # Check if part has a parent
                    try:
                        siblings = self.table_pdf.get_children(parent_id)
                        current_index = siblings.index(item_id)
                        if current_index > 0:
                            can_move_up = True
                        if current_index < len(siblings) - 1:
                            can_move_down = True
                    except ValueError:
                        # Item not found among siblings, should not happen if exists() is true
                        print(f"Avertissement: Item sélectionné {item_id} non trouvé parmi les enfants de {parent_id} lors de la mise à jour des boutons.")
                        pass # Keep buttons disabled

        self.up_button.config(state=tk.NORMAL if can_move_up else tk.DISABLED)
        self.down_button.config(state=tk.NORMAL if can_move_down else tk.DISABLED)

    # === END OF ALL METHODS ===

# --- Main execution block (if __name__ == "__main__":) remains the same ---
if __name__ == "__main__":
    if not PDF_LIB_AVAILABLE:
        try:
            root_err = tk.Tk(); root_err.withdraw()
            messagebox.showerror("Erreur Critique", "Module 'pypdf' manquant.\n\nInstaller: pip install pypdf\n\nApplication arrêtée.", title="Dépendance Manquante")
            root_err.destroy()
        except Exception as tk_err: print("ERREUR CRITIQUE: 'pypdf' manquant."); print(f"(Tkinter échec: {tk_err})")
        sys.exit(1)
    root = None
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="clam")
        available = root.get_themes(); preferred = ['clam', 'arc', 'plastik', 'vista', 'aqua', 'radiance']
        theme_to_use = next((t for t in preferred if t in available), None)
        if theme_to_use and theme_to_use != "clam": root.set_theme(theme_to_use); print(f"Info: Thème ttk: '{theme_to_use}'")
        elif "clam" in available: print(f"Info: Thème ttk 'clam'.")
        elif available: theme_to_use = available[0]; root.set_theme(theme_to_use); print(f"Info: Thème préféré non trouvé. Utilisation de '{theme_to_use}'.")
        else: root.destroy(); raise RuntimeError("Aucun thème ttk trouvé.")
    except (ImportError, RuntimeError, Exception) as e:
        print(f"Info: ttkthemes non dispo/erreur ({e}). Tkinter standard.")
        if root: root.destroy();
        root = tk.Tk()
    app = PdfSplitterApp(root)
    root.mainloop()
# --- END OF FILE XS PDF ASSISTANT.py ---