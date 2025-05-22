# from collect_png import collect_png_files
from dicom_to_png_array import png_to_png_directory
from png_mask_creator import transform
from rename_files import rename_png_files
from png_array_to_nii import save_png_to_nifty
import os
import shutil


def create_nifty_data(directory_path, directory_path_png, directory_path_mask):
    study_number_1 = directory_path_png.split(os.sep)[-1].split('.')[0]
    study_number_2 = directory_path_mask.split(os.sep)[-1].split('.')[0]

    rename_png_files(directory_path_png, study_number_1)
    rename_png_files(directory_path_mask, study_number_2)

    input_directory = directory_path_png  # Директория с обычными изображениями-файлами
    input_directory_segmentation = directory_path_mask  # Директория с размеченными PNG-изображениями

    dir_masks = directory_path_mask + ".cr"  # КТ разметка png
    dir_images = directory_path_png + ".cs"  # КТ снимки png

    png_to_png_directory(input_directory, '', dir_images)
    png_to_png_directory(input_directory, input_directory_segmentation, dir_masks)

    dir_bin_masks = directory_path_mask + ".b"  # бинарные маски png
    dir_output_labels = directory_path_mask + ".a"  # аннотации txt

    transform(dir_masks, dir_images, dir_bin_masks, dir_output_labels)

    image_nifti_out = directory_path + "\images\\" + study_number_1 + "_image.nii.gz"
    mask_nifti_out = directory_path + "\labels\\" + study_number_2 + "_label.nii.gz"

    save_png_to_nifty(dir_bin_masks, mask_nifti_out)
    save_png_to_nifty(dir_images, image_nifti_out)

    shutil.rmtree(dir_bin_masks)
    shutil.rmtree(dir_output_labels)
    shutil.rmtree(dir_masks)
    shutil.rmtree(dir_images)

    print("-" * 100, "\n", f"create_nifty_data: преобразование исследования {study_number_1} завершено!")


if __name__ == "__main__":
    directory_path = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries"
    directory_path_mask = r""
    directory_path_png = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\test_1.1"
    create_nifty_data(directory_path, directory_path_png, directory_path_mask)