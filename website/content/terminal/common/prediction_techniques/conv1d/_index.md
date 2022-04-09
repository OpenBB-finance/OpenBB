```
usage: conv1d [-d N_DAYS] [-i N_INPUTS] [--epochs N_EPOCHS] [-e S_END_DATE] [--batch_size N_BATCH_SIZE] [--xla_cpu] [--xla_gpu]
              [--force_gpu_allow_growth {true,false,default}] [--loops N_LOOPS] [-v VALID_SPLIT] [--lr LR] [--no_shuffle] [-h]
```

1D Convolutional Neural Net.

```
optional arguments:
  -d N_DAYS, --days N_DAYS
                        prediction days.
  -i N_INPUTS, --input N_INPUTS
                        number of days to use for prediction.
  --epochs N_EPOCHS     number of training epochs.
  -e S_END_DATE, --end S_END_DATE
                        The end date (format YYYY-MM-DD) to select - Backtesting
  --batch_size N_BATCH_SIZE
                        batch size for model fitting (use a power of 2)
  --xla_cpu             enable XLA for CPU (see https://www.tensorflow.org/xla)
  --xla_gpu             enable XLA for GPU (see https://www.tensorflow.org/xla)
  --force_gpu_allow_growth {true,false,default}
                        true: GPU memory will grow as needed.
                        false: TensorFlow will allocate 100% of GPU memory.
                        default: usually the same as false, uses env/TensorFlow default
  --loops N_LOOPS       number of loops to iterate and train models
  -v VALID_SPLIT, --valid VALID_SPLIT
                        Validation data split fraction
  --lr LR               Specify learning rate for optimizer.
  --no_shuffle          Specify if shuffling validation inputs.
  -h, --help            show this help message
```
<img size="1400" alt="Feature Screenshot - conv1d" src="https://user-images.githubusercontent.com/18151143/154813903-4df1cb49-21f3-4346-9f43-7630c27a5d42.png">

