```markdown
# AGENTS.md - Instructions for AI Agents

## Project Overview

This is a Legal CRM (Customer Relationship Management) application. The project has undergone a refactoring process.

*   **Original Version:** Primarily in `main_app.py` using Tkinter directly with UI logic mixed with application logic. Associated UI files might be `*_ui.py` at the root level that seem to be part of this older structure (e.g., `seguimiento_ui.py`, `partes_ui.py` if not fully integrated into the refactored version).
*   **Refactored Version:** This is the current focus for development and completion.
    *   **Main Entry Point:** `main_app_refactored_entry.py`
    *   **Main Window Logic:** `main_window_refactored.py` (controls the overall application shell and interactions between main modules).
    *   **Case Details:** When a case is opened, details are shown in a separate `CaseDetailsWindow` (from `case_details_window.py`), which itself contains a notebook with various tabs for different aspects of the case.
    *   **Modular UI Tabs:**
        *   `clientes_ui.py`: Manages the client list and client creation/editing dialogs (from the main window).
        *   `casos_ui.py`: Manages the case list for a selected client and case creation/editing dialogs (from the main window).
        *   `audiencias_ui.py`: Manages the calendar and daily audiencia list (in the main window).
        *   The `CaseDetailsWindow` hosts tabs like:
            *   `casos_detalles_ui.py`: Displays detailed read-only information about the case.
            *   `documentos_ui.py`: For managing case-related document folders.
            *   `tareas_ui.py`: For managing tasks related to the case.
            *   `partes_ui.py`: For managing parties involved in the case.
            *   `seguimiento_ui.py`: For logging activities related to the case.
            *   `etiquetas_ui.py`: For managing global tags and applying them to clients/cases.
            *   `financiero_ui.py`: For managing financial aspects (honorarios, gastos, facturas) of the case.
    *   **Database:** All data is stored in an SQLite database managed by `crm_database.py`.
    *   **IA Features:** `ia_ui.py` provides UI for AI-assisted features. These features are intended to interact with a local server, defined in `mcp_server.py`. Currently, the IA features are not a top priority for core CRM functionality.

## How to Run (Refactored Version)

1.  Ensure all dependencies are installed. Key dependencies include:
    *   `tkinter` (usually part of standard Python)
    *   `sqlite3` (usually part of standard Python)
    *   `Pillow` (PIL fork)
    *   `plyer`
    *   `pystray`
    *   `tkcalendar`
    *   `requests` (for IA features)
    *   `python-docx` (for IA features saving to .docx)
    *   (For `mcp_server.py`): `Flask`, `openai`
    *   Install using: `pip install Pillow plyer pystray tkcalendar requests python-docx Flask openai`
2.  Run the main entry point:
    ```bash
    python main_app_refactored_entry.py
    ```
3.  If testing IA features, `mcp_server.py` would need to be run separately (e.g., `python mcp_server.py`), and a compatible LLM (like Ollama with a Gemma model) should be running and configured in `mcp_server.py`.

## Key Design Points (Refactored Version)

*   **Modularity:** UI components are broken into their own files/classes.
*   **Central Controller:** `main_window_refactored.py` acts as a central point for managing shared state like `selected_client` and `selected_case`, and for coordinating actions between different UI modules.
*   **`CaseDetailsWindow`:** Provides a dedicated window for all information and actions related to a single case, improving organization.
*   **Tagging System:** Uses a relational system (`etiquetas`, `cliente_etiquetas`, `caso_etiquetas` tables). The old text-based `etiquetas` columns in `clientes` and `casos` tables are considered deprecated for new operations.
*   **Database Abstraction:** `crm_database.py` encapsulates all SQLite operations.

## Agent Instructions

*   When working on UI elements, ensure they are placed within the correct parent frame/window as per the modular structure.
*   Dialogs for creating/editing items related to a specific case (e.g., new Tarea for a Case) should be modal to the `CaseDetailsWindow` instance for that case.
*   Data refresh logic is important. After CUD operations, ensure relevant lists or detail views are updated.
*   Prioritize functionality and stability of the refactored version.
```
