# Meme Carver

Meme Carver is a simple python script with GUI or CLI interfaces that uses seam carving to create content-aware scale gif images.

## Usage

Download the source from GitHub, install requirements and run.

The GUI interface offers a more user-friendly way to use the carver. It allows you to select a input file, which can be a normal image or a GIF file, adjust various settings, and generate an output file.

The CLI interface is also available for use. It offers a few hardcoded options and is primarily intended for use by developers who want to automate the carver or use it in a script.
The CLI interface can be used by running the script with the path to an input image file as an argument.

## Options

### Min scale (min_scale)
This option specifies the minimum scale value for the seam carving operation. It is a percentage value from 0 to 1, where 0 means the image is entirely scaled down and 1 means no scaling is applied. This option is useful for preventing the carver from scaling the image too much and losing detail.

### Recursive (use_prev_frame)
This option allows the seam carving algorithm to use information from previous frames when carving. This can help to create smoother and more natural-looking carvings, especially when carving through regions of the image that have a lot of detail or movement. However, this option is much slower due to the inability to be multithreaded. This cannot be used when carving a gif.

### Number of frames (num_frames)
This option specifies the number of frames to carve. When carving a gif, this option is ignored. When carving a single image, this will control how many different scale values are used in the output. A higher value of num_frames will produce a more detailed and gradual carving, but will also increase the computational cost of the operation.

### Method (method)

The method parameter controls how the image is scaled during the seam carving process. The two available methods are "linear" and "sine".

When using the linear method, the scaling will be a linear interpolation between the minimum and maximum scale values specified. This results in a uniform scaling of the image.

When using the sine method, the scaling will be a sine interpolation between the minimum and maximum scale values specified. This results in a more natural-looking scaling of the image, with the image being scaled less at the beginning of the carve, and more at the end

### Resize output (shape_options)
This section is for controlling the resolution of the final animation.

### No (shape_same)
Preserves the original resolution

### Scale (shape_scale)
Specify a scale factor for the final image. This can be a single floating point value to scale both the x and y axes equally, or a comma-separated value to specify a different scale factor for each axis.

### Resolution (shape_resolution)
Specify a custom resolution for the final image. This option takes a comma-separated pair of integers, where the first integer specifies the width and the second integer specifies the height.

### Loop (loop)
Repeat the frames in reverse order at the end of the animation to create a seamless loop.

### Save all frames (save_frames)
This option will save each frame of the animation as a separate gif file. The frames will be saved in a folder with the same name as the output file, with the frames named by their order in the animation. This can be useful for debugging or creating animations that need to be edited in a different program. Note that this option can be quite slow and may increase the total size of the output, so it is generally only used for debugging or special cases.

### GIF interval (msec) (gif_interval_msec)
Specify the time in milliseconds between each frame in the final animation. For input GIFs, a value of 0 will preserve the original frame interval.

### size_limit_kb
Not implemented

## Examples

| Input | Method: linear | Method: sine |
|-----------|-----------|-----------|
| ![copiums](https://github.com/zaapaa/meme_carver/assets/24585685/39b93156-79a2-4683-863f-bccf03f34b6b)    | ![copiums_F40_M1_S80x80](https://github.com/zaapaa/meme_carver/assets/24585685/cdcf7fd6-c555-4951-b09e-437e77bc7379)    | ![copiums_F40_M2_S80x80](https://github.com/zaapaa/meme_carver/assets/24585685/4f73ed6a-4eb3-4115-b0b8-b3253b94034f)    |

| Input | Output |
|-----------|-----------|
| ![jerry](https://github.com/zaapaa/meme_carver/assets/24585685/66c8a341-ae88-4445-b2a1-62b474038b10)    | ![jerry](https://github.com/zaapaa/meme_carver/assets/24585685/c8083b5a-2113-4401-abb5-a3613a69e346)    |

| Input | Loop: off | Loop: on |
|-----------|-----------|-----------|
| ![myotis2](https://github.com/zaapaa/meme_carver/assets/24585685/7f313775-e961-4e35-a582-65b23b8f6201)    | ![myotis2_S0 0_F40_M2_R107x112](https://github.com/zaapaa/meme_carver/assets/24585685/9ce673e6-9a2a-438f-bd5d-99cc73ca732b)    | ![myotis2_S0 0_F40_M2_R107x112_(loop)](https://github.com/zaapaa/meme_carver/assets/24585685/4dede915-bf8f-4c0b-bfca-7a60e18bdb5a)    |

| GIF Input | Min scale 0.0 | Min scale 0.2 | Min scale 0.4 |
|-----------|-----------|-----------|-----------|
| ![869896923237220423](https://github.com/zaapaa/meme_carver/assets/24585685/e9630076-1598-4fb0-a85b-fc2d30b8f09d)    | ![869896923237220423_S0 0_F90_M1_R44x44](https://github.com/zaapaa/meme_carver/assets/24585685/845806a7-1d0a-4025-86f6-caad235abf40)    | ![869896923237220423_S0 2_F90_M1_R44x44](https://github.com/zaapaa/meme_carver/assets/24585685/a561e255-ceff-4900-882c-4ad385ada245)    | ![869896923237220423_S0 4_F90_M1_R44x44](https://github.com/zaapaa/meme_carver/assets/24585685/0df394f0-d96d-4d87-b2b6-6eeeda70884f)    |

| GIF Input | Output |
|-----------|-----------|
| ![1638380881296](https://github.com/zaapaa/meme_carver/assets/24585685/fdf1f522-05ee-4e40-a0df-7e647f6f1bb3)    | ![1638380881296_S0 2_F95_M2_R180x240](https://github.com/zaapaa/meme_carver/assets/24585685/16b549f0-ddc4-45d1-9492-e57e32ab66ab)    |
