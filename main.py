import customtkinter as ctk
from model.project import Project
import os

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)


def open_main_app():
    """Mở ứng dụng chính sau khi đăng nhập"""
    from view.main_window_modern import ModernMainWindow
    from controoller.maincontrooler import MainController
    
    project = Project()
    app = ModernMainWindow(project)
    controller = MainController(app)
    app.mainloop()


def open_admin():
    """Mở Admin Key Manager"""
    from view.admin.adminmanager import AdminManagerWindow
    from controoller.admin.admin_controller import AdminController
    
    app = AdminManagerWindow()
    controller = AdminController(app)
    app.mainloop()


def main():
    from view.login_window import LoginWindow
    
    # Show login window
    login = LoginWindow()
    login.mainloop()
    
    # Check result
    if login.login_success:
        open_main_app()
    elif login.open_admin:
        open_admin()


if __name__ == "__main__":
    main()
