from PIL import Image
import matplotlib.pyplot as plt
import os

# Load map image
map_img = Image.open(r"media\AWSDefcon1App\MapChart_Game_1.png")

# Directory of tiles
tiles_dir = r"AWSDefcon1App\static\AWSDefcon1App\white_image/"

def onclick(event):
    if event.xdata is None or event.ydata is None:
        return
    x, y = int(event.xdata), int(event.ydata)
    print(f"Clicked at: x={x}, y={y}")

    # Loop through tiles to find which one is non-transparent at this pixel
    for filename in os.listdir(tiles_dir):
        if not filename.endswith(".png"):
            continue
        tile_path = os.path.join(tiles_dir, filename)
        tile_img = Image.open(tile_path).convert("RGBA")
        pixel = tile_img.getpixel((x, y))
        if pixel[3] > 0:  # alpha > 0 means not transparent
            print("Clicked tile:", filename)
            break

    plt.close()  # close image after processing click

# Show the map and wait for click
fig, ax = plt.subplots()
ax.imshow(map_img)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()
