```
usage: lstm [-d N_DAYS] [-i N_INPUTS] [--epochs N_EPOCHS] [-e S_END_DATE] [--batch_size N_BATCH_SIZE] [--xla_cpu] [--xla_gpu]
            [--force_gpu_allow_growth {true,false,default}] [--loops N_LOOPS] [-v VALID_SPLIT] [--lr LR] [--no_shuffle] [-h]
```

Long-Short Term Memory

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.py](/config_neural_network_models.py)
```
Long_Short_Term_Memory \
    = [ {'LSTM':
                {'units':25, 'activation':'tanh', 'return_sequences':True} },
        {'LSTM':
                {'units':15, 'activation':'tanh', 'return_sequences':False} },
        {'Dense':
                {'activation':'relu'} }]
```

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

![lstm](https://user-images.githubusercontent.com/25267873/108604943-d2025400-73a8-11eb-83c5-edb4a2121cba.png)

#### Backtesting Example

![appl_pred](https://user-images.githubusercontent.com/25267873/111053156-4173dc80-8459-11eb-9fcb-e81211961743.png)

![apple_error](https://user-images.githubusercontent.com/25267873/111053157-420c7300-8459-11eb-8c37-fb1b5208d635.png)

<img width="992" alt="Captura de ecrã 2021-03-14, às 00 06 51" src="https://user-images.githubusercontent.com/25267873/111053158-420c7300-8459-11eb-993b-6d9c26f98af9.png">
