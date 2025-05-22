from dataset_creator import create_nifty_data
import time

# Список номеров исследований для обработки
names = [
    2,
    3,
    5,
    7,
    8,
    9,
    11,
    12,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    34,
    39,
    40,
    41,
    42,
    43,
    46,
    49,
    50,
    55,
    56,
    63,
    67,
    68,
    69,
    70,
    71,
    72,
    73,
    74,
    75,
    76,
    77,
    78,
    79,
    80,
    81,
    82,
    83,
    84,
    85,
    86,
    88,
    89,
    90,
    91,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101,
    102,
    103
]

directory_path = r"C:\Users\stden\PycharmProjects\Diploma\venv\3d_data_ceries"
start_time = time.time()
for i in range(len(names)):
    directory_path_mask = directory_path + "\\" + str(names[i]) + ".1"
    directory_path_png = directory_path + "\\" + str(names[i]) + ".2"

    create_nifty_data(directory_path, directory_path_png, directory_path_mask)
consumed_time = time.time() - start_time
avg_time = consumed_time / len(names)
print("СРЕДНЕЕ ВРЕМЯ ВЫПОЛНЕНИЯ:", avg_time)
