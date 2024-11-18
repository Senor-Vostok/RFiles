import datetime
import pytsk3
from datetime import datetime
from signatures import file_signatures as signatures
from PyQt5.QtWidgets import *


class Recover:
    def __init__(self, path, out_path, choice_signatures=None):
        self.CLUSTER_SIZE = 4096
        self.img = pytsk3.Img_Info(path)
        self.seen_hashes = set()
        self.choice_signatures = choice_signatures
        self.out_path = out_path

    def scan_signatures(self, out_progress=None, out_label=None, log=None):
        disk_size = self.img.get_size()
        total_clusters = disk_size // self.CLUSTER_SIZE
        recovered_files = []
        cluster_number = 0

        while True:
            try:
                offset = cluster_number * self.CLUSTER_SIZE
                cluster_data = self.img.read(offset, self.CLUSTER_SIZE)
                if not cluster_data:
                    break
                if cluster_data.startswith(signatures["png"]):
                    file_name = f"recovered_png_{cluster_number}.png"
                    print(f"Найдена сигнатура PNG в кластере {cluster_number}, начинается восстановление...")
                    log.append(f"Найдена сигнатура PNG в кластере {cluster_number}, начинается восстановление...")
                    file_data = cluster_data
                    next_cluster = cluster_number + 1
                    enter_time = datetime.now()
                    while True:
                        if (datetime.now() - enter_time).seconds > 10:
                            print('Файл фрагментирован, восстановление будет частичным!!!')
                            log.append('Файл фрагментирован, восстановление будет частичным!!!')
                            break
                        offset = next_cluster * self.CLUSTER_SIZE
                        next_cluster_data = self.img.read(offset, self.CLUSTER_SIZE)
                        if not next_cluster_data:
                            break
                        if next_cluster_data.startswith(signatures["png"]):
                            print(f"Достигнута новая сигнатура в кластере {next_cluster}, завершение файла {file_name}")
                            log.append(f"Достигнута новая сигнатура в кластере {next_cluster}, завершение файла {file_name}")
                            break
                        file_data += next_cluster_data
                        next_cluster += 1
                    with open(f'{self.out_path}/{file_name}', "wb") as f:
                        f.write(file_data)
                    print(f"Файл {file_name} успешно восстановлен.")
                    log.append(f"Файл {file_name} успешно восстановлен.\n")
                    recovered_files.append(file_name)
            except Exception as e:
                print(f"Ошибка при чтении кластера {cluster_number}: {e}")
                break
            cluster_number += 1
            progress = (cluster_number / total_clusters) * 100
            if out_progress:
                out_progress.setValue(int(progress))
                out_label.setText(f'{progress:.2f}%')
                QApplication.processEvents()
            else:
                print(f"\rПрогресс: {progress:.2f}%", end="")
