import datetime
import pytsk3
from datetime import datetime
from signatures import file_signatures as signatures
from PyQt5.QtWidgets import *
import zipfile


def type_of_zip(filepath):
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


class Recover:
    def __init__(self, path, out_path, choice_signatures, app):
        self.CLUSTER_SIZE = 4096
        self.img = pytsk3.Img_Info(path)
        self.signatures = dict()
        if choice_signatures:
            for i in choice_signatures:
                self.signatures[i] = signatures[i]
        else:
            self.signatures = signatures
        print(self.signatures)
        self.app = app
        self.out_path = out_path
        self.close = False

    def signature(self, data):
        for sign in self.signatures:
            if data.startswith(self.signatures[sign]):
                return sign

    def recover__(self, cluster_number, cluster_data, sign):
        file_name = f"recovered_{cluster_number}.{sign}"
        self.app.log_text.append(f"Найдена сигнатура {sign} в кластере {cluster_number}, начинается восстановление...")
        file_data = cluster_data
        next_cluster = cluster_number + 1
        enter_time = datetime.now()
        while not self.close:
            if (datetime.now() - enter_time).seconds > 3:
                self.app.log_text.append('Файл фрагментирован, восстановление будет частичным!!!')
                break
            offset = next_cluster * self.CLUSTER_SIZE
            next_cluster_data = self.img.read(offset, self.CLUSTER_SIZE)
            if not next_cluster_data:
                break
            if next_cluster_data.startswith(self.signatures[sign]):
                self.app.log_text.append(
                    f"Достигнута новая сигнатура в кластере {next_cluster}, завершение файла {file_name}")
                break
            file_data += next_cluster_data
            next_cluster += 1
        with open(f'{self.out_path}/{file_name}', "wb") as f:
            f.write(file_data)
        try:
            if sign == 'zip':
                file_name = (file_name.split('.'))[0] + type_of_zip(f'{self.out_path}/{file_name}')
                with open(f'{self.out_path}/{file_name}', "wb") as f:
                    f.write(file_data)
        except Exception:
            self.app.log_text.append(f"Неизвестный тип .zip")
        self.app.log_text.append(f"Файл {file_name} восстановлен.\n")

    def scan_signatures(self):
        disk_size = self.img.get_size()
        total_clusters = disk_size // self.CLUSTER_SIZE
        cluster_number = 0
        cluster_per_seconds = 1
        wal_clusters = cluster_number + 1
        start_time = datetime.now()
        while not self.close:
            try:
                offset = cluster_number * self.CLUSTER_SIZE
                cluster_data = self.img.read(offset, self.CLUSTER_SIZE)
                if not cluster_data:
                    break
                sign = self.signature(cluster_data)
                if sign:
                    self.recover__(cluster_number, cluster_data, sign)
            except Exception as e:
                print(f"Ошибка при чтении кластера {cluster_number}: {e}")
                break
            cluster_number += 1
            progress = (cluster_number / total_clusters) * 100
            if (datetime.now() - start_time).seconds >= 1:
                start_time = datetime.now()
                cluster_per_seconds = cluster_number - wal_clusters
                wal_clusters = cluster_number
            self.app.progress_bar.setValue(int(progress))
            seconds = ((total_clusters - cluster_number) // cluster_per_seconds)
            self.app.progress_label.setText(f"\rПрогресс: {progress:.2f}%\tПримерное время сканирования: {seconds // 3600}:{seconds // 60 - (seconds // 3600) * 60}:{seconds % 60}")
            QApplication.processEvents()
