import importlib

import importlib_metadata
from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata("transformers")
datas += copy_metadata("tokenizers")
datas += copy_metadata("tqdm")
datas += copy_metadata("regex")
datas += copy_metadata("requests")
datas += copy_metadata("packaging")
datas += copy_metadata("filelock")
datas += copy_metadata("numpy")
datas += copy_metadata("torch")

candidates = [
    "tensorflow",
    "tensorflow-cpu",
    "tensorflow-gpu",
    "tf-nightly",
    "tf-nightly-cpu",
    "tf-nightly-gpu",
    "intel-tensorflow",
    "intel-tensorflow-avx512",
    "tensorflow-rocm",
    "tensorflow-macos",
    "tensorflow-aarch64",
]
for candidate in candidates:
    try:
        if importlib.util.find_spec(candidate):
            datas += copy_metadata(candidate)
            break
    except importlib_metadata.PackageNotFoundError:
        pass
