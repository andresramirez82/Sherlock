import flet as ft
import sys
import os
import threading
import json

# Configuración de rutas para importar sherlock_project
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
parent_of_package = os.path.dirname(package_root)
sys.path.append(parent_of_package)

try:
    from sherlock_project.sherlock import sherlock
    from sherlock_project.notify import QueryNotify
    from sherlock_project.result import QueryStatus
except ImportError:
    print("Error: No se pudo encontrar el paquete 'sherlock_project'. Asegúrate de que la ruta sea correcta.")

class FletNotify(QueryNotify):
    def __init__(self, page: ft.Page, on_result):
        super().__init__()
        self.page = page
        self.on_result = on_result

    def start(self, message=None):
        pass

    def update(self, result):
        # Solo notificamos si el usuario fue encontrado (CLAIMED)
        if result.status == QueryStatus.CLAIMED:
            self.on_result(result)

    def finish(self, message=None):
        pass

def main(page: ft.Page):
    page.title = "Sherlock OSINT - Native App"
    page.theme_mode = "dark"
    page.window_width = 900
    page.window_height = 800
    page.padding = 30
    page.bgcolor = "#0c0d10"

    # --- UI COMPONENTS ---
    
    header = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("🕵️‍♂️", size=40),
                    ft.Text("SHERLOCK", size=40, weight="bold", color="white"),
                ],
                alignment="center",
            ),
            ft.Text(
                "Search for usernames across social networks",
                color="#a0a4b8",
                size=16,
                text_align="center",
            ),
        ],
        horizontal_alignment="center",
        spacing=0,
    )

    results_list = ft.ListView(expand=True, spacing=10, padding=20)
    found_count_text = ft.Text("0 found", color="green", weight="bold")
    progress_ring = ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False)
    status_text = ft.Text("Ready", color="#00f2ff")
    
    status_bar = ft.Container(
        content=ft.Row(
            [
                status_text,
                progress_ring,
                ft.VerticalDivider(width=20, color="transparent"),
                found_count_text,
            ],
            alignment="start",
        ),
        bgcolor="rgba(255, 255, 255, 0.05)",
        padding=15,
        border_radius=10,
        visible=False
    )

    # --- LOGIC ---

    def on_result(result):
        results_list.controls.insert(0, ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(result.site_name, weight="bold", size=16),
                    ft.Container(
                        content=ft.Text("CLAIMED", size=10, color="green"),
                        border=ft.Border.all(1, "green"),
                        padding=5,
                        border_radius=5
                    )
                ], alignment="spaceBetween"),
                ft.TextButton(
                    content=ft.Text(result.site_url_user, color="#a0a4b8"),
                    url=result.site_url_user
                )
            ]),
            bgcolor="#191b22",
            padding=15,
            border_radius=15,
            border=ft.Border.all(1, "rgba(255, 255, 255, 0.1)")
        ))
        
        # Actualizar contador
        try:
            count = int(found_count_text.value.split()[0]) + 1
            found_count_text.value = f"{count} found"
        except:
            pass
        page.update()

    def search_click(e):
        username = username_input.value.strip()
        if not username:
            return

        # Reset UI
        results_list.controls.clear()
        found_count_text.value = "0 found"
        status_bar.visible = True
        progress_ring.visible = True
        status_text.value = f"Scanning {username}..."
        username_input.disabled = True
        search_btn.disabled = True
        page.update()

        # Load sites data
        data_path = os.path.join(current_dir, "resources", "data.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                site_data = json.load(f)
            site_data.pop("$schema", None)
        except Exception as err:
            status_text.value = f"Error loading data: {err}"
            page.update()
            return

        notify = FletNotify(page, on_result)

        def run_scan():
            sherlock(username, site_data, notify)
            # Finalize UI
            progress_ring.visible = False
            status_text.value = "Scan complete"
            username_input.disabled = False
            search_btn.disabled = False
            page.update()

        threading.Thread(target=run_scan, daemon=True).start()

    # --- INPUTS ---

    username_input = ft.TextField(
        hint_text="Enter username...",
        border_color="#00f2ff",
        focused_border_color="#00f2ff",
        expand=True,
        on_submit=search_click,
        text_size=18,
        height=60,
    )

    search_btn = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Text("SEARCH", color="black", weight="bold"),
            on_click=search_click,
            style=ft.ButtonStyle(
                bgcolor="#00f2ff",
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            height=60,
        )
    )

    # --- FOOTER (CORREGIDO) ---

    footer = ft.Column(
        [
            ft.Row(
                [
                    ft.Text("©️", size=40),
                    ft.Text("Andrés Nicolás Ramirez", weight="bold"),
                    ft.Text("📧", size=40),
                    ft.Text("andresramirez82@gmail.com", size=12, color="#a0a4b8"),
                ],
                alignment="center",
            ),
            ft.Row(
                ft.Column(
                    
                    ft.TextButton(
                        content=ft.Text("GitHub", color="#a0a4b8"),
                        url="https://github.com/andresramirez82",
                    ),
                    width=100,
                    height=50,
                ),
               alignment="center",
            ),
            
        ],
        alignment="center",
        spacing=0,
    )


    # --- MAIN LAYOUT ---
    
    # Usamos una Column con expand=True para que el ListView respete los límites
    main_content = ft.Column(
        [
            header,
            ft.Divider(height=20, color="transparent"),
            ft.Row([username_input, search_btn], spacing=10),
            ft.Divider(height=20, color="transparent"),
            status_bar,
            ft.Divider(height=10, color="transparent"),
            results_list,
            footer,
        ],
        expand=True,
    )

    page.add(main_content)

if __name__ == "__main__":
    ft.run(main)