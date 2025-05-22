import numpy as np
import os
import cv2


def create_binary_mask(image_path, path_out, lower_hsv, upper_hsv):
    """
    Функция для создания бинарной маски на изображении.

    Параметры:
    - image_path: str, путь к изображению в формате PNG.
    - path_out: str, путь для сохранения бинарной маски.
    - lower_hsv: tuple, нижняя граница цвета в формате HSV (H, S, V).
    - upper_hsv: tuple, верхняя граница цвета в формате HSV (H, S, V).

    Возвращает:
    - binary_mask: бинарная маска.
    - contours: список найденных контуров.
    """
    # Шаг 1: Загрузка изображения
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Изображение не найдено: {image_path}")

    # Шаг 2: Преобразование в HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Шаг 3: Создание бинарной маски по заданным границам HSV
    binary_mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    success = cv2.imwrite(path_out, binary_mask)

    if success:
        print(f"Бинарная маска сохранена как {path_out}")
    else:
        print(f"Ошибка при сохранении бинарной маски: {path_out}")

    return binary_mask


def mask_to_polygons(mask):
    """
    Преобразует бинарную маску в список многоугольников.

    :param mask: Бинарная маска (numpy array, shape=(H, W)).
    :return: Список многоугольников в формате [[x1, y1, x2, y2, ..., xn, yn], ...].
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    print(contours)
    polygons = []
    for contour in contours:
        # Уплощаем контур в одномерный массив [x1, y1, x2, y2, ..., xn, yn]
        contour = contour.flatten().tolist()
        if len(contour) >= 6:  # Многоугольник должен иметь хотя бы 3 точки
            polygons.append(contour)
    return polygons


def polygon_to_yolo_format(polygon, img_width, img_height, class_id=0):
    """
    Преобразует многоугольник в формат YOLO.

    :param polygon: Многоугольник в формате [x1, y1, x2, y2, ..., xn, yn].
    :param img_width: Ширина изображения.
    :param img_height: Высота изображения.
    :param class_id: ID класса объекта.
    :return: Строка аннотации в формате YOLO для сегментации.
    """
    # Нормализация координат многоугольника
    normalized_polygon = [
        coord / img_width if i % 2 == 0 else coord / img_height
        for i, coord in enumerate(polygon)
    ]

    # Формирование строки в формате YOLO
    yolo_format = f"{class_id} " + " ".join(f"{coord:.6f}" for coord in normalized_polygon)
    return yolo_format


def interractive_mask_choosing(fn):
    def nothing(args):
        pass

    # Создаем окно для отображения результата и бегунки
    cv2.namedWindow("setup")

    # Бегунки для нижнего и верхнего диапазона HSV
    cv2.createTrackbar("H1", "setup", 0, 179, nothing)  # H в OpenCV имеет диапазон 0-179
    cv2.createTrackbar("S1", "setup", 0, 255, nothing)  # S и V имеют диапазон 0-255
    cv2.createTrackbar("V1", "setup", 0, 255, nothing)
    cv2.createTrackbar("H2", "setup", 179, 179, nothing)
    cv2.createTrackbar("S2", "setup", 255, 255, nothing)
    cv2.createTrackbar("V2", "setup", 255, 255, nothing)

    # Загрузка изображения
    img = cv2.imread(fn)

    # Преобразуем изображение в HSV
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    while True:
        # Получаем значения из бегунков
        h1 = cv2.getTrackbarPos('H1', 'setup')
        s1 = cv2.getTrackbarPos('S1', 'setup')
        v1 = cv2.getTrackbarPos('V1', 'setup')
        h2 = cv2.getTrackbarPos('H2', 'setup')
        s2 = cv2.getTrackbarPos('S2', 'setup')
        v2 = cv2.getTrackbarPos('V2', 'setup')

        # Собираем значения в нижний и верхний диапазоны HSV
        lower_bound = np.array([h1, s1, v1])
        upper_bound = np.array([h2, s2, v2])

        # Применяем фильтр и делаем бинаризацию
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)

        # Показываем результат
        cv2.imshow('Mask', mask)

        # Выход по нажатию 'q'
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def transform(dir_masks, dir_images, dir_bin_masks, dir_output_labels):
    # interractive_mask_choosing(r"C:\Users\stden\PycharmProjects\Diploma\Nephrogr.ph.  1.5  Br40  4_149.png")

    # Параметры HSV для выделенных опухолей
    lower_hsv = np.array([40, 40, 40])  # Минимальные значения H, S, V
    upper_hsv = np.array([150, 255, 255])  # Максимальные значения H, S, V

    # Пути к директориям
    # dir_masks = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.cr"  # КТ разметка png
    # dir_images = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.cs"  # КТ снимки png
    # dir_bin_masks = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.b"  # бинарные маски png
    # dir_output_labels = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.a"  # аннотации txt

    # Создание выходных директорий
    os.makedirs(dir_bin_masks, exist_ok=True)
    os.makedirs(dir_output_labels, exist_ok=True)

    # Создание списка полных путей КТ масок png и бинарных масок png
    file_names = [f for f in os.listdir(dir_masks) if f.endswith('.png')]
    input_mask = [os.path.join(dir_masks, f) for f in file_names]
    output_bin_masks = [os.path.join(dir_bin_masks, f) for f in file_names]

    # Создание бинарных масок и сохранение их в директорию
    for k in range(len(input_mask)):
        create_binary_mask(input_mask[k], output_bin_masks[k], lower_hsv, upper_hsv)

    # Получение списка файлов
    image_files = sorted([f for f in os.listdir(dir_images) if f.endswith('.png')])
    bin_mask_files = sorted([f for f in os.listdir(dir_bin_masks) if f.endswith('.png')])

    # Убедитесь, что количество файлов совпадает
    assert len(image_files) == len(bin_mask_files), "Количество изображений и масок не совпадает!"

    for i, (image_file, mask_file) in enumerate(zip(image_files, bin_mask_files)):
        # Создание полных путей к файлам
        image_path = os.path.join(dir_images, image_file)
        label_path = os.path.join(dir_bin_masks, mask_file)

        # Чтение изображения и бинарной маски
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(label_path, cv2.IMREAD_GRAYSCALE)

        # Убедитесь, что размеры совпадают
        assert image.shape == mask.shape, f"Размеры изображения и маски не совпадают для {image_file}"

        # Нахождение bounding boxes
        bboxes = mask_to_polygons(mask)

        # Имена для выходных файлов
        output_label_name = bin_mask_files[i].replace('.png', '.txt')

        # Сохранение аннотаций
        output_label_path = os.path.join(dir_output_labels, output_label_name)

        with open(output_label_path, "w") as f:
            for bbox in bboxes:
                yolo_annotation = polygon_to_yolo_format(bbox, img_width=image.shape[1], img_height=image.shape[0],
                                                         class_id=0)
                f.write(yolo_annotation + "\n")
        print(f"Аннотация сохранена как {output_label_path}")


if __name__ == "__main__":
    dir_masks = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.cr"  # КТ разметка png
    dir_images = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.cs"  # КТ снимки png
    dir_bin_masks = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.b"  # бинарные маски png
    dir_output_labels = r"C:\Users\stden\PycharmProjects\DIPLOMA\venv\PNG\69.a"  # аннотации txt
    transform(dir_masks, dir_images, dir_bin_masks, dir_output_labels)

