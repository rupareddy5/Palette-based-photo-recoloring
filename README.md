## Palette-based Photo recoloring

A python implemenation of the research paper [[1](#paper)]




**To Run:**

#### Install required packages

```shell
sudo apt install qt5-default
pip install opencv-python-headless
pip install imageio
python3 -m pip install Pillow
pip install multiprocess
```




#### To run an example

```shell
python3 GUI.py
```
This opens the UI. Select an image by clicking on "Upload image" button. 
You can now click on any of the palette blocks and select a colour of your choice to recolour your image.
 


### Sample Outputs
<!-- |     Input |      Output |                
|------------------|--------------|
|![Emma](outputs/emma.jpeg) | ![Emma_edited](outputs/emma_edited.jpeg)|
|![Himalaya](outputs/himalaya.jpeg) | ![himalaya_edited](outputs/himalaya_edited.jpeg) |
| ![Apple](outputs/apple.jpeg) | ![apple_edited](outputs/apple_edited.jpeg) | -->
[Inputs](https://drive.google.com/drive/folders/1BNSl7vNzKOJFU5AZ3JRklm24x-zWPCax?usp=sharing)
[Outputs](https://drive.google.com/drive/folders/1fgwEwZJnEyduFgtGiZ4GJxV2ICvyk2WG?usp=sharing)


##### paper

[1] Palette-based Photo Recoloring. [Link to Paper](https://gfx.cs.princeton.edu/pubs/Chang_2015_PPR/chang2015-palette_small.pdf)
