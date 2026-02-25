import customtkinter as ctk
from view.main_window_modern import ModernMainWindow
from controoller.maincontrooler import MainController
from model.project import Project
import os

# Ensure temp directory exists or other setup
os.makedirs("temp", exist_ok=True)

def main():
    # Initialize Config/Project
    project = Project()
    
    # Initialize UI - MODERN VERSION
    app = ModernMainWindow(project)
    
    # Initialize Controller
    controller = MainController(app)
    
    # Run
    app.mainloop()

if __name__ == "__main__":
    main()
