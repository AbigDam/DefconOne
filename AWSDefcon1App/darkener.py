from PIL import Image
import os

def darken_images_in_folder(folder_path):
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            # Open the image file``
            file_path = os.path.join(folder_path, filename)
            with Image.open(file_path) as img:
                # Convert image to RGBA if not already
                img = img.convert("RGBA")
                
                # Get the data of the image
                data = img.getdata()
                
                # Replace white pixels with black
                new_data = []
                for item in data:
                    # Check if the pixel is white
                    if item[:3] == (255, 255, 255):  # RGB for white
                        new_data.append((0, 0, 0, item[3]))  # Replace with black, keep alpha
                    else:
                        new_data.append(item)
                
                # Update the image with new data
                img.putdata(new_data)
                
                # Save the modified image, overwriting the original
                img.save(file_path)

# Example usage
folder_path = "AWSDefcon1App\static\AWSDefcon1App\white_image"  # Replace with the path to your folder
darken_images_in_folder(folder_path)
