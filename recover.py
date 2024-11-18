import datetime
import pytsk3
from datetime import datetime
from signatures import file_signatures as signatures
from PyQt5.QtWidgets import *
import zipfile


class Recover:
    def __init__(self, path, out_path, choice_signatures=None):
        self.CLUSTER_SIZE = 4096
        self.img = pytsk3.Img_Info(path)
        self.seen_hashes = set()
        self.signatures = dict()
        if choice_signatures:
            for i in choice_signatures:
                self.signatures[i] = signatures[i]
        else:
            self.signatures = signatures
        print(self.signatures)
        self.out_path = out_path

    def type_of_zip(self, filepath):
        with zipfile.ZipFile(filepath, 'r') as archive:
            file_list = archive.namelist()
            if 'word/document.xml' in file_list:
                return '.docx'
            elif 'xl/workbook.xml' in file_list:
                return '.xlsx'
            elif 'ppt/presentation.xml' in file_list:
                return '.pptx'
            else:
                return '.zip'

    def signature(self, data):
        for sign in self.signatures:
            if data.startswith(self.signatures[sign]):
                return sign
        return None

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
                sign = self.signature(cluster_data)
                if sign:
                    file_name = f"recovered_{cluster_number}.{sign}"
                    print(f"Найдена сигнатура {sign} в кластере {cluster_number}, начинается восстановление...")
                    log.append(f"Найдена сигнатура {sign} в кластере {cluster_number}, начинается восстановление...")
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
                        if self.signature(next_cluster_data) == sign:
                            print(f"Достигнута новая сигнатура в кластере {next_cluster}, завершение файла {file_name}")
                            log.append(f"Достигнута новая сигнатура в кластере {next_cluster}, завершение файла {file_name}")
                            break
                        file_data += next_cluster_data
                        next_cluster += 1

                    with open(f'{self.out_path}/{file_name}', "wb") as f:
                        f.write(file_data)

                    try:
                        if sign == 'zip':
                            file_name = (file_name.split('.'))[0] + self.type_of_zip(f'{self.out_path}/{file_name}')
                            with open(f'{self.out_path}/{file_name}', "wb") as f:
                                f.write(file_data)
                    except Exception:
                        print(f"Неизвесттный тип .zip")
                        log.append(f"Неизвесттный тип .zip")

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
