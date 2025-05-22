import pydicom
import os
from PIL import Image
import numpy as np
import cv2


def dicom_to_png_array(dicom_path, png_path):
    """
    Преобразует DICOM-файл в массив png файлов с применением окна для мягких тканей.

    :param dicom_path: Путь к DICOM-файлу.
    :param png_path: Путь для сохранения PNG-изображения.
    :param rescale: Изменить размер изображения.
    """
    try:
        ds = pydicom.dcmread(dicom_path)
        pixel_array = ds.pixel_array.astype(float)

        # Применение рескейлинга (по DICOM-файлу)
        if 'RescaleSlope' in ds and 'RescaleIntercept' in ds:
            rescale_slope = float(ds.RescaleSlope)
            rescale_intercept = float(ds.RescaleIntercept)
            pixel_array = pixel_array * rescale_slope + rescale_intercept

        # Настройки Soft Tissue Window
        soft_tissue_center = 10  # Центр окна для мягких тканей
        soft_tissue_width = 350  # Ширина окна для мягких тканей

        # Применение окна для мягких тканей в [0, 255]
        img_min = soft_tissue_center - soft_tissue_width / 2
        img_max = soft_tissue_center + soft_tissue_width / 2
        windowed_image = np.clip(pixel_array, img_min, img_max)
        windowed_image = ((windowed_image - img_min) / (img_max - img_min) * 255).astype(np.uint8)

        image = np.array(windowed_image)
        image = Image.fromarray(image)

        # Сохранение изображения в формате PNG
        image.save(png_path, format="PNG")
        print(f"Файл успешно сохранен как {png_path}")

    except Exception as e:
        print(f"Ошибка при преобразовании DICOM в PNG: {e}")


def png_to_png(input_png_path, input_png_segmentation_path, output_path, resize=True):
    '''
    Преобразует PNG-файл в PNG с окном для мягких тканей (Soft Tissue Window).
    Если нет размеченного изображения, то обрезает изображение по контурам.
    Если есть размеченное изображение, то обрезает его также, как и основное без разметки.
    :param original_path: Путь к оригинальному PNG-файлу.
    :param segmentation_path: Путь к размеченному PNG-файлу.
    :param png_path: Путь для сохранения PNG-изображения.
    :param resize: Изменить размер изображения.
    '''
    if input_png_segmentation_path == "":
        try:
            img = Image.open(input_png_path, mode='r', formats=None)

            pixel_array = np.array(img)
            # print(pixel_array.shape)

            image = np.array(pixel_array)

            # Удаление верхней части изображения и левой части (закрашивание в черный)
            image[:19, :] = (0, 0, 0, 255)  # Верхняя часть
            image[:, :19] = (0, 0, 0, 255)  # Левая часть

            mask_image = image
            if len(image.shape) > 2:
                mask_image = cv2.cvtColor(mask_image, cv2.COLOR_RGB2GRAY)

            # Создание маски для пикселей, которые не являются ни черными, ни белыми
            lower_threshold = 1  # Минимальное значение (исключаем черный)
            upper_threshold = 254  # Максимальное значение (исключаем белый)
            mask_image = cv2.inRange(mask_image, lower_threshold, upper_threshold)

            # Применение маски для получения координат "ненулевых" пикселей
            non_zero = cv2.findNonZero(mask_image)

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(non_zero)

            print(x, y, w, h)

            # Convert back to PIL and crop
            image = Image.fromarray(image[y:y + h, x:x + w])

            if resize:
                image = image.resize((512, 512))  # 384
                image = np.array(image)
                image = Image.fromarray(image)

            image.save(output_path, format="PNG")
            print(f"Файл успешно сохранен как {output_path}")

        except Exception as e:
            print(f"Ошибка при преобразовании PNG в PNG: {e}")
    else:
        try:
            img = Image.open(input_png_path, mode='r', formats=None)
            img_seg = Image.open(input_png_segmentation_path, mode='r', formats=None)

            image = np.array(img)
            image_seg = np.array(img_seg)

            # 1) работаем только с изображением без разметки

            if (image.shape[:2] != image_seg.shape[:2]):
                print("Ошибка: Размеры массивов пикселей не совпадают.")
                return

            # Удаление верхней части изображения И левой части
            image[:19, :] = (0, 0, 0, 255)  # Верхняя часть
            image[:, :19] = (0, 0, 0, 255)  # Левая часть

            mask_image = image

            if len(image.shape) > 2:
                mask_image = cv2.cvtColor(mask_image, cv2.COLOR_RGB2GRAY)

            # Создание маски для пикселей, которые не являются ни черными, ни белыми
            lower_threshold = 1  # Минимальное значение (исключаем черный)
            upper_threshold = 254  # Максимальное значение (исключаем белый)
            mask_image = cv2.inRange(mask_image, lower_threshold, upper_threshold)

            # Применение маски для получения координат "ненулевых" пикселей
            non_zero = cv2.findNonZero(mask_image)

            x, y, w, h = cv2.boundingRect(non_zero)

            image = Image.fromarray(image[y:y + h, x:x + w, :])

            # Ресайз изображения
            if resize:
                image = image.resize((512, 512))  # 384
                image = np.array(image)
                image = Image.fromarray(image)

            # 2) аналогичные преобразования для размеченного изображения

            cropped_seg_image = image_seg[y:y + h, x:x + w, :]

            seg_image = Image.fromarray(cropped_seg_image)

            if resize:
                seg_image = seg_image.resize((512, 512))  # 384
                seg_image = np.array(seg_image)
                seg_image = Image.fromarray(seg_image)

            seg_image.save(output_path, format="PNG")
            print(f"222 Файл успешно сохранен как {output_path}")

        except Exception as e:
            print(f"222 Ошибка при преобразовании DICOM в PNG: {e}")


def png_to_png_directory(input_dir, input_dir_segmentation, output_dir):
    """
    Преобразует все PNG-файлы из input_dir в PNG и сохраняет их в output_dir.

    :param input_dir: Директория с PNG-файлами.
    :param output_dir: Директория для сохранения PNG-изображений.
    """

    # Создание выходной директории, если она не существует
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Если есть размеченные изображения, то обрабатываем пары файлов
    if input_dir_segmentation != "":

        # Получение списка файлов из обеих директорий
        original_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".png")])
        segmentation_files = sorted([f for f in os.listdir(input_dir_segmentation) if f.endswith(".png")])

        print(original_files)
        print(segmentation_files)

        # Определяем минимальное количество файлов
        min_files = min(len(original_files), len(segmentation_files))

        if min_files == 0:
            print("Ошибка: Нет совпадающих DICOM-файлов в директориях.")
            return

        # Обрабатываем пары файлов по порядку
        for i in range(min_files):
            original_filename = original_files[i]
            segmentation_filename = segmentation_files[i]

            # Формируем пути
            original_path = os.path.join(input_dir, original_filename)
            segmentation_path = os.path.join(input_dir_segmentation, segmentation_filename)

            png_path = os.path.join(output_dir, segmentation_filename)

            # Обрабатываем оба файла
            png_to_png(original_path, segmentation_path, png_path)

            print(f"Обработана пара: {original_filename} <-> {segmentation_filename}")
    else:
        # Если нет размеченных изображений, то обрабатываем этим путем
        # Получение списка файлов из обеих директорий
        original_files = [f for f in os.listdir(input_dir) if f.endswith(".png")]

        # Обрабатываем пары файлов по порядку
        for original_filename in original_files:
            # Формируем пути
            dicom_path = os.path.join(input_dir, original_filename)

            # Создаем имена для PNG-файлов
            png_path = os.path.join(output_dir, original_filename)

            # Обрабатываем оба файла
            png_to_png(dicom_path, "", png_path)
            print(f"Обработан файл: {original_filename}")


if __name__ == "__main__":
    input_directory_segmentation = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\103.1"
    input_directory = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\103.2"
    output_directory = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\103.3"  # Директория для сохранения размеченных PNG-изображений

    png_to_png_directory(input_directory, input_directory_segmentation, output_directory)

    input_directory_segmentation = r""
    output_directory = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\103.4"  # Директория для сохранения обычных PNG-изображений

    png_to_png_directory(input_directory, input_directory_segmentation, output_directory)
