import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Watermark Adder")
        self.root.geometry("1000x700")
        self.root.config(bg="#f5f5f5")

        # Attributes
        self.main_image_path = None
        self.watermark_image_path = None
        self.main_image = None
        self.watermarked_image = None
        self.opacity = 128  # default opacity
        self.text_watermark = ""
        self.watermark_mode = tk.StringVar(value="text")  # 'text' or 'image'
        self.text_color = "#ffffff"

        # ---------------------------
        # Title Label
        # ---------------------------
        title = tk.Label(
            root, text="Watermark Adder",
            font=("Helvetica", 24, "bold"),
            bg="#f5f5f5", fg="#333"
        )
        title.pack(pady=15)

        # ---------------------------
        # Frame for Controls
        # ---------------------------
        control_frame = tk.Frame(root, bg="#f5f5f5")
        control_frame.pack(pady=20)

        # Buttons
        tk.Button(control_frame, text="Upload Image(s)", command=self.upload_images,
                  bg="#4CAF50", fg="white", font=("Arial", 12), width=20).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(control_frame, text="Upload Watermark Logo", command=self.upload_watermark,
                  bg="#2196F3", fg="white", font=("Arial", 12), width=20).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(control_frame, text="Apply Watermark", command=self.apply_watermark,
                  bg="#FFC107", fg="black", font=("Arial", 12), width=20).grid(row=0, column=2, padx=10, pady=10)
        tk.Button(control_frame, text="Save Image(s)", command=self.save_images,
                  bg="#E91E63", fg="white", font=("Arial", 12), width=20).grid(row=0, column=3, padx=10, pady=10)

        # ---------------------------
        # Opacity Slider
        # ---------------------------
        opacity_label = tk.Label(root, text="Watermark Opacity", font=("Arial", 12), bg="#f5f5f5")
        opacity_label.pack()
        self.opacity_slider = ttk.Scale(root, from_=0, to=255, orient="horizontal",
                                        command=self.update_opacity)
        self.opacity_slider.set(self.opacity)
        self.opacity_slider.pack(pady=5)

        # ---------------------------
        # Live Preview Label
        # ---------------------------
        preview_frame = tk.Frame(root, bg="#eaeaea", bd=2, relief="ridge")
        preview_frame.pack(pady=20, fill="both", expand=True)

        preview_label_title = tk.Label(preview_frame, text="Live Preview", font=("Arial", 14, "bold"), bg="#eaeaea")
        preview_label_title.pack(pady=10)

        # The critical part — define preview_label early!
        self.preview_label = tk.Label(preview_frame, bg="#ccc")
        self.preview_label.pack(expand=True)

        # ---------------------------
        # Status Label
        # ---------------------------
        self.status_label = tk.Label(root, text="Ready", bg="#f5f5f5", font=("Arial", 10), fg="#555")
        self.status_label.pack(pady=5)

    # ---------------------------
    # Core Functions
    # ---------------------------

    def upload_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Image(s)",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if paths:
            self.image_paths = list(paths)
            self.main_image_path = self.image_paths[0]
            self.main_image = Image.open(self.main_image_path)
            self.update_preview(self.main_image)
            self.status_label.config(text=f"Loaded {len(self.image_paths)} image(s).")

    def upload_watermark(self):
        path = filedialog.askopenfilename(
            title="Select Watermark Logo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if path:
            self.watermark_image_path = path
            self.status_label.config(text=f"Watermark selected: {os.path.basename(path)}")

    def update_opacity(self, val):
        self.opacity = int(float(val))
        self.status_label.config(text=f"Opacity set to {self.opacity}")
        if self.main_image:
            self.apply_watermark(preview_only=True)

    def apply_watermark(self, preview_only=False):
        if not self.main_image_path:
            messagebox.showwarning("No Image", "Please upload an image first.")
            return

        if not self.watermark_image_path:
            messagebox.showwarning("No Watermark", "Please upload a watermark logo.")
            return

        watermark = Image.open(self.watermark_image_path).convert("RGBA")
        watermark = watermark.resize((150, 150))

        # Adjust transparency
        alpha = watermark.split()[3]
        alpha = alpha.point(lambda p: p * self.opacity / 255)
        watermark.putalpha(alpha)

        # Apply watermark to all selected images
        for path in getattr(self, 'image_paths', [self.main_image_path]):
            img = Image.open(path).convert("RGBA")
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            position = (img.width - watermark.width - 20, img.height - watermark.height - 20)
            layer.paste(watermark, position, watermark)
            watermarked = Image.alpha_composite(img, layer)
            self.watermarked_image = watermarked

            if preview_only:
                self.update_preview(watermarked)
                return

        self.update_preview(watermarked)
        self.status_label.config(text="Watermark applied successfully!")

    def save_images(self):
        if not self.watermarked_image:
            messagebox.showinfo("No Image", "Please apply watermark first.")
            return

        save_dir = filedialog.askdirectory(title="Select Folder to Save Watermarked Images")
        if not save_dir:
            return

        for i, path in enumerate(getattr(self, 'image_paths', [self.main_image_path])):
            filename = os.path.basename(path)
            save_path = os.path.join(save_dir, f"watermarked_{filename}")

            # Convert if saving to JPEG
            if save_path.lower().endswith((".jpg", ".jpeg")):
                rgb_image = self.watermarked_image.convert("RGB")
                rgb_image.save(save_path)
            else:
                self.watermarked_image.save(save_path)

    def update_preview(self, img):
        """Show the live preview of the processed image"""
        img_copy = img.copy()
        img_copy.thumbnail((600, 400))
        preview_img = ImageTk.PhotoImage(img_copy)
        self.preview_label.config(image=preview_img)
        self.preview_label.image = preview_img

    # ---------------------------
    # Drag-and-Drop Events
    # ---------------------------
    def drag_event(self, event):
        self.status_label.config(text="Drag detected...")

    def drop_event(self, event):
        # This part can be customized using tkdnd library for true drag/drop support
        self.status_label.config(text="Drop event triggered (requires tkdnd on some OS).")


# ---------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
