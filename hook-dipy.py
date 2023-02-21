from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('dipy')

hiddenimports = [
    "dipy.utils.omp",
    "dipy.segment.cythonutils",
]
