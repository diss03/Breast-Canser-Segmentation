import os
import re


def rename_png_files(directory, study_number):
    """
    Переименовывает все .png файлы в указанной директории по шаблону <номер исследования>_<номер маски>.png

    :param directory: Путь к директории с файлами
    :param study_number: Номер исследования (например, "11")
    """

    if not os.path.exists(directory):
        print(f"rename_png_files: Директория {directory} не существует.")
        return

    files = [f for f in os.listdir(directory) if f.endswith('.png')]

    for i, file_name in enumerate(files, start=1):

        new_file_name = f"{study_number}_{i}.png"

        # Полные пути для старого и нового имени файла
        old_path = os.path.join(directory, file_name)
        new_path = os.path.join(directory, new_file_name)
        print("rename_png_files: ", old_path, new_path)

        if (old_path != new_path):
            os.rename(old_path, new_path)
            print(f"rename_png_files: Переименовано: {file_name} -> {new_file_name}")


def rename_dcm_files(directory, study_number):
    """
    Переименовывает все .dcm файлы в указанной директории по шаблону <номер исследования>_<номер маски>.dcm

    :param directory: Путь к директории с файлами
    :param study_number: Номер исследования (например, "11")
    """

    def extract_second_number(filename):
        """
        Извлекает второе число из имени файла.

        :param filename: Имя файла.
        :return: Второе число или None, если число не найдено.
        """
        match = re.search(r'\.(\d+)\.', filename)  # Ищем число между точками
        if match:
            return int(match.group(1))  # Преобразуем число в integer
        return float('inf')  # Если число не найдено, ставим его в конец списка

    if not os.path.exists(directory):
        print(f"Директория {directory} не существует.")
        return

    files = [f for f in os.listdir(directory) if f.endswith('.dcm')]
    files.sort(key=extract_second_number)

    for i, file_name in enumerate(files, start=1):
        new_file_name = f"{study_number}_{i}.dcm"

        # Полные пути для старого и нового имени файла
        old_path = os.path.join(directory, file_name)
        new_path = os.path.join(directory, new_file_name)

        os.rename(old_path, new_path)
        print(f"Переименовано: {file_name} -> {new_file_name}")


if __name__ == "__main__":
    directory_path_1 = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\7.1"
    directory_path_2 = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries\7.2"
    study_number_1 = directory_path_1.split(os.sep)[-1].split('.')[0]
    study_number_2 = directory_path_2.split(os.sep)[-1].split('.')[0]

    rename_png_files(directory_path_1, study_number_1)
    rename_png_files(directory_path_2, study_number_2)
