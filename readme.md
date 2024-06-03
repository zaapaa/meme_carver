# Meme Carver

Meme Carver is a simple python script with GUI or CLI interfaces that uses seam carving to create content-aware scale gif images.

## Usage

Download the source from GitHub, install requirements and run.

The GUI interface offers a more user-friendly way to use the carver. It allows you to select a input file, which can be a normal image or a GIF file, adjust various settings, and generate an output file.

The CLI interface is also available for use. It offers a few hardcoded options and is primarily intended for use by developers who want to automate the carver or use it in a script.
The CLI interface can be used by running the script with the path to an input image file as an argument.

## Options

### min_scale
This option specifies the minimum scale value for the seam carving operation. It is a percentage value from 0 to 1, where 0 means the image is entirely scaled down and 1 means no scaling is applied. This option is useful for preventing the carver from scaling the image too much and losing detail.

### use_prev_frame
This option allows the seam carving algorithm to use information from previous frames when carving. This can help to create smoother and more natural-looking carvings, especially when carving through regions of the image that have a lot of detail or movement. However, this option is much slower due to the inability to be multithreaded. This cannot be used when carving a gif.

### num_frames
This option specifies the number of frames to carve. When carving a gif, this option is ignored. When carving a single image, this will control how many different scale values are used in the output. A higher value of num_frames will produce a more detailed and gradual carving, but will also increase the computational cost of the operation.

### method

The method parameter controls how the image is scaled during the seam carving process. The two available methods are "linear" and "sine".

When using the linear method, the scaling will be a linear interpolation between the minimum and maximum scale values specified. This results in a uniform scaling of the image.

When using the sine method, the scaling will be a sine interpolation between the minimum and maximum scale values specified. This results in a more natural-looking scaling of the image, with the image being scaled less at the beginning of the carve, and more at the end

### shape_options
This section is for controlling the resolution of the final animation.

### shape_same
Preserves the original resolution

### shape_scale
Specify a scale factor for the final image. This can be a single floating point value to scale both the x and y axes equally, or a comma-separated value to specify a different scale factor for each axis.

### shape_resolution
Specify a custom resolution for the final image. This option takes a comma-separated pair of integers, where the first integer specifies the width and the second integer specifies the height.

### loop
Repeat the frames in reverse order at the end of the animation to create a seamless loop.

### save_frames
This option will save each frame of the animation as a separate gif file. The frames will be saved in a folder with the same name as the output file, with the frames named by their order in the animation. This can be useful for debugging or creating animations that need to be edited in a different program. Note that this option can be quite slow and may increase the total size of the output, so it is generally only used for debugging or special cases.

### gif_interval_msec
Specify the time in milliseconds between each frame in the final animation. For input GIFs, a value of 0 will preserve the original frame interval

### size_limit_kb
Not implemented
