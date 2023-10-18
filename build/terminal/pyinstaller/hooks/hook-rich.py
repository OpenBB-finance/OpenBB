from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = copy_metadata("rich") + collect_data_files("rich")
