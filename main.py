import tkinter as tk
from tkinter import filedialog
from tkinter.tix import IMAGETEXT
from PIL import Image
from package import generate_qr, breakdown_qr,add_border_to_image, cut_border_from_image

def generate_qr_button():
    data = input_text.get()
    generate_qr(data)
    breakdown_qr()
    file_path = filedialog.askopenfilename()
    add_border_to_image(file_path)
    result_label.config(text="QR code generated and processed.")

def select_image_button():
    file_path = filedialog.askopenfilename()
    cut_border_from_image(file_path)
    display_reconstructed_image()
    result_label.config(text="QR code Deciphered from the final image.")

def display_reconstructed_image():
    img = Image.open("./reconstructed_qr.jpg")
    img.show()

# Create the main window
window = tk.Tk()
window.title("QR Code Cipher")

# Left side (Cipher)
left_frame = tk.Frame(window)
left_frame.pack(side="left", padx=10)

input_label = tk.Label(left_frame, text="Enter Data:")
input_label.pack()

input_text = tk.Entry(left_frame)
input_text.pack()

generate_button = tk.Button(left_frame, text="Generate QR", command=generate_qr_button)
generate_button.pack()

# Right side (Decipher QR)
right_frame = tk.Frame(window)
right_frame.pack(side="left", padx=10)

select_image_button = tk.Button(right_frame, text="Select Image to Decipher", command=select_image_button)
select_image_button.pack()

result_label = tk.Label(right_frame)
result_label.pack()

window.mainloop()
