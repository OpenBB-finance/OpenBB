```
usage: lstm [-d N_DAYS] [-i N_INPUTS] [--epochs N_EPOCHS] [-e S_END_DATE] [--loops N_LOOPS] [-v VALID]
[--lr LEARNING_RATE] [--no_shuffle]
```
1D Convolutional Neural Net:
  * -d : prediction days. Default 5.
  * -i : number of days to use for prediction. Default 40.
  * --epochs : number of training epochs. Default 50.
  * -v : validation split.  Default 0.1
  * -e : end date (format YYYY-MM-DD) of the stock - Backtesting. Default None.
  * --xla_cpu: if present, will enable XLA for CPU (overrides environment variables during run).
  * --xla_gpu: if present, will enable XLA for GPU (overrides environment variables during run).
  * --force_allow_gpu_growth: if true, will force TensorFlow to allow GPU memory usage to grow as needed. Otherwise will allocate 100% of available GPU memory when CUDA is set up. Default true.
  * --batch_size: batch size for model training, should not be used unless advanced user. Default None.
  * --loops: number of loops to iterate and train models. Default 1.
  * --lr : learning rate for optimizer
  * --no_shuffle : split validation data in time_ordered way instead of random.
