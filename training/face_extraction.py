import os
import uuid

import cv2
import numpy as np
from mtcnn import MTCNN
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['TF_DISABLE_MKL'] = '1' 

def process_image(file, img_size, confidence_threshold, temp_folder, face_detector):
    img = np.array(Image.open(file))

    if img is None:
        return []

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_detector.detect_faces(img)
    face_paths = []

    for i, face in enumerate(faces):
        if face['confidence'] > confidence_threshold:
            x, y, width, height = face['box']
            cropped_face = img[y:y + height, x:x + width]
            resized_face = cv2.resize(cropped_face, (img_size, img_size))
            output_filename = f"{os.path.splitext(file.name)[0]}_face_{i}.png"
            output_path = os.path.join(temp_folder, output_filename)
            cv2.imwrite(output_path, cv2.cvtColor(resized_face, cv2.COLOR_RGB2BGR))
            face_paths.append(output_path)

    return face_paths


def save_faces_from_images(full_images, img_size=512, confidence_threshold=0.8):
    temp_folder = os.path.join("media", "temp", "extracted_faces", str(uuid.uuid4()))
    os.makedirs(temp_folder, exist_ok=True)

    face_paths = []

    if full_images:
        face_detector = MTCNN()

        with ThreadPoolExecutor() as executor:
            futures = []
            for file in full_images:
                futures.append(executor.submit(process_image, file, img_size, confidence_threshold, temp_folder, face_detector))

            for future in futures:
                face_paths.extend(future.result())

    return face_paths