"""
test_gui.py: Quick test to verify GUI can launch without API key.

This script tests that all GUI components work without making API calls.
"""

import customtkinter as ctk


def test_gui_launch():
    """Test that the GUI window can be created and displayed."""
    print("\n" + "="*60)
    print("Testing GUI Components")
    print("="*60 + "\n")
    
    try:
        # Test CustomTkinter
        print("✅ CustomTkinter imported successfully")
        
        # Create test window
        print("Creating test window...")
        root = ctk.CTk()
        root.title("GUI Test")
        root.geometry("400x300")
        
        # Test dark mode
        ctk.set_appearance_mode("dark")
        print("✅ Dark theme applied")
        
        # Test button creation
        button = ctk.CTkButton(
            root,
            text="🎤",
            font=ctk.CTkFont(size=48),
            width=150,
            height=150,
            corner_radius=75,
            border_width=5,
            border_color="gray"
        )
        button.pack(pady=20)
        print("✅ Circular button created")
        
        # Test textbox
        textbox = ctk.CTkTextbox(root, height=100)
        textbox.pack(pady=10, padx=20, fill="both", expand=True)
        textbox.insert("1.0", "Test conversation log\n")
        print("✅ Textbox created")
        
        # Test label
        label = ctk.CTkLabel(root, text="Test Status", font=ctk.CTkFont(size=14))
        label.pack(pady=10)
        print("✅ Label created")
        
        print("\n" + "="*60)
        print("GUI Test Complete!")
        print("="*60)
        print("\nThe test window will close in 3 seconds...")
        print("If you see a GUI window, everything is working!\n")
        
        # Auto-close after 3 seconds
        root.after(3000, root.quit)
        root.mainloop()
        
        print("✅ GUI test successful!\n")
        return True
    
    except Exception as e:
        print(f"❌ GUI test failed: {e}\n")
        return False


if __name__ == "__main__":
    test_gui_launch()
