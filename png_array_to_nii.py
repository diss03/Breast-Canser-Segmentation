import nibabel as nib
import numpy as np
from PIL import Image
import os


# png_folder = r"C:\Users\stden\PycharmProjects\Diploma\venv\PNG\5.cs"
# png_out = r"C:\Users\stden\PycharmProjects\Diploma\venv\nii_data\5.cs.nii.gz"
# png_folder = r"C:\Users\stden\PycharmProjects\Diploma\venv\PNG\5.b"
# png_out = r"C:\Users\stden\PycharmProjects\Diploma\venv\nii_data\5 .b.nii.gz"

def save_png_to_nifty(png_folder, png_out):
    png_files = [f for f in os.listdir(png_folder) if f.endswith('.png')]

    max_x, max_y = 0, 0
    for png_file in png_files:
        img = Image.open(os.path.join(png_folder, png_file))
        x, y = img.size
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    num_slices = len(png_files)

    nifti_array = np.zeros((max_y, max_x, num_slices), dtype=np.uint8)

    def sort_filenames_by_number(filenames):
        # Определяем ключ сортировки: извлекаем число после '_'
        def extract_number(filename):
            # Разделяем строку по '_' и берем последнюю часть (число с расширением)
            number_part = filename.split('_')[-1]
            # Убираем расширение файла и преобразуем оставшуюся часть в целое число
            return int(number_part.split('.')[0])

        # Сортируем список с использованием ключа
        return sorted(filenames, key=extract_number)

    png_files = sort_filenames_by_number(png_files)

    for i, png_file in enumerate(png_files):
        img = Image.open(os.path.join(png_folder, png_file))
        img = img.convert('L')

        current_x, current_y = img.size

        # Проверка, что все изображения одного размера
        if current_x != max_x or current_y != max_y:
            raise ValueError(
                f"Размер {png_file} ({current_x}x{current_y}) не совпадает с максимальным размером ({max_x}x{max_y})!")

        nifti_array[:, :, i] = np.array(img)

    pixel_spacing = [1, 1]

    # Приводим к LPI
    affine = np.array([
        [pixel_spacing[0], 0, 0, 0],
        [0, pixel_spacing[1], 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    rotation_1 = np.array([
        [0, -1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    rotation_2 = np.array([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ])

    affine = rotation_1 @ rotation_2 @ affine

    nifti_image = nib.Nifti1Image(nifti_array, affine, dtype=np.int32)
    nifti_image.header['pixdim'] = [1.0, pixel_spacing[0], pixel_spacing[1], 1.0, 1.0, 1.0, 1.0, 1.0]
    nib.save(nifti_image, png_out)

    print(f'{png_file} saved')
