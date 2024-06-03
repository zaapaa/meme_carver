import sys
import numpy as np
import seam_carving
import os
from skimage import io, transform, util
from PIL import Image
from PIL import ImageTk
import math
import tkinter.filedialog as tk_filedialog
import tkinter as tk
import tkinter.ttk as ttk
from idlelib.tooltip import Hovertip
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor


def validate_int_positive(value: str, allow_zero: bool = False):
    if allow_zero and int(value) == 0:
        return True
    if int(value) <= 0:
        return False
    return True


def validate_float_positive(value: str, allow_zero: bool = False):
    if allow_zero and abs(float(value)) < 0.0001:
        return True
    if float(value) <= 0:
        return False
    return True


def validate_shape_scale(value: str):
    values = value.split(",")
    if len(values) == 1:
        if not validate_float_positive(values[0]):
            return False
    elif len(values) == 2:
        if not validate_float_positive(values[0]) or not validate_float_positive(values[1]):
            return False
        else:
            return True
    else:
        return False


def validate_shape_resolution(value: str):
    values = value.split(",")
    if len(values) != 2 or not validate_int_positive(values[0]) or not validate_int_positive(values[1]):
        return False
    return True


def seam_carving_meme(img: np.ndarray, scale: float, shape: Tuple[int, int]):
    """
    Carve an image to the specified scale and resolution, then resize to the
    specified shape.

    Args:
        img (np.ndarray): Input image
        scale (float): Scale factor
        shape (Tuple[int, int]): Desired output shape

    Returns:
        np.ndarray: Carved and resized image
    """
    # Calculate the new height and width of the image
    # after applying the scale factor.
    # Ensure that the new dimensions are at least 1
    new_height, new_width = int(
        img.shape[0] * scale), int(img.shape[1] * scale)
    new_height, new_width = max(new_height, 1), max(new_width, 1)

    # Convert the input image to float
    img = util.img_as_float(img)

    # Use seam carving to resize the image to the new dimensions
    # and then resize the image to the desired shape
    carved_img = seam_carving.resize(img, (new_height, new_width))
    resized_img = transform.resize(carved_img, shape)

    # Convert the resized image back to 8-bit unsigned integers
    resized_img = util.img_as_ubyte(resized_img)

    return resized_img


def load_image(path: str):
    """
    Load an image from the specified file path.

    Args:
        path (str): The path to the image file.

    Notes:
        This function uses skimage.io to open the image, and then uses the
        `black_alpha_and_remove_alpha` function to remove alpha
        channels and set transparent pixels to black.

        If the image is a GIF, it loads the image frames into a list
        and applies the `black_alpha_and_remove_alpha` function to each frame.

        The duration of GIFs is stored in the `input_gif_interval_msec`
        global variable.
    """
    global input_image
    global input_gif_interval_msec

    img = io.imread(path)
    imgPillow = Image.open(path)
    input_gif_interval_msec = getattr(imgPillow.info, "duration", 50)

    if not path.endswith(".gif"):
        input_image = black_alpha_and_remove_alpha(img)
    else:
        input_image = list([black_alpha_and_remove_alpha(img[i])
                           for i in range(len(img))])


def black_alpha_and_remove_alpha(img: np.ndarray) -> np.ndarray:
    """
    Remove alpha channel from an image and set transparent pixels to black.

    Args:
        img (np.ndarray): 3D NumPy array representing an image, with shape
            (height, width, channels), where channels is 3 for RGB or 4 for RGBA.

    Returns:
        np.ndarray: A 3D NumPy array representing the image with the alpha
            channel removed and transparent pixels set to black (i.e. RGB values
            of (0, 0, 0)).

    Notes:
        If the image has an alpha channel (i.e. channels is 4), this function
        sets the RGB values of transparent pixels (i.e. pixels with alpha
        values of 0) to (0, 0, 0) and returns the resulting image with the
        alpha channel removed.
    """
    if img.shape[2] == 4:
        # set RGB values of transparent pixels to 0
        img[img[..., 3] == 0, :3] = 0
    return img[..., :3]


gif_playing_input = False
gif_playing_output = False
gif_animation_id_input = None
gif_animation_id_output = None
input_image: np.ndarray = None
input_gif_interval_msec = 50


def gui():

    def browse_file(canvas):
        global input_image
        stop_gif("input")
        file_path = tk_filedialog.askopenfilename(filetypes=[(
            "Image Files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.tiff;*.tif;*.jfif;*.webp;*.avif;*.heif;*.heic;*.apng")], initialdir=os.getcwd())
        if file_path and os.path.exists(file_path):
            textbox_input_path.delete(0, tk.END)
            textbox_input_path.insert(tk.END, file_path)
            load_image(file_path)
            preview_image(canvas, input_image,
                          os.path.splitext(file_path)[1] == ".gif")

    def preview_image(canvas: tk.Canvas, img: np.ndarray | List[np.ndarray], gif: bool = False):
        """
        Display the image in the canvas as a preview.

        Args:
            canvas (Canvas): The canvas to display the image in.
            img (np.ndarray or List[np.ndarray]): The image to display.
                If a single image is provided, it will be displayed as a static
                image. If a list of images is provided, it will be displayed as
                an animated GIF.

            gif (bool): Whether the image is a GIF or not. Defaults to False.

        Returns:
            None
        """
        print(f"{gif=}")
        print(f"{type(img)=}")
        input_image_list = []
        if not gif:
            print(f"static image")
            input_image_list = [ImageTk.PhotoImage(Image.fromarray(img))]
            
        else:
            print(f"animated image")
            input_image_list = [ImageTk.PhotoImage(
                Image.fromarray(x)) for x in img]
        show_image(canvas, input_image_list, 0, input_gif_interval_msec, True)

    def update_canvas(canvas: tk.Canvas, img: ImageTk.PhotoImage):
        """
        Deletes all items on the canvas, sets the canvas's width and height
        to match the image, and then creates a new image on the canvas with
        the given image.

        Args:
            canvas (Canvas): The canvas to update.
            img (ImageTk.ImageTk.PhotoImage): The image to display on the canvas.
        """
        canvas.delete("all")
        canvas["width"] = img.width()
        canvas["height"] = img.height()
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.update()

    def show_image(canvas: tk.Canvas, imgs: List[ImageTk.PhotoImage], i: int, gif_interval_msec: int, start: bool = False):
        global gif_playing_input
        global gif_playing_output
        global gif_animation_id_input
        global gif_animation_id_output

        which = getattr(canvas, "type", None)
        if which == "input":
            if not gif_playing_input:
                if start:
                    gif_playing_input = True
                else:
                    return
            elif start:
                root.after_cancel(gif_animation_id_input)
        elif which == "output":
            if not gif_playing_output:
                if start:
                    gif_playing_output = True
                else:
                    return
            elif start:
                root.after_cancel(gif_animation_id_output)
        else:
            return
        if len(imgs) == 0:
            return
        update_canvas(canvas, imgs[i])

        i = (i+1) % len(imgs)
        id = root.after(gif_interval_msec, lambda: show_image(
            canvas, imgs, i, gif_interval_msec))
        if which == "input":
            gif_animation_id_input = id
        elif which == "output":
            gif_animation_id_output = id

    def stop_gif(which: str):
        global gif_playing_input
        global gif_playing_output
        if which == "input":
            gif_playing_input = False
        elif which == "output":
            gif_playing_output = False
    
    # Randomly change the icon of the window every 16 milliseconds
    def randomize_icon(root: tk.Tk):
        # Create a 16x16x3 numpy array of random unsigned 8-bit integers
        # representing a pixel array
        icon = np.ndarray((16, 16, 3), dtype=np.uint8)
        for i in range(16):
            for j in range(16):
                # Assign a random RGB value to each pixel
                icon[i, j] = np.random.randint(0, 256, 3)
        # Convert the numpy array to an Image object
        icon = Image.fromarray(icon)
        # Set the icon of the window to the new image
        root.iconphoto(False, ImageTk.PhotoImage(icon))
        # Schedule this function to run again after 16 milliseconds
        root.after(16, lambda: randomize_icon(root))

    root = tk.Tk()
    root.title("Meme Carver")
    root.resizable(False, False)
    randomize_icon(root)


    min_scale = tk.DoubleVar(value=0.0)
    use_prev = tk.BooleanVar()
    frames = tk.IntVar(value=40)
    method = tk.IntVar(value=2)
    shape_options = tk.StringVar(value="Same")
    shape_scale = tk.DoubleVar(value=1.0)
    shape_resolution = tk.StringVar(value="64,64")
    loop = tk.BooleanVar(value=True)
    save_frames = tk.BooleanVar(value=False)
    gif_interval_msec = tk.IntVar(value=50)
    size_limit_kb = tk.IntVar(value=0)

    frame_left = ttk.Frame(root)
    frame_left.pack(side=tk.LEFT, anchor=tk.NW)
    frame_right = ttk.Frame(root)
    frame_right.pack(side=tk.RIGHT, anchor=tk.NW)
    frame_input_path = ttk.Frame(frame_left)
    frame_input_path.pack(side=tk.TOP, pady=10, anchor=tk.NW)
    textbox_input_path = ttk.Entry(frame_input_path, width=50)
    textbox_input_path.insert(0, "Enter image path")
    textbox_input_path.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    input_canvas = tk.Canvas(frame_right, width=0, height=0)
    setattr(input_canvas, "type", "input")
    output_canvas = tk.Canvas(frame_right, width=0, height=0)
    setattr(output_canvas, "type", "output")
    browsebutton = ttk.Button(frame_input_path, text="Browse", command=lambda: browse_file(
        input_canvas))
    browsebutton.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(browsebutton, "Browse for an input image.", hover_delay=500)

    frame_options = ttk.Frame(frame_left)
    frame_options.pack(pady=10, anchor=tk.NW)

    ttk.Label(frame_options, text="Min scale:").grid(
        row=0, column=0, padx=5, pady=5, sticky=tk.W)
    scale_entry = ttk.Entry(frame_options, textvariable=min_scale, width=5)
    scale_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(
        scale_entry, "The image will be processed from full size to this scale.", hover_delay=500)

    ttk.Label(frame_options, text="Recursive").grid(
        row=1, column=0, padx=5, pady=5, sticky=tk.W)
    recursive_button = ttk.Checkbutton(frame_options, variable=use_prev)
    recursive_button.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(recursive_button, 'Enable recursive processing.\nThis will make the algorithm use previous frame for input instead of the original image.\nDisables multithreading.', hover_delay=500)

    ttk.Label(frame_options, text="Number of frames:").grid(
        row=2, column=0, padx=5, pady=5, sticky=tk.W)
    frames_entry = ttk.Entry(frame_options, textvariable=frames, width=5)
    frames_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(frames_entry, "Number of frames to generate.", hover_delay=500)

    ttk.Label(frame_options, text="Method:").grid(
        row=3, column=0, padx=5, pady=5, sticky=tk.W)
    radio_linear = ttk.Radiobutton(
        frame_options, text="linear", variable=method, value=1)
    radio_linear.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(radio_linear,
             "Seam carving will scale the image linearly.", hover_delay=500)
    radio_sine = ttk.Radiobutton(
        frame_options, text="sine", variable=method, value=2)
    radio_sine.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
    Hovertip(radio_sine, "Seam carving will scale the image with a sine wave, resulting in smaller effect in the beginning and larger effect in the end.", hover_delay=500)

    shape_label = ttk.Label(frame_options, text="Resize output:")
    shape_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    Hovertip(shape_label, "Resize the output image.", hover_delay=500)
    radio_same = ttk.Radiobutton(
        frame_options, text="No", variable=shape_options, value="Same")
    radio_same.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(radio_same, "Maintain input image resolution", hover_delay=500)
    radio_scale = ttk.Radiobutton(
        frame_options, text="Scale", variable=shape_options, value="Scale")
    radio_scale.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(radio_scale, "Scale the output image by a value.\nCan be a single float or two floats separated by a comma.", hover_delay=500)
    radio_resolution = ttk.Radiobutton(
        frame_options, text="Resolution", variable=shape_options, value="Resolution")
    radio_resolution.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(radio_resolution, "Scale the output image to a specific resolution.\nMust be two integers separated by a comma.", hover_delay=500)

    shape_same_label = ttk.Label(frame_options, text="")
    shape_same_label.grid(row=4, column=2, padx=5, pady=6, sticky=tk.W)

    shape_scale_label = ttk.Label(frame_options, text="Scale:")
    shape_scale_label.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
    shape_scale_label.grid_remove()
    shape_scale_entry = ttk.Entry(
        frame_options, textvariable=shape_scale, width=5)
    shape_scale_entry.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
    shape_scale_entry.grid_remove()
    Hovertip(shape_scale_entry, "Scale the output image by a value.\nCan be a single float or two floats separated by a comma.", hover_delay=500)

    shape_resolution_label = ttk.Label(frame_options, text="Resolution:")
    shape_resolution_label.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
    shape_resolution_label.grid_remove()
    shape_resolution_entry = ttk.Entry(
        frame_options, textvariable=shape_resolution, width=9)
    shape_resolution_entry.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
    shape_resolution_entry.grid_remove()
    Hovertip(shape_resolution_entry,
             "Scale the output image to a specific resolution.\nMust be two integers separated by a comma.", hover_delay=500)

    def toggle_shape_options(shape_options, shape_scale_label, shape_scale_entry, shape_resolution_label, shape_resolution_entry):
        if shape_options.get() == "Scale":
            shape_same_label.grid_remove()
            # shape_scale_label.grid()
            shape_scale_entry.grid()
            shape_resolution_label.grid_remove()
            shape_resolution_entry.grid_remove()
        elif shape_options.get() == "Resolution":
            shape_same_label.grid_remove()
            shape_scale_label.grid_remove()
            shape_scale_entry.grid_remove()
            # shape_resolution_label.grid()
            shape_resolution_entry.grid()
        elif shape_options.get() == "Same":
            shape_scale_label.grid_remove()
            shape_scale_entry.grid_remove()
            shape_resolution_label.grid_remove()
            shape_resolution_entry.grid_remove()
            # shape_same_label.grid()

    shape_options.trace_add('write', lambda *args: toggle_shape_options(shape_options,
                                                                        shape_scale_label, shape_scale_entry, shape_resolution_label, shape_resolution_entry))

    ttk.Label(frame_options, text="Loop").grid(
        row=7, column=0, padx=5, pady=5, sticky=tk.W)
    check_loop = ttk.Checkbutton(frame_options, variable=loop)
    check_loop.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(check_loop, "Create seamless loop by appending frames in reverse order", hover_delay=500)

    ttk.Label(frame_options, text="Save all frames").grid(
        row=8, column=0, padx=5, pady=5, sticky=tk.W)
    check_save_frames = ttk.Checkbutton(frame_options, variable=save_frames)
    check_save_frames.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(check_save_frames, "Save all frames in folder", hover_delay=500)

    ttk.Label(frame_options, text="GIF interval (msec):").grid(
        row=9, column=0, padx=5, pady=5, sticky=tk.W)
    entry_interval = ttk.Entry(frame_options, textvariable=gif_interval_msec, width=5)
    entry_interval.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(entry_interval, "GIF interval in milliseconds", hover_delay=500)

    ttk.Label(frame_options, text="Size limit (KB):").grid(
        row=10, column=0, padx=5, pady=5, sticky=tk.W)
    entry_size_limit = ttk.Entry(frame_options, textvariable=size_limit_kb, width=5)
    entry_size_limit.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)
    Hovertip(entry_size_limit, "Size limit in KB", hover_delay=500)


    def submit():
        stop_gif("output")
        path = textbox_input_path.get()
        file, ext = os.path.splitext(path)

        if not path:
            print("Path is empty")
            return

        if not os.path.exists(path) or not os.path.isfile(path):
            print("Path does not exist")
            return

        if not validate_float_positive(min_scale.get(), True):
            print("Min scale must be a zero or a positive float")
            return

        if not validate_int_positive(frames.get()):
            print("Frames must be a positive integer")
            return

        if not validate_int_positive(gif_interval_msec.get(), True if ext.lower() == ".gif" else False):
            print("GIF interval must be a positive integer")
            return

        if shape_options.get() == "Scale" and not validate_shape_scale(shape_scale.get()):
            print("Shape scale must be a positive float")
            return

        if shape_options.get() == "Resolution" and not validate_shape_resolution(shape_resolution.get()):
            print("Shape resolution must be a comma-separated pair of positive integers")
            return

        # print(path)
        if ext.lower() == ".gif" and use_prev.get():
            print("GIF cannot be used with 'use prev' option")
            return

        shape = None
        if shape_options.get() == "Scale":
            shape = shape_scale
        elif shape_options.get() == "Resolution":
            shape = shape_resolution
        interval = gif_interval_msec.get() if gif_interval_msec.get(
        ) != 0 else input_gif_interval_msec

        imgs = process_frames(path, min_scale.get(), use_prev.get(), int(frames.get()), int(method.get()), shape, shape_options.get(
        ), loop.get(), save_frames.get(), interval, int(size_limit_kb.get()))

        stop_gif("output")
        show_image(output_canvas, imgs, 0, interval, True)

    submit_button = ttk.Button(frame_left, text="Carve!", command=submit)
    submit_button.pack(pady=10)
    input_canvas.pack(pady=10)
    output_canvas.pack(pady=10)
    root.mainloop()


def commandline():
    input_image_path = sys.argv[1]
    min_scale = 0.0
    use_prev = False
    frames = 40
    method = 2
    shape = (512, 854)
    loop = True
    save_frames = False
    gif_interval_msec = 50
    process_frames(input_image_path, min_scale, use_prev, frames, method,
                   shape, None, loop, save_frames, gif_interval_msec, 0)


def process_frames(input_image_path: str, min_scale: float, use_prev: bool, num_frames: int, method: int, shape: Tuple[int, int], shape_options: str, loop: bool, save_frames: bool, gif_interval_msec: int, size_limit_kb=0):
    global input_image
    file, ext = os.path.splitext(input_image_path)
    if not os.path.exists(file):
        os.mkdir(file)

    resolution = None
    if input_image is None:
        load_image(input_image_path)
    if ext.lower() == ".gif":
        num_frames = len(input_image)
        if gif_interval_msec == 0:
            gif_interval_msec = input_gif_interval_msec
        resolution = input_image[0].shape[:2]
    else:
        resolution = input_image.shape[:2]

    if shape_options == "Scale":
        values = shape.get().split(",")
        if len(values) == 2:
            values = [values[0], values[0]]
        resolution = tuple(int(values[i]*resolution[i]) for i in range(2))
    elif shape_options == "Resolution":
        resolution = tuple(int(x) for x in shape.get().split(","))
    elif shape is not None:
        resolution = shape

    scales = False

    match method:
        case 1:
            scales = list(np.arange(1, min_scale, -(1-min_scale)/num_frames))
        case 2:
            scales = [min_scale + (1-min_scale)*math.cos(x) for x in np.arange(
                0, math.pi/2, (math.pi/2)/num_frames)]

    # print(f"{method=}, {scales=}")
    imgs = []

    if not use_prev:
        print(
            f"processing {num_frames} frames with {method=}, {shape=}, {loop=}, {save_frames=}, {gif_interval_msec=} in concurrent.futures")
        imgs = multiprocess_frames(
            num_frames, ext, input_image, resolution, scales)
    else:
        for i in range(num_frames):
            scale = scales[i]
            # print(f"{scale=}")

            # Load the image
            if len(imgs) == 0:
                img = input_image
            elif ext.lower() == ".gif":
                img = input_image[i]
            else:
                img = np.asarray(imgs[-1])

            carved_img = seam_carving_meme(np.asarray(img), scale, resolution)
            imgs.append(Image.fromarray(carved_img))

    if save_frames:
        for i in range(len(imgs)):
            output_image_path = os.path.join(file, f"out_{i}{ext}")
            io.imsave(output_image_path, np.asarray(imgs[i]))

    output_gif_path = os.path.join(
        os.getcwd(), file, f"{file}_S{min_scale}_F{num_frames}_M{method}_R{resolution[0]}x{resolution[1]}")
    print(f"{output_gif_path=}, {file=}, {ext=}, {os.getcwd()=}")
    if use_prev:
        output_gif_path += "_(prev)"
    final_frames = imgs[1:]
    if loop:
        output_gif_path += "_(loop)"
        final_frames += imgs[-2:0:-1]
    output_gif_path += ".gif"
    imgs[0].save(output_gif_path, save_all=True, append_images=final_frames,
                 duration=gif_interval_msec, loop=0, optimize=True)
    print(f"saved to {output_gif_path}")
    return list([ImageTk.PhotoImage(image=img) for img in imgs])


def multiprocess_frames(num_frames: int, ext: str, input_img: np.ndarray, resolution: Tuple[int, int], scales: List[float]):
    """
    This function runs seam_carving_meme in parallel using concurrent.futures
    """
    # check for invalid inputs
    if input_img is None:
        raise ValueError("input_img cannot be None")
    if resolution is None:
        raise ValueError("resolution cannot be None")
    if scales is None:
        raise ValueError("scales cannot be None")
    if len(scales) != num_frames:
        raise ValueError("len(scales) must be equal to frames")

    # create an empty list to store processed frames
    processed_frames = []

    # use ThreadPoolExecutor to run seam_carving_meme in parallel
    # The number of workers is set to the number of frames
    with ThreadPoolExecutor(max_workers=num_frames) as executor:
        # If the input is a gif, submit seam_carving_meme for each frame
        if ext.lower() == ".gif":
            futures = [executor.submit(
                seam_carving_meme, input_img[i], scales[i], resolution) for i in range(len(scales))]
        # If the input is not a gif, submit seam_carving_meme for each scale
        else:
            futures = [executor.submit(
                seam_carving_meme, input_img, scale, resolution) for scale in scales]
        # wait for all the futures to complete and store the results in processed_frames
        processed_frames = [future.result() for future in futures]

    # convert the processed frames to PIL images
    processed_frames = list([Image.fromarray(img) for img in processed_frames])
    # return the processed frames
    return processed_frames

def main():
    if len(sys.argv) < 2:
        gui()
        exit()
    else:
        commandline()


if __name__ == "__main__":
    main()
