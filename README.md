# XS PDF ASSISTANT 📄✂️

A desktop application built with Python and Tkinter (using ttk themes) for splitting and merging specific page ranges from a source PDF into multiple, organized output PDF files.

## Features

*   **Source & Destination:** Select a source PDF file and a destination folder for output.
*   **Group-Based Output:** Define "Groups", where each group corresponds to one output PDF file.
*   **Part Definition:** Within each group, define "Parts" specifying the start and end page numbers from the source PDF to include.
*   **Editing:**
    *   Double-click group or part names to rename them.
    *   Single-click the "Page Début" or "Page Fin" columns for a part to edit the page numbers.
    *   Contextual "✓" icon appears next to the edited cell for saving (or press Enter/click away). Escape cancels.
*   **Organization:**
    *   **Add:** Add new Groups and Parts easily.
    *   **Duplicate:** Duplicate selected groups (including their parts) or individual parts.
    *   **Move Between Groups:** Select a part, click "➡️ Déplacer Partie", select the target group, and click "✅ Confirmer Destination".
    *   **Reorder Parts:** Select a part and use the "↑" and "↓" buttons to change its order within its group (this affects the order pages are added to the output PDF).
    *   **Delete:** Remove selected groups or parts.
    *   **Reset:** Clear the entire configuration (groups, parts, source/destination paths).
*   **Processing:**
    *   "🚀 Lancer Traitement" button processes the defined structure, reading pages from the source PDF and writing them to the corresponding group output files.
    *   Handles existing output files by prompting the user whether to overwrite.
    *   Provides success or error/warning feedback upon completion.
*   **Convenience:**
    *   "↗️" button to quickly open the selected output destination folder.
    *   Uses themed widgets (`ttkthemes`) for a potentially better look and feel if the library is installed.
    *   Includes a custom application icon.

## Requirements

*   **Python:** 3.7 or higher recommended.
*   **Libraries:**
    *   `pypdf`: For reading and writing PDF files.
    *   `ttkthemes` (Optional): For improved widget styling. The application will fall back to standard ttk themes if not installed.

## Installation

1.  **Clone or Download:** Get the application files (`XS PDF ASSISTANT.py` and `oonfg-z0zg7-001.ico`).
    ```bash
    # Example using git clone
    git clone <your-repository-url>
    cd <repository-directory>
    ```
2.  **Create Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # Activate (Windows)
    .\venv\Scripts\activate
    # Activate (macOS/Linux)
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install pypdf
    # Optional, for better themes:
    pip install ttkthemes
    ```

## Usage

1.  **Run the Application:**
    ```bash
    python "XS PDF ASSISTANT.py"
    ```
    *(Ensure the `.ico` file is in the same directory)*

2.  **Select Files/Folders:**
    *   Click "📂" to choose your source PDF file.
    *   Click "📁" to choose the folder where the output PDFs will be saved (defaults to an "Output\_SplitMerge" subfolder near the source PDF if not set).

3.  **Define Structure:**
    *   Click "➕ Groupe" to add a new output file definition. The name will automatically end in `.pdf`.
    *   Select a group and click "➕ Partie" to add a page range definition to that group.
    *   *Edit Names:* Double-click on a group or part name in the table to change it. A "✓" icon appears; click it or press Enter to save.
    *   *Edit Pages:* Single-click on the "Page Début" or "Page Fin" number for a part. Use the spinbox or type the number. A "✓" icon appears; click it or press Enter to save.

4.  **Organize (Optional):**
    *   *Duplicate:* Select a group or part, click "➕ Dupliquer".
    *   *Move Part (Group):* Select the *part* to move, click "➡️ Déplacer Partie", select the *destination group*, click "✅ Confirmer Destination".
    *   *Reorder Part (Within Group):* Select a part, use the "↑" / "↓" buttons.
    *   *Delete:* Select item(s), click "❌ Supprimer".
    *   *Reset:* Click "🧹 Réinitialiser" to clear everything.

5.  **Process:**
    *   Click "🚀 Lancer Traitement".
    *   The application will read the source PDF and create the output files based on your defined groups and parts (respecting the order of parts within groups).
    *   Check the pop-up messages for success or errors.

6.  **Open Output:**
    *   Click "↗️" to open the selected destination folder in your file explorer.

