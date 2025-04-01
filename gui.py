import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from inputs.vote_data import ridings
from inputs.party_data import all_parties
from ElectionGraphicMachine import generate_individual_graphics

class ValidationFrame(ttk.Frame):
    """Frame to display validation status of input folders and files"""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        
    def create_widgets(self):
        # Create validation indicators with icons
        self.validation_frame = ttk.LabelFrame(self, text="Input Validation", padding="5")
        self.validation_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create grid for validation items
        self.validation_items = {
            "Required Images": ("Required_Images/", ["background.jpg"]),
            "Input Data": ("inputs/", ["vote_data.py", "party_data.py"]),
            "Riding Data": ("irlriding/", []),
            "SVG Files": ("svg/", []),
            "Party Graphics": ("party_graphics/", []),
            "Candidate Photos": ("facesteals/", [])
        }
        
        row = 0
        for label, (folder, required_files) in self.validation_items.items():
            ttk.Label(self.validation_frame, text=f"{label}:").grid(row=row, column=0, sticky='w', padx=5)
            status_label = ttk.Label(self.validation_frame, text="❌")
            status_label.grid(row=row, column=1, padx=5)
            
            # Store reference to status label
            self.validation_items[label] = (folder, required_files, status_label)
            row += 1
            
    def validate_all(self):
        """Validate all input folders and files"""
        all_valid = True
        validation_messages = []
        
        for label, (folder, required_files, status_label) in self.validation_items.items():
            is_valid, message = self.validate_item(folder, required_files)
            status_label.config(text="✓" if is_valid else "❌", 
                              foreground="green" if is_valid else "red")
            
            if not is_valid:
                all_valid = False
                validation_messages.append(f"{label}: {message}")
        
        return all_valid, validation_messages
    
    def validate_item(self, folder, required_files):
        """Validate a single input folder and its required files"""
        # Check if folder exists
        if not os.path.exists(folder):
            return False, f"Folder '{folder}' not found"
            
        # Check required files if any
        for file in required_files:
            file_path = os.path.join(folder, file)
            if not os.path.exists(file_path):
                return False, f"Required file '{file}' not found in {folder}"
            
        # For folders that should not be empty
        if not required_files and not os.listdir(folder):
            return False, f"Folder '{folder}' is empty"
            
        return True, "Valid"

class ConfigFrame(ttk.Frame):
    """Frame for configuration options"""
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        
    def create_widgets(self):
        # Create config frame
        self.config_frame = ttk.LabelFrame(self, text="Configuration", padding="5")
        self.config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Variables
        self.num_graphics = tk.StringVar(value="40")
        self.num_selected_steps = tk.StringVar(value="2")
        self.byelection = tk.BooleanVar(value=False)
        self.seats_in_election = tk.StringVar(value="1")
        
        # Create grid for config items
        row = 0
        # Total steps
        ttk.Label(self.config_frame, text="Total Number of Steps:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.config_frame, textvariable=self.num_graphics, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        # Selected steps
        ttk.Label(self.config_frame, text="Number of Selected Steps:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.config_frame, textvariable=self.num_selected_steps, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        # Byelection checkbox
        ttk.Checkbutton(self.config_frame, text="Byelection", variable=self.byelection).grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        # Seats in election
        ttk.Label(self.config_frame, text="Seats in Election:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.config_frame, textvariable=self.seats_in_election, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
    
    def validate(self):
        """Validate configuration values"""
        try:
            num_graphics = int(self.num_graphics.get())
            num_selected_steps = int(self.num_selected_steps.get())
            seats_in_election = int(self.seats_in_election.get())
            
            if num_graphics < 1:
                return False, "Total number of steps must be at least 1"
            
            if num_selected_steps < 2:
                return False, "Number of selected steps must be at least 2"
            
            if num_selected_steps > num_graphics:
                return False, "Selected steps cannot exceed total steps"
            
            if seats_in_election < 1:
                return False, "Number of seats must be at least 1"
            
            return True, "Valid"
        except ValueError:
            return False, "Please enter valid numbers"
    
    def get_config(self):
        """Get configuration values"""
        return {
            'num_graphics': int(self.num_graphics.get()),
            'num_selected_steps': int(self.num_selected_steps.get()),
            'byelection': self.byelection.get(),
            'seats_in_election': int(self.seats_in_election.get())
        }

class RidingConfirmationDialog:
    def __init__(self, parent, riding, riding_index, total_ridings):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Confirm Riding {riding_index + 1}/{total_ridings}: {riding['name']}")
        self.dialog.geometry("900x600")  # Even smaller dialog window
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.riding = riding
        self.riding_name = riding['name'].replace(" ", "_")
        self.output_dir = 'output_images'
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header with riding info
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=2)
        ttk.Label(header_frame, text=f"Riding: {riding['name']}", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"({riding_index + 1} of {total_ridings})", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Create scrollable frame
        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel event for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create button frame at the bottom
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create status label
        self.status_label = ttk.Label(button_frame, text="Loading images...", font=('Helvetica', 10))
        self.status_label.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Add buttons
        self.reroll_button = ttk.Button(button_frame, text="Reroll", command=self.reroll)
        self.reroll_button.pack(side=tk.LEFT, padx=5)
        
        self.accept_button = ttk.Button(button_frame, text="Accept", command=self.accept)
        self.accept_button.pack(side=tk.RIGHT, padx=5)
        
        self.result = False
        self.load_riding_images()
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def load_riding_images(self):
        """Load and display all images for this riding in a grid layout with thumbnails"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Get all images for this riding
        images = []
        try:
            for filename in os.listdir(self.output_dir):
                if filename.startswith(self.riding_name) and filename.endswith('.png'):
                    images.append(filename)
            
            if not images:
                ttk.Label(self.scrollable_frame, text=f"No images found for {self.riding['name']}", font=('Helvetica', 12)).pack(pady=10)
                self.status_label.config(text=f"No images found for this riding")
                return
                
            # Sort images by step number
            images.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
            
            # Check if there's a line graph
            line_graphs = []
            for filename in os.listdir(self.output_dir):
                if filename.startswith(f"line_graph_riding_") and self.riding_name in filename and filename.endswith('.png'):
                    line_graphs.append(filename)
            
            # If there's a line graph, add it to the top
            if line_graphs:
                graph_frame = ttk.LabelFrame(self.scrollable_frame, text="Vote Progression")
                graph_frame.pack(fill=tk.X, padx=2, pady=2)
                
                for graph_file in line_graphs:
                    try:
                        graph_path = os.path.join(self.output_dir, graph_file)
                        graph_image = Image.open(graph_path)
                        
                        # Make line graph smaller
                        window_width = 400
                        aspect_ratio = graph_image.height / graph_image.width
                        new_width = window_width
                        new_height = int(new_width * aspect_ratio)
                        graph_image = graph_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        graph_photo = ImageTk.PhotoImage(graph_image)
                        
                        graph_label = ttk.Label(graph_frame, image=graph_photo)
                        graph_label.image = graph_photo
                        graph_label.pack(pady=2)
                    except Exception as e:
                        print(f"ERROR loading graph {graph_file}: {e}")
            
            # Create a grid frame for the step images
            grid_frame = ttk.Frame(self.scrollable_frame)
            grid_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Define grid layout parameters - more columns and smaller thumbnails
            num_cols = 5  # Show 5 thumbnails per row
            thumbnail_width = 160  # Even smaller thumbnails
            
            # Create a thumbnail for each image in a grid layout
            for i, image_file in enumerate(images):
                try:
                    # Get step number for display
                    step_num = image_file.split('_')[-1].split('.')[0]
                    
                    # Calculate row and column position
                    row = i // num_cols
                    col = i % num_cols
                    
                    # Create frame for each image
                    image_frame = ttk.LabelFrame(grid_frame, text=f"Step {step_num}")
                    image_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
                    
                    # Load and display image
                    image_path = os.path.join(self.output_dir, image_file)
                    
                    try:
                        # Create thumbnail
                        image = Image.open(image_path)
                        aspect_ratio = image.height / image.width
                        new_width = thumbnail_width
                        new_height = int(new_width * aspect_ratio)
                        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        
                        # Create label with image
                        label = ttk.Label(image_frame, image=photo)
                        label.image = photo
                        label.pack(pady=1, padx=1)
                        
                        # Make the label clickable
                        label.bind("<Button-1>", lambda e, path=image_path: self.show_large_image(path))
                        
                    except Exception as img_error:
                        print(f"ERROR loading image {image_file}: {img_error}")
                        ttk.Label(image_frame, text="Error", foreground="red").pack()
                    
                except Exception as frame_error:
                    print(f"ERROR creating frame for image {image_file}: {frame_error}")
                    continue
            
            # Configure grid weights
            for i in range(num_cols):
                grid_frame.columnconfigure(i, weight=1)
            
            self.status_label.config(text=f"Loaded {len(images)} images")
            
        except Exception as e:
            print(f"ERROR in load_riding_images: {e}")
            import traceback
            traceback.print_exc()
            ttk.Label(self.scrollable_frame, text=f"Error loading images", foreground="red", font=('Helvetica', 12)).pack(pady=10)
            self.status_label.config(text="Error loading images")
    
    def show_large_image(self, image_path):
        """Show a larger version of the image in a new window"""
        try:
            top = tk.Toplevel(self.dialog)
            top.title("Full Size Image")
            
            # Load the image
            image = Image.open(image_path)
            
            # Resize to fit screen if too large
            screen_width = self.dialog.winfo_screenwidth() - 100
            screen_height = self.dialog.winfo_screenheight() - 100
            
            if image.width > screen_width or image.height > screen_height:
                # Calculate resize dimensions to maintain aspect ratio
                width_ratio = screen_width / image.width
                height_ratio = screen_height / image.height
                resize_ratio = min(width_ratio, height_ratio)
                
                new_width = int(image.width * resize_ratio)
                new_height = int(image.height * resize_ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            # Create canvas for image
            canvas = tk.Canvas(top, width=image.width, height=image.height)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Add image to canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep a reference
            
            # Add close button
            ttk.Button(top, text="Close", command=top.destroy).pack(pady=10)
            
        except Exception as e:
            print(f"ERROR showing large image: {e}")
            messagebox.showerror("Error", f"Failed to open image: {e}")
    
    def delete_riding_images(self):
        """Delete all images for this riding"""
        try:
            print(f"DEBUG GUI: Deleting images for riding {self.riding_name}")
            count = 0
            for filename in os.listdir(self.output_dir):
                if (filename.startswith(self.riding_name) or 
                    (filename.startswith("line_graph_riding_") and self.riding_name in filename)) and filename.endswith('.png'):
                    file_path = os.path.join(self.output_dir, filename)
                    os.remove(file_path)
                    count += 1
            print(f"DEBUG GUI: Deleted {count} images for riding {self.riding_name}")
            return count
        except Exception as e:
            print(f"ERROR deleting images: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def reroll(self):
        """Delete all images and set result to True for reroll"""
        # Disable buttons while processing
        self.reroll_button.config(state="disabled")
        self.accept_button.config(state="disabled")
        self.status_label.config(text="Deleting images for reroll...")
        self.dialog.update()
        
        # Delete existing images
        count = self.delete_riding_images()
        
        # Set result and close dialog
        self.result = True
        self.status_label.config(text=f"Deleted {count} images. Rerolling...")
        self.dialog.update()
        self.dialog.after(500, self.dialog.destroy)  # Small delay to show message
    
    def accept(self):
        """Set result to False for accept and close dialog"""
        self.result = False
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result

class ElectionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Election Graphics Generator")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add validation frame
        self.validation_frame = ValidationFrame(self.main_frame)
        self.validation_frame.pack(fill=tk.X, pady=5)
        
        # Add configuration frame
        self.config_frame = ConfigFrame(self.main_frame)
        self.config_frame.pack(fill=tk.X, pady=5)
        
        # Create status label
        self.status_label = ttk.Label(self.main_frame, text="Ready", font=('Helvetica', 10))
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Create generate button
        self.generate_button = ttk.Button(self.main_frame, text="Generate Graphics", command=self.generate_graphics)
        self.generate_button.pack(pady=10)
        
        # Initial validation
        self.validate_inputs()
    
    def validate_inputs(self):
        """Validate all inputs and update status"""
        # Validate folders and files
        folders_valid, folder_messages = self.validation_frame.validate_all()
        
        # Validate configuration
        config_valid, config_message = self.config_frame.validate()
        
        if not folders_valid or not config_valid:
            self.status_label.config(text="⚠️ Some inputs are invalid", foreground="red")
            self.generate_button.config(state="disabled")
            
            # Collect all error messages
            error_messages = []
            if not folders_valid:
                error_messages.extend(folder_messages)
            if not config_valid:
                error_messages.append(f"Configuration: {config_message}")
            
            # Show detailed error message
            error_message = "The following issues were found:\n\n" + "\n".join(error_messages)
            messagebox.showwarning("Validation Errors", error_message)
        else:
            self.status_label.config(text="✓ All inputs validated successfully", foreground="green")
            self.generate_button.config(state="normal")
        
        return folders_valid and config_valid
    
    def show_riding_confirmation(self, riding, riding_index, total_ridings):
        try:
            print(f"DEBUG GUI: Creating confirmation dialog for riding {riding['name']}")
            print(f"DEBUG GUI: Riding data: parties={len(riding['party_names'])}, candidates={len(riding['candidate_names'])}, final_results={len(riding['final_results'])}")
            dialog = RidingConfirmationDialog(self.root, riding, riding_index, total_ridings)
            result = dialog.show()
            print(f"DEBUG GUI: Confirmation dialog result: {result}")
            return result
        except Exception as e:
            import traceback
            print(f"ERROR in show_riding_confirmation: {e}")
            traceback.print_exc()
            # Return False to continue to next riding if there's an error
            messagebox.showerror("Error", f"An error occurred displaying the riding confirmation: {str(e)}\n\nContinuing to next riding.")
            return False
    
    def generate_graphics(self):
        """Generate graphics with current configuration"""
        if not self.validate_inputs():
            return
        
        try:
            config = self.config_frame.get_config()
            
            # Update status
            self.status_label.config(text="Generating graphics...", foreground="black")
            self.generate_button.config(state="disabled")
            self.root.update()
            
            # Generate graphics
            success = generate_individual_graphics(
                ridings=ridings,
                all_parties=all_parties,
                num_graphics=config['num_graphics'],
                num_selected_steps=config['num_selected_steps'],
                seatsToProcess=config['seats_in_election'],
                byelection=config['byelection'],
                callback=lambda riding, idx, total: self.show_riding_confirmation(riding, idx, total)
            )
            
            if success:
                self.status_label.config(text="✓ Graphics generated successfully", foreground="green")
            else:
                self.status_label.config(text="⚠️ Error generating graphics", foreground="red")
        except Exception as e:
            self.status_label.config(text=f"⚠️ Error: {str(e)}", foreground="red")
            messagebox.showerror("Error", f"An error occurred while generating graphics:\n\n{str(e)}")
        finally:
            self.generate_button.config(state="normal")
    
    def run(self):
        self.root.mainloop()

def main():
    app = ElectionGUI()
    app.run()

if __name__ == "__main__":
    main() 