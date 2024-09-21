import json
import os
import cv2

def image_header_footer_removal_process(op_dir_and_ip_dir_image, output_directory_hf, group_name, doc_name_with_extension, header_offset, footer_offset):
    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_directory_hf):
            os.makedirs(output_directory_hf)
        # Find the position of the last dot (.) in the filename
        last_dot_index = doc_name_with_extension.rfind(".")
        # Extract the filename without the extension
        filename_without_extension = doc_name_with_extension[:last_dot_index]
        # Print the result
        print("Filename without extension for HF removal:", filename_without_extension)

        # Check if the folder exists in the input path
        folder_b_path = os.path.join(op_dir_and_ip_dir_image, group_name)

        # Check if the subfolder exists inside folder_b
        folder_c_path = os.path.join(folder_b_path, filename_without_extension)

        # Get the list of PNG files in folder_c
        png_files = [f for f in os.listdir(folder_c_path) if f.lower().endswith(".png")]

        # Create the output subdirectory if it doesn't exist
        output_subdir = os.path.join(output_directory_hf, group_name, filename_without_extension)
        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)

        # Process each PNG file
        for png_file in png_files:
            file_path = os.path.join(folder_c_path, png_file)
            output_file_path = os.path.join(output_subdir, png_file)

            # Read the image using OpenCV
            image = cv2.imread(file_path)

            # Get the current dimensions of the image
            height, width = image.shape[:2]
            #print(height, width)

            if header_offset >= 0 and footer_offset > 0:
                header_pixels = header_offset
                footer_pixels = height - footer_offset
                image_without_top = image[header_pixels:height, :]
                image_without_top_and_bottom = image_without_top[:-footer_pixels, :]
                # Save the modified image
                cv2.imwrite(output_file_path, image_without_top_and_bottom)
            else:
                # Calculate the cropping boundaries
                top_boundary = header_offset if header_offset > 0 else 0
                bottom_boundary = height - footer_offset if footer_offset > 0 else height

                # Perform the cropping
                image_cropped = image[top_boundary:bottom_boundary, :]

                # Save the modified image
                cv2.imwrite(output_file_path, image_cropped)

        return "Header Footer removal process completed."
    except Exception as e:
        print("IMAGE header footer removal process failed", str(e))                       