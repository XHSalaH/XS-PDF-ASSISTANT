# --- START OF FILE XS PDF ASSISTANT FL.py ---

# --- START OF FILE PDF SPLITTER.py ---

# --- START OF FILE pdf_splitter_app.py ---

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog # Keep simpledialog for cell edit fallback if needed
from tkinter import *
import os
import sys
import subprocess
import tempfile
import shutil
# No time needed anymore
# No pathlib needed anymore

# --- Conditional Import for PDF ---
try:
    from pypdf import PdfReader, PdfWriter
    PDF_LIB_AVAILABLE = True
    PYPDF_VERSION = getattr(__import__("pypdf"), "__version__", "unknown")
    print(f"Info: Using pypdf library version {PYPDF_VERSION}.")
except ImportError:
    PDF_LIB_AVAILABLE = False
    print("ERREUR: Le module 'pypdf' (version 3+ recommandée) est requis.")
    print("        Installez-le avec : pip install pypdf")

# --- Original Icon Constants ---
ICON_FILE_ICO = "C:/PDFTool/FECHIER FINAL/oonfg-z0zg7-001.ico" # Using forward slashes
ICON_FILE_PNG = "app_icon.png" # Or your preferred original icon

# --- !!! DEFINE YOUR IMAGE FILENAME HERE !!! ---
STATIC_IMAGE_FILE = "logo.png" # <-- CHANGE THIS to your image file

class PdfSplitterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XS PDF ASSISTANT ") # Original title
        self.root.geometry("750x730") # Adjusted height slightly (can maybe be smaller now)

        # --- Add Application Icon ---
        self._app_icon = None
        try:
            # *** IMPORTANT: Handle potential issue with hardcoded absolute path ***
            # If ICON_FILE_ICO is absolute, os.path.join(base_path, ICON_FILE_ICO) might not work as expected.
            # Let's check if ICON_FILE_ICO is absolute first.
            if os.path.isabs(ICON_FILE_ICO):
                icon_path_ico = ICON_FILE_ICO # Use the absolute path directly
            else:
                # If relative, join with base_path (useful for PyInstaller)
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                icon_path_ico = os.path.join(base_path, ICON_FILE_ICO)

            # Handle PNG icon (assuming it's relative or found via base_path)
            base_path_png = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path_png = os.path.join(base_path_png, ICON_FILE_PNG) # Use base_path for PNG too

            icon_to_load = None
            # Check existence of the potentially absolute ICO path
            if sys.platform == "win32" and os.path.exists(icon_path_ico):
                icon_to_load = icon_path_ico
                self.root.iconbitmap(default=icon_to_load)
            elif os.path.exists(icon_path_png):
                icon_to_load = icon_path_png
                self._app_icon = tk.PhotoImage(file=icon_to_load)
                self.root.iconphoto(True, self._app_icon)

            if icon_to_load: print(f"Info: Icône '{os.path.basename(icon_to_load)}' chargée.")
            else: print(f"Avertissement: Fichier icône non trouvé ({ICON_FILE_ICO} or {ICON_FILE_PNG}). Vérifiez les chemins.")
        except Exception as e: print(f"Erreur chargement icône: {e}")
        # --- End Icon ---

        self.style = ttk.Style()
        # REMOVED: self.create_backup_var = tk.BooleanVar(value=False)

        # --- Load Static Image ---
        self.static_image = None # Initialize attribute
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_path, STATIC_IMAGE_FILE)
            if os.path.exists(image_path):
                 self.static_image = tk.PhotoImage(file=image_path)
                 print(f"Info: Image statique '{STATIC_IMAGE_FILE}' chargée.")
            else:
                 print(f"Avertissement: Fichier image statique introuvable: {image_path}")
        except tk.TclError as img_err:
             print(f"Erreur chargement image statique (Tkinter TclError): {img_err}. Assurez-vous que le format est supporté (PNG/GIF).")
        except Exception as e:
             print(f"Erreur chargement image statique: {e}")
        # --- End Image Loading ---

        self.initialiser_interface_pdf()

        if not PDF_LIB_AVAILABLE:
             messagebox.showerror("Erreur de dépendance", "Module 'pypdf' (v3+) manquant.\nInstallez-le (`pip install pypdf`) et redémarrez.", parent=self.root)
             for widget in self.root.winfo_children():
                 self._disable_widgets_recursively(widget)

    def _disable_widgets_recursively(self, widget):
        """Recursively disable a widget and its children."""
        try: widget.configure(state=tk.DISABLED)
        except tk.TclError: pass
        for child in widget.winfo_children(): self._disable_widgets_recursively(child)

    def initialiser_interface_pdf(self):
        self.pdf_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.style.configure("Bold.TLabel", font=("Arial", 10, "bold"))
        self.style.configure("Group.Treeview", font=("Arial", 10, "bold"))

        # --- Main Content Frames (Source, Dest, Treeview, Buttons, Launch) ---
        # Source Frame
        frame_source = ttk.LabelFrame(self.root, text="Fichier source")
        frame_source.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_source, text="Fichier PDF source:", style="Bold.TLabel").pack(anchor='w', padx=5, pady=2)
        entry_frame = ttk.Frame(frame_source)
        # entry_frame.pack(fill="x", padx=5, pady=(2,0)) # Original padding if backup checkbox existed
        entry_frame.pack(fill="x", padx=5, pady=2) # Normal padding now
        ttk.Entry(entry_frame, textvariable=self.pdf_path_var).pack(side=tk.LEFT, fill="x", expand=True, padx=(0,5))
        ttk.Button(entry_frame, text="📂", command=self.choisir_fichier_pdf, width=3).pack(side=tk.LEFT)
        # REMOVED: backup_check = ttk.Checkbutton(...)
        # REMOVED: backup_check.pack(...)

        # Destination Frame
        frame_dest = ttk.LabelFrame(self.root, text="Destination")
        frame_dest.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_dest, text="Dossier de destination des fichiers groupés:", style="Bold.TLabel").pack(anchor='w', padx=5, pady=2)
        dest_frame = ttk.Frame(frame_dest); dest_frame.pack(fill="x", padx=5, pady=2)
        ttk.Entry(dest_frame, textvariable=self.output_dir_var).pack(side=tk.LEFT, fill="x", expand=True, padx=(0,5))
        ttk.Button(dest_frame, text="📁", command=self.choisir_dossier_sortie, width=3).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(dest_frame, text="↗️", command=self.ouvrir_dossier_destination, width=3).pack(side=tk.LEFT)

        # Treeview Frame for Groups and Parts
        frame_table = ttk.LabelFrame(self.root, text="Groupes et Parties (Simple-clic pour éditer)")
        frame_table.pack(fill="both", expand=True, padx=10, pady=10) # expand=True takes most space
        self.table_pdf = ttk.Treeview(frame_table, columns=("Nom", "Début", "Fin"), show='tree headings')
        self.table_pdf.heading("#0", text="Groupe / Partie", anchor=tk.W); self.table_pdf.column("#0", width=300, stretch=True, anchor=tk.W)
        self.table_pdf.heading("Nom", text="Nom Item"); self.table_pdf.column("Nom", width=0, stretch=False, anchor=tk.W)
        self.table_pdf.heading("Début", text="Page Début"); self.table_pdf.column("Début", width=80, stretch=False, anchor=tk.CENTER)
        self.table_pdf.heading("Fin", text="Page Fin"); self.table_pdf.column("Fin", width=80, stretch=False, anchor=tk.CENTER)
        self.table_pdf.tag_configure('group', font=('Arial', 10, 'bold')); self.table_pdf.tag_configure('part', font=('Arial', 10))
        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.table_pdf.yview); self.table_pdf.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.table_pdf.pack(fill="both", expand=True, padx=5, pady=5)
        self.table_pdf.bind("<Button-1>", self.modifier_cellule_pdf)

        # Buttons Frame
        frame_btns = ttk.Frame(self.root); frame_btns.pack(fill="x", padx=10, pady=5, side=tk.BOTTOM) # Pack at bottom
        ttk.Button(frame_btns, text="➕ Ajouter Groupe (Ctrl+G)", command=self.ajouter_groupe).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text="➕ Ajouter Partie (Ctrl+A)", command=self.ajouter_partie).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text="❌ Supprimer (Suppr)", command=self.supprimer_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_btns, text="🧹 Tout réinitialiser", command=self.tout_supprimer_pdf).pack(side=tk.LEFT, padx=5)

        # Launch Frame
        launch_frame = ttk.Frame(self.root); launch_frame.pack(fill="x", padx=10, pady=5, side=tk.BOTTOM) # Pack at bottom
        self.launch_btn = tk.Button(launch_frame, text="🚀 Lancer Découpage & Fusion (Ctrl+Entrée)", command=self.lancer_traitement, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief=tk.RAISED, borderwidth=2, padx=10, pady=5);
        self.launch_btn.pack(fill="x", pady=5)

        # --- Footer Area (Pack at bottom, above buttons/launch) ---
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=(5, 0)) # Pack at bottom

        # --- Display Static Image ---
        if self.static_image:
            image_label = ttk.Label(footer_frame, image=self.static_image)
            image_label.pack(pady=(0, 5))
        # --- End Image Display ---

        # Footer Text Label
        ttk.Label(footer_frame, text="XS PDF ASSISTANT - Réalisé par Learnpls ©", foreground="gray").pack(pady=(0, 5))

        # Bind shortcuts (can be done once)
        self.root.bind_all("<Control-g>", self.ajouter_groupe_shortcut, add='+'); self.root.bind_all("<Control-a>", self.ajouter_partie_shortcut, add='+'); self.root.bind_all("<Control-Return>", self.lancer_traitement_shortcut, add='+'); self.root.bind_all("<Delete>", self.supprimer_selection_shortcut, add='+')

    # --- Shortcut Handlers (Keep as before) ---
    def ajouter_groupe_shortcut(self, event=None): self.ajouter_groupe()
    def ajouter_partie_shortcut(self, event=None): self.ajouter_partie()
    def lancer_traitement_shortcut(self, event=None): self.lancer_traitement()
    def supprimer_selection_shortcut(self, event=None): self.supprimer_selection()

    # --- Core UI Functions (Keep as before) ---
    def choisir_fichier_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")], parent=self.root)
        if path:
            self.pdf_path_var.set(os.path.normpath(path))
            if not self.output_dir_var.get():
                 pdf_dir = os.path.dirname(path)
                 self.output_dir_var.set(os.path.join(pdf_dir, "Output_SplitMerge"))

    def choisir_dossier_sortie(self):
        path = filedialog.askdirectory(parent=self.root)
        if path: self.output_dir_var.set(os.path.normpath(path))

    def ouvrir_dossier_destination(self):
        path = self.output_dir_var.get()
        if not path: messagebox.showwarning("Attention", "Aucun dossier de destination défini.", parent=self.root); return
        if not os.path.isdir(path):
            if messagebox.askyesno("Dossier Inexistant", f"Dossier '{path}' inexistant.\nCréer maintenant ?", parent=self.root):
                try: os.makedirs(path); print(f"Info: Dossier '{path}' créé.")
                except Exception as e: messagebox.showerror("Erreur", f"Création dossier échouée:\n{e}", parent=self.root); return
            else: return
        try:
            if sys.platform == "win32": os.startfile(os.path.normpath(path))
            elif sys.platform == "darwin": subprocess.call(["open", os.path.normpath(path)])
            else: subprocess.call(["xdg-open", os.path.normpath(path)])
        except Exception as e: messagebox.showerror("Erreur", f"Ouverture dossier échouée:\n{e}", parent=self.root)

    def _add_default_part(self, parent_id):
        if not self.table_pdf.exists(parent_id): return
        part_name = "Partie 1"; existing_part_texts = [self.table_pdf.item(child, 'text') for child in self.table_pdf.get_children(parent_id)]
        part_num = 1
        while f"Partie {part_num}" in existing_part_texts: part_num += 1
        part_name = f"Partie {part_num}"
        part_id = self.table_pdf.insert(parent_id, 'end', text=part_name, values=(part_name, "1", "1"), tags=('part',))
        self.table_pdf.item(parent_id, open=True)
        try: self.table_pdf.selection_set(part_id); self.table_pdf.focus(part_id); self.table_pdf.see(part_id)
        except tk.TclError: pass

    def ajouter_groupe(self, event=None):
        self.root.focus_set()
        group_name = f"Nouveau_Groupe_{len(self.table_pdf.get_children('')) + 1}"
        existing_group_texts = [self.table_pdf.item(child, 'text') for child in self.table_pdf.get_children('')]
        group_num = 1
        while f"Nouveau_Groupe_{group_num}.pdf" in existing_group_texts or f"Nouveau_Groupe_{group_num}" in existing_group_texts: group_num += 1
        group_name = f"Nouveau_Groupe_{group_num}"
        group_id = self.table_pdf.insert('', 'end', text=group_name, values=(group_name, "-", "-"), tags=('group',))
        self._add_default_part(group_id)

    def ajouter_partie(self, event=None):
        self.root.focus_set()
        selected_items = self.table_pdf.selection()
        if not selected_items: messagebox.showwarning("Sélection Requise", "Veuillez sélectionner un groupe.", parent=self.root); return
        parent_id = selected_items[0]
        if self.table_pdf.parent(parent_id) != '' or 'group' not in self.table_pdf.item(parent_id, 'tags'):
             messagebox.showwarning("Sélection Invalide", "Veuillez sélectionner un élément 'Groupe'.", parent=self.root); return
        self._add_default_part(parent_id)

    def supprimer_selection(self):
        items = self.table_pdf.selection()
        if not items: messagebox.showwarning("Sélection Requise", "Sélectionner éléments à supprimer.", parent=self.root); return
        item_names = [f"'{self.table_pdf.item(item_id, 'text')}'" for item_id in items if self.table_pdf.exists(item_id)]
        if not item_names: return
        if messagebox.askyesno("Confirmation", f"Supprimer {len(item_names)} élément(s) ?\n({', '.join(item_names)})", parent=self.root):
            for item in reversed(items):
                if self.table_pdf.exists(item): self.table_pdf.delete(item)

    def tout_supprimer_pdf(self):
        if not self.table_pdf.get_children(): messagebox.showinfo("Info", "Tableau vide.", parent=self.root); return
        if messagebox.askyesno("Confirmation", "Réinitialiser ?", parent=self.root):
            self.table_pdf.delete(*self.table_pdf.get_children())
            self.pdf_path_var.set(""); self.output_dir_var.set("")
            # REMOVED: self.create_backup_var.set(False)

    # --- In-Place Editing (Keep as before) ---
    def modifier_cellule_pdf(self, event):
        active_edits = [w for w in self.root.winfo_children() if isinstance(w, (ttk.Entry, tk.Spinbox)) and hasattr(w, '_edit_cell_info')]
        for entry_widget in active_edits:
            current_item_id = self.table_pdf.identify_row(event.y); current_col_id = self.table_pdf.identify_column(event.x)
            if entry_widget.winfo_exists() and entry_widget._edit_cell_info != (current_item_id, current_col_id):
                 entry_widget.event_generate("<FocusOut>")
        region = self.table_pdf.identify_region(event.x, event.y); item_id = self.table_pdf.identify_row(event.y); column_id = self.table_pdf.identify_column(event.x)
        if region not in ("cell", "tree") or not item_id: return
        is_editing_this = any(hasattr(w, '_edit_cell_info') and w._edit_cell_info == (item_id, column_id) for w in self.root.winfo_children())
        if is_editing_this: return
        is_group = 'group' in self.table_pdf.item(item_id, 'tags'); is_part = 'part' in self.table_pdf.item(item_id, 'tags')
        col_index = -1
        if column_id == '#0': col_index = -1
        elif column_id.startswith('#'):
            try: col_index = int(column_id.replace("#", "")) - 1
            except ValueError: return
        if is_group and col_index in [1, 2]: return
        x, y, width, height = self.table_pdf.bbox(item_id, column_id)
        if not width or not height: return
        value = ""
        if col_index == -1: value = self.table_pdf.item(item_id, 'text')
        elif is_part and col_index in [1, 2]:
             try: value = self.table_pdf.item(item_id, 'values')[col_index]
             except IndexError: return
        else: return
        entry_var = tk.StringVar(value=str(value)); editor = None
        if is_part and col_index in [1, 2]:
            max_page = 9999; pdf_path = self.pdf_path_var.get()
            if pdf_path and os.path.exists(pdf_path) and PDF_LIB_AVAILABLE:
                try: max_page = len(PdfReader(pdf_path).pages)
                except Exception as e: print(f"Avertissement: Lire nb pages échoué: {e}")
            editor = tk.Spinbox(self.root, from_=1, to=max_page, textvariable=entry_var, wrap=False, width=5)
        else: editor = ttk.Entry(self.root, textvariable=entry_var)
        editor._edit_cell_info = (item_id, column_id)
        abs_x = self.table_pdf.winfo_rootx() + x; abs_y = self.table_pdf.winfo_rooty() + y
        root_x = abs_x - self.root.winfo_rootx(); root_y = abs_y - self.root.winfo_rooty()
        editor.place(x=root_x, y=root_y, width=width, height=height, anchor='nw'); editor.focus_force()
        if isinstance(editor, ttk.Entry): editor.select_range(0, 'end')
        elif isinstance(editor, tk.Spinbox): editor.selection('range', '0', 'end')
        def save_edit(event=None, cancel=False):
            if not editor.winfo_exists() or not hasattr(editor, '_edit_cell_info') or editor._edit_cell_info != (item_id, column_id): return
            if not self.table_pdf.exists(item_id):
                 if editor.winfo_exists(): editor.destroy(); return
            if not cancel:
                try:
                    new_value_str = entry_var.get().strip()
                    if not new_value_str: messagebox.showerror("Erreur", "Valeur vide non permise.", parent=self.root); editor.focus_force(); return
                    if col_index == -1:
                        invalid_chars = '/\\:*?"<>|'
                        if any(char in new_value_str for char in invalid_chars) or new_value_str in ['.', '..']:
                             messagebox.showerror("Erreur", f"Nom invalide.\nNe peut contenir: {invalid_chars} ou être '.'/'..'", parent=self.root); editor.focus_force(); return
                        if is_group and not new_value_str.lower().endswith('.pdf'): new_value_str += ".pdf"
                        self.table_pdf.item(item_id, text=new_value_str)
                        current_vals = list(self.table_pdf.item(item_id, 'values')); current_vals[0] = new_value_str; self.table_pdf.item(item_id, values=tuple(current_vals))
                    elif is_part and col_index in [1, 2]:
                        try:
                            page_num = int(new_value_str); assert page_num > 0
                            current_values = list(self.table_pdf.item(item_id, "values")); current_values[col_index] = page_num; self.table_pdf.item(item_id, values=tuple(current_values))
                        except (ValueError, AssertionError) as ve: messagebox.showerror("Validation Erreur", f"Page invalide: Entier positif requis.", parent=self.root); editor.focus_force(); return
                except Exception as e: print(f"Erreur sauvegarde édition: {e}"); messagebox.showerror("Erreur", f"Sauvegarde impossible: {e}", parent=self.root)
            if editor.winfo_exists(): editor.destroy()
            self.table_pdf.focus_set()
        editor.bind("<FocusOut>", save_edit); editor.bind("<Return>", save_edit); editor.bind("<KP_Enter>", save_edit); editor.bind("<Escape>", lambda e: save_edit(e, cancel=True))

    # --- Main Processing Logic (Backup code removed) ---
    def lancer_traitement(self, event=None):
        if not PDF_LIB_AVAILABLE: messagebox.showerror("Erreur Critique", "'pypdf' manquant.", parent=self.root); return
        pdf_path = self.pdf_path_var.get(); output_dir = self.output_dir_var.get(); groups = self.table_pdf.get_children('')
        if not pdf_path or not output_dir or not groups: messagebox.showwarning("Config Incomplète", "Vérifier source, destination et groupes/parties.", parent=self.root); return
        if not os.path.exists(pdf_path): messagebox.showerror("Erreur Fichier", f"Source PDF introuvable:\n{pdf_path}", parent=self.root); return
        if not os.path.isdir(output_dir):
            if messagebox.askyesno("Confirmer Création", f"Dossier destination '{os.path.basename(output_dir)}' inexistant.\nCréer ?", parent=self.root):
                try: os.makedirs(output_dir); print(f"Info: Dossier '{output_dir}' créé.")
                except Exception as e: messagebox.showerror("Erreur Création Dossier", f"Impossible de créer:\n{e}", parent=self.root); return
            else: return

        # REMOVED: Backup creation logic block

        progress_parent_frame = self.launch_btn.master; progress_frame = ttk.Frame(progress_parent_frame); progress_frame.pack(fill="x", pady=(5,0), before=self.launch_btn)
        progress_label = ttk.Label(progress_frame, text="Préparation..."); progress_label.pack(side="left", padx=(0, 5)); progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", maximum=len(groups))
        progress_bar.pack(fill="x", expand=True, side="left"); self.launch_btn.pack_forget(); self.root.update_idletasks()

        errors = [] # Initialize empty error list (no backup errors possible now)
        success_count = 0
        try:
            reader = PdfReader(pdf_path); total_pages = len(reader.pages)
            for group_idx, group_id in enumerate(groups):
                if not self.table_pdf.exists(group_id): continue
                group_item = self.table_pdf.item(group_id); group_name_raw = group_item['text'].strip()
                if not group_name_raw: errors.append(f"Groupe {group_idx+1}: Nom manquant."); continue
                group_name_base = group_name_raw[:-4] if group_name_raw.lower().endswith('.pdf') else group_name_raw
                invalid_chars = '/\\:*?"<>|';
                if any(char in group_name_base for char in invalid_chars) or group_name_base in ['.', '..']: errors.append(f"Groupe '{group_name_raw}': Nom fichier invalide."); continue
                group_filename = f"{group_name_base}.pdf"
                parts = self.table_pdf.get_children(group_id)
                if not parts: errors.append(f"Groupe '{group_filename}': Aucune partie."); progress_bar['value'] = group_idx + 1; self.root.update_idletasks(); continue
                progress_label.config(text=f"Groupe: {group_filename}..."); self.root.update_idletasks()
                group_writer = PdfWriter(); group_has_errors = False; pages_added_to_group = 0
                for part_idx, part_id in enumerate(parts):
                    if not self.table_pdf.exists(part_id): continue
                    part_item = self.table_pdf.item(part_id); part_name = part_item['text'].strip() or f"Partie_{part_idx+1}"; part_values = part_item['values']
                    try:
                        start_str, end_str = part_values[1], part_values[2]; start_page = int(start_str); end_page = int(end_str)
                        if not (0 < start_page <= end_page): raise ValueError("Plage invalide")
                        if start_page > total_pages: raise ValueError(f"Début {start_page} > Total {total_pages}")
                        adjusted_end_page = min(end_page, total_pages); current_part_pages = 0
                        for i in range(start_page - 1, adjusted_end_page):
                            try: group_writer.add_page(reader.pages[i]); current_part_pages += 1
                            except IndexError: errors.append(f"Groupe '{group_filename}', Partie '{part_name}': Erreur accès page {i+1}."); group_has_errors = True; break
                        if group_has_errors: continue
                        if current_part_pages == 0: errors.append(f"Groupe '{group_filename}', Partie '{part_name}': Aucune page dans {start_page}-{end_page}.")
                        else: pages_added_to_group += current_part_pages; print(f"  + Partie '{part_name}' ({start_page}-{adjusted_end_page}): {current_part_pages} pages.")
                    except (ValueError, TypeError) as page_err: errors.append(f"Groupe '{group_filename}', Partie '{part_name}': Pages invalides ('{start_str}'-'{end_str}'). {page_err}."); group_has_errors = True
                    except Exception as extract_err: errors.append(f"Groupe '{group_filename}', Partie '{part_name}': Erreur extraction: {extract_err}."); group_has_errors = True
                if pages_added_to_group == 0:
                    if not group_has_errors: errors.append(f"Groupe '{group_filename}': Aucune page ajoutée.")
                    progress_bar['value'] = group_idx + 1; self.root.update_idletasks(); continue
                output_path = os.path.join(output_dir, group_filename)
                if os.path.exists(output_path):
                    if not messagebox.askyesno("Fichier Existant", f"Remplacer '{group_filename}'?", parent=self.root, icon='warning'): errors.append(f"Groupe '{group_filename}': Non remplacé."); progress_bar['value'] = group_idx + 1; self.root.update_idletasks(); continue
                try:
                    with open(output_path, "wb") as final_outfile: group_writer.write(final_outfile)
                    success_count += 1; print(f"Info: Groupe '{group_filename}' créé ({pages_added_to_group} pages).")
                except Exception as merge_err: errors.append(f"Groupe '{group_filename}': Erreur sauvegarde: {merge_err}")
                progress_bar['value'] = group_idx + 1; self.root.update_idletasks()
        except FileNotFoundError: messagebox.showerror("Erreur Fichier", f"Source PDF introuvable:\n{pdf_path}", parent=self.root)
        except Exception as main_err: messagebox.showerror("Erreur Inattendue", f"Erreur majeure:\n{main_err}", parent=self.root); errors.append(f"Erreur Globale: {main_err}")
        finally:
            if 'progress_frame' in locals() and progress_frame.winfo_exists(): progress_frame.destroy()
            self.launch_btn.pack(fill="x", pady=5)
            if errors:
                error_details = "\n - ".join(errors)
                msg = f"Terminé.\n\n{success_count} fichier(s) créé(s).\n\nErreurs/Infos:\n - {error_details}"
                messagebox.showwarning("Résultat avec Erreurs/Infos", msg, parent=self.root)
            elif success_count > 0:
                if messagebox.askyesno("Succès", f"Terminé ! ✅\n\n{success_count} fichier(s) créé(s).\n\nOuvrir dossier ?", parent=self.root): self.ouvrir_dossier_destination()
            else: messagebox.showinfo("Info", "Aucun fichier créé.", parent=self.root)

# --- END OF CLASS PdfSplitterApp ---

if __name__ == "__main__":
    # --- Dependency Check ---
    if not PDF_LIB_AVAILABLE:
        critical_error_msg = "ERREUR CRITIQUE: Module 'pypdf' (v3+) manquant.\n\nInstallez-le (`pip install pypdf`) et relancez."
        print("="*60); print(critical_error_msg.replace('\n\n','\n').replace('\n','\n ')); print("="*60)
        try: root_err = tk.Tk(); root_err.withdraw(); messagebox.showerror("Erreur Dépendance", critical_error_msg); root_err.destroy()
        except Exception as tk_err: print(f"(Note: Tkinter messagebox échec: {tk_err})")
        sys.exit(1)

    # --- Setup Main Window ---
    root = tk.Tk()
    # --- Theme Loading ---
    theme_to_use = None
    try:
        from ttkthemes import ThemedTk
        available = ThemedTk().get_themes(); preferred = ['plastik', 'arc', 'adapta', 'ubuntu', 'radiance']
        for theme in preferred:
            if theme in available: theme_to_use = theme; break
        if not theme_to_use and available: theme_to_use = available[0]
        if theme_to_use: root.destroy(); root = ThemedTk(theme=theme_to_use); print(f"Info: Thème ttk: '{theme_to_use}'")
        else: print("Avertissement: Thème ttkthemes non trouvé. Thème défaut.")
    except ImportError: print("Info: 'ttkthemes' non trouvé. Thème défaut.")
    except Exception as e: print(f"Erreur thème: {e}. Thème défaut."); root = tk.Tk() # Fallback

    # --- Initialize and Show Main App ---
    app = PdfSplitterApp(root)
    root.mainloop()

# --- END OF FILE pdf_splitter_app.py ---
# --- END OF FILE PDF SPLITTER.py ---
# --- END OF FILE XS PDF ASSISTANT FL.py ---