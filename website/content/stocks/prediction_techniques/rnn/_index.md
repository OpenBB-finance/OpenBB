```
usage: rnn [-d N_DAYS] [-i N_INPUTS] [--epochs N_EPOCHS] [-e S_END_DATE] [--batch_size N_BATCH_SIZE] [--xla_cpu] [--xla_gpu]
            [--force_gpu_allow_growth {true,false,default}] [--loops N_LOOPS] [-v VALID_SPLIT] [--lr LR] [--no_shuffle] [-h]
```

Recurrent Neural Network

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.txt](/config_neural_network_models.py)
```
Recurrent_Neural_Network \
    = [ {'SimpleRNN':
                {'units':100, 'activation':'linear', 'return_sequences':True} },
        {'SimpleRNN':
                {'units':50, 'activation':'linear', 'return_sequences':True} },
        {'Dropout':
                {'rate':0.2} },
        {'SimpleRNN':
                {'units':21, 'activation':'linear', 'return_sequences':False} },
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

![rnn](https://user-images.githubusercontent.com/25267873/108604940-d0d12700-73a8-11eb-837e-a5aa128942d9.png)
