import os
from PIL import Image

def compress_images(input_folder, output_folder, quality=10, max_size=(1024, 1024)):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Check if the file is an image
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            try:
                with Image.open(input_path) as img:
                    # Resize the image using the new Resampling method
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save the image with reduced quality
                    img.save(output_path, optimize=True, quality=quality)
                    print(f"Compressed and saved: {output_path}")
            except Exception as e:
                print(f"Error compressing {filename}: {e}")

if __name__ == "__main__":
    input_folder = "AWSDefcon1App\static\AWSDefcon1App\white_image"
    output_folder = "white_image"
    compress_images(input_folder, output_folder)
