import threading
import os
import requests
import yt_dlp
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, ttk
from PIL import Image, ImageDraw, ImageFont



# Function to split download
def download_part(url, start, end, part_number, filename, progress_var, part_size, num_parts):
    headers = {"Range": f"bytes={start}-{end}"}
    response = requests.get(url, headers=headers, stream=True)
    
    with open(f"{filename}_part{part_number}", "wb") as f:
        f.write(response.content)
    
    # Update progress bar for each part
    progress_var.set(progress_var.get() + (1 / num_parts) * 100)

def split_download(url, filename, num_parts=4, progress_var=None):
    response = requests.head(url)
    file_size = int(response.headers['content-length'])

    part_size = file_size // num_parts
    threads = []

    for i in range(num_parts):
        start = i * part_size
        end = (i + 1) * part_size - 1 if i != num_parts - 1 else file_size
        thread = threading.Thread(target=download_part, args=(url, start, end, i, filename, progress_var, part_size, num_parts))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    with open(filename, "wb") as f:
        for i in range(num_parts):
            with open(f"{filename}_part{i}", "rb") as part_file:
                f.write(part_file.read())
            os.remove(f"{filename}_part{i}")

# Function to download YouTube video
def download_video(video_url, save_path, progress_var):
    ydl_opts = {'outtmpl': f'{save_path}/%(title)s.%(ext)s'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    # تحديث شريط التقدم عند اكتمال التحميل
    progress_var.set(100)

# Function to start file download
def start_file_download(url, save_path, progress_var):
    split_download(url, save_path, num_parts=4, progress_var=progress_var)

# Function to browse save location
def browse_save_location(entry):
    folder_selected = filedialog.askdirectory()
    entry.set(folder_selected)

# Function to handle download button click
def handle_download():
    url = url_entry.get()
    save_location = save_path.get()
    
    if url and save_location:
        progress_var.set(0)  # Reset progress bar
        if "youtube.com" in url or "youtu.be" in url:
            threading.Thread(target=download_video, args=(url, save_location, progress_var)).start()
        else:
            file_name = os.path.join(save_location, url.split("/")[-1])
            threading.Thread(target=start_file_download, args=(url, file_name, progress_var)).start()

# Tkinter GUI setup
root = Tk()
root.title("Python Download Manager")

# URL Input
Label(root, text="Enter URL:").grid(row=0, column=0, padx=10, pady=10)
url_entry = Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Save Location
Label(root, text="Save to:").grid(row=1, column=0, padx=10, pady=10)
save_path = StringVar()
save_entry = Entry(root, textvariable=save_path, width=50)
save_entry.grid(row=1, column=1, padx=10, pady=10)
Button(root, text="Browse", command=lambda: browse_save_location(save_path)).grid(row=1, column=2, padx=10, pady=10)

# Progress Bar
progress_var = StringVar(value=0)
progress_bar = ttk.Progressbar(root, length=400, variable=progress_var)
progress_bar.grid(row=2, column=1, padx=10, pady=10)

# Download Button
Button(root, text="Download", command=handle_download).grid(row=3, column=1, padx=10, pady=10)

# Start Tkinter loop
root.mainloop()
