import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import subprocess
import threading
from typing import Dict, List

class ServiceController:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Database Services Controller")
        self.root.geometry("400x300")
        
        # Configure style
        style = ttk.Style()
        style.configure("Running.TLabel", foreground="green")
        style.configure("Stopped.TLabel", foreground="red")
        
        # Service definitions
        self.services = {
            "MySQL": "MySQL80",  # Default MySQL 8.0 service name
            "MongoDB": "MongoDB"  # Default MongoDB service name
        }
        
        self.create_widgets()
        self.root.after(1000, self.update_status)  # Update status every second
    
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add title
        title_label = ttk.Label(
            main_frame, 
            text="Database Services Control Panel",
            font=("Helvetica", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Headers
        ttk.Label(main_frame, text="Service").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(main_frame, text="Status").grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(main_frame, text="Action").grid(row=1, column=2, padx=5, pady=5)
        
        # Add service controls
        self.status_labels: Dict[str, ttk.Label] = {}
        self.action_buttons: Dict[str, ttk.Button] = {}
        
        for idx, (service_name, service_id) in enumerate(self.services.items(), start=2):
            # Service name
            ttk.Label(main_frame, text=service_name).grid(
                row=idx, column=0, padx=5, pady=5
            )
            
            # Status label
            status_label = ttk.Label(main_frame, text="Checking...")
            status_label.grid(row=idx, column=1, padx=5, pady=5)
            self.status_labels[service_id] = status_label
            
            # Action button
            action_button = ttk.Button(
                main_frame,
                text="Loading...",
                command=lambda s=service_id: self.toggle_service(s)
            )
            action_button.grid(row=idx, column=2, padx=5, pady=5)
            self.action_buttons[service_id] = action_button
        
        # Add refresh button
        ttk.Button(
            main_frame,
            text="Refresh Status",
            command=self.update_status
        ).grid(row=len(self.services) + 2, column=0, columnspan=3, pady=10)
    
    def get_service_status(self, service_name: str) -> bool:
        """Check if a Windows service is running."""
        try:
            service = psutil.win_service_get(service_name)
            return service.status() == "running"
        except Exception:
            return False
    
    def toggle_service(self, service_name: str):
        """Toggle service status between running and stopped."""
        def run_command():
            try:
                is_running = self.get_service_status(service_name)
                action = "stop" if is_running else "start"
                
                # Run command with elevated privileges
                subprocess.run(
                    ["net", action, service_name],
                    check=True,
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.root.after(1000, self.update_status)  # Update status after action
                messagebox.showinfo(
                    "Success",
                    f"Successfully {'stopped' if is_running else 'started'} {service_name}"
                )
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to {'stop' if is_running else 'start'} {service_name}.\n"
                    f"Error: {e.stderr}\n\n"
                    "Make sure you're running the application as administrator."
                )
        
        # Run in separate thread to prevent GUI freezing
        threading.Thread(target=run_command, daemon=True).start()
    
    def update_status(self):
        """Update the status of all services."""
        for service_id in self.services.values():
            is_running = self.get_service_status(service_id)
            
            # Update status label
            self.status_labels[service_id].configure(
                text="Running" if is_running else "Stopped",
                style="Running.TLabel" if is_running else "Stopped.TLabel"
            )
            
            # Update button text
            self.action_buttons[service_id].configure(
                text="Stop" if is_running else "Start"
            )
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = ServiceController()
    app.run()