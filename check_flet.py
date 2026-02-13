
import flet as ft
print(f"Has FilledButton: {hasattr(ft, 'FilledButton')}")
print(f"Has Button: {hasattr(ft, 'Button')}")
try:
    btn = ft.Button(text="Test")
    print("ft.Button instantiated successfully")
except Exception as e:
    print(f"ft.Button failed: {e}")
