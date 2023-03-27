import os
from flask import url_for

def process_selected_name(selected_name: str, current_image: str) -> None:
    """
    Process the user's selection and either move the image to the corresponding folder or delete it.

    Args:
        selected_name (str): The selected name for the face image.
        current_image (str): The path of the current image being processed.

    Returns:
        None
    """
    if selected_name == "neither":
        # Delete the image
        os.remove(current_image.lstrip('/'))
    else:
        # Move the image to the corresponding folder
        target_folder = os.path.join("training", "faces", selected_name)
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, os.path.basename(current_image))
        os.rename(current_image.lstrip('/'), target_path)

def get_next_image_url(extracted_faces: list) -> str:
    """
    Get the URL for the next face image in the extracted_faces list.

    Args:
        extracted_faces (list): A list of extracted face images.

    Returns:
        str: The URL for the next face image.
    """
    if extracted_faces:
        return url_for("static", filename=extracted_faces[0])
    else:
        return None