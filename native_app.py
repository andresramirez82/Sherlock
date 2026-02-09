import flet as ft
import sys
import os
import asyncio
import threading
from typing import List

# Add the directory containing 'sherlock_project' to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
parent_of_package = os.path.dirname(package_root)
sys.path.append(parent_of_package)

from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus

class FletNotify(QueryNotify):
    def __init__(self, page: ft.Page, on_result):
        super().__init__()
        self.page = page
        self.on_result = on_result

    def start(self, message=None):
        pass

    def update(self, result):
        if result.status == QueryStatus.CLAIMED:
            # We call this via page.run_task or similar to be thread-safe
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
    
    # Header
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

    results_list = ft.ListView(expand=1, spacing=10, padding=20)
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

    def on_result(result):
        results_list.controls.insert(0, ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(result.site_name, weight="bold", size=16),
                    ft.Container(
                        content=ft.Text("CLAIMED", size=10, color="green"),
                        border=ft.border.all(1, "green"),
                        padding=ft.padding.all(5),
                        border_radius=5
                    )
                ], alignment="spaceBetween"),
                ft.TextButton(
                    text=result.site_url_user,
                    url=result.site_url_user,
                    style=ft.ButtonStyle(color="#a0a4b8")
                )
            ]),
            bgcolor="#191b22",
            padding=15,
            border_radius=15,
            border=ft.border.all(1, "rgba(255, 255, 255, 0.1)")
        ))
        
        # Update count
        count = int(found_count_text.value.split()[0]) + 1
        found_count_text.value = f"{count} found"
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

        # Load sites
        data_path = os.path.join(package_root, "resources", "data.json")
        sites = SitesInformation(data_path)
        
        notify = FletNotify(page, on_result)

        def run_scan():
            sherlock(username, sites.sites, notify)
            # Finalize UI
            progress_ring.visible = False
            status_text.value = "Scan complete"
            username_input.disabled = False
            search_btn.disabled = False
            page.update()

        threading.Thread(target=run_scan, daemon=True).start()

    username_input = ft.TextField(
        hint_text="Enter username...",
        border_color="#00f2ff",
        focused_border_color="#00f2ff",
        expand=True,
        on_submit=search_click,
        text_size=18,
        height=60,
    )

    search_btn = ft.ElevatedButton(
        content=ft.Text("SEARCH", color="black", weight="bold"),
        on_click=search_click,
        style=ft.ButtonStyle(
            bgcolor="#00f2ff",
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        ),
        height=60,
    )

    page.add(
        header,
        ft.Divider(height=20, color="transparent"),
        ft.Row([username_input, search_btn], spacing=10),
        ft.Divider(height=20, color="transparent"),
        status_bar,
        ft.Divider(height=10, color="transparent"),
        results_list
    )

if __name__ == "__main__":
    ft.app(target=main)
