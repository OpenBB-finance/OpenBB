```
usage: mlp [-d N_DAYS] [-i N_INPUTS] [--epochs N_EPOCHS] [-e S_END_DATE] [--loops N_LOOPS] [-v VALID]
 [--lr LEARNING_RATE] [--no_shuffle]
```
MulitLayer Perceptron:
  * -d : prediciton days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * --epochs : number of training epochs. Default 200.
  * -v : validation split.  Default 0.1
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --lr : learning rate for optimizer
  * --loops: number of loops to iterate and train models. Default 1.
  * --no_shuffle : split validation data in time_ordered way instead of random.

Due to the complexity of defining a model through command line, one can define it in: [config_neural_network_models.txt](/config_neural_network_models.py)
```
MultiLayer_Perceptron \
    = [ {'Dense':
                {'units':50, 'activation':'relu'} },
        {'Dense':
                {'units':100, 'activation':'relu'} },
        {'Dense':
                {'units':80, 'activation':'relu'} },
        {'Dense':
                {'units':30, 'activation':'relu'} },
        {'Dense':
                {'activation':'relu'} }]
```

![mlp](https://user-images.githubusercontent.com/25267873/108604944-d2025400-73a8-11eb-9ab6-52972160cd2a.png)
