```
usage: lstm [-d N_DAYS] [-i N_INPUTS]  [--epochs N_EPOCHS] [-e S_END_DATE] [--loops N_LOOPS] [-v VALID]
 [--lr LEARNING_RATE] [--no_shuffle]
```
Long-Short Term Memory:
  * -d : prediction days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * --epochs : number of training epochs. Default 200.
  * -v : validation split.  Default 0.1
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --loops: number of loops to iterate and train models. Default 1
  * --lr : learning rate for optimizer
  * --no_shuffle : split validation data in time_ordered way instead of random.

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

![lstm](https://user-images.githubusercontent.com/25267873/108604943-d2025400-73a8-11eb-83c5-edb4a2121cba.png)

### Backtesting Example <a name="backtesting"></a>

![appl_pred](https://user-images.githubusercontent.com/25267873/111053156-4173dc80-8459-11eb-9fcb-e81211961743.png)

![apple_error](https://user-images.githubusercontent.com/25267873/111053157-420c7300-8459-11eb-8c37-fb1b5208d635.png)

<img width="992" alt="Captura de ecrã 2021-03-14, às 00 06 51" src="https://user-images.githubusercontent.com/25267873/111053158-420c7300-8459-11eb-993b-6d9c26f98af9.png">
