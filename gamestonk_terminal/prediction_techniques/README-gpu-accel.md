# GPU acceleration with CUDA

Most up-to-date docs and recommendations: https://www.tensorflow.org/install/gpu

### CUDA 11.0.3, cuDNN 8.0.5 - Tested working

1. Install [CUDA 11.0.3](https://developer.nvidia.com/cuda-toolkit-archive)

2. Install [cuDNN 8.0.5 for CUDA 11.0](https://developer.nvidia.com/rdp/cudnn-archive). This requires signing up for the nvidia developer program. To install, copy the bin/, lib/, include/ dirs into your CUDA install dirs.

    | Platform | CUDA path                                                  |
    | -------- | ---------------------------------------------------------- |
    | Linux    | /usr/local/cuda-X.Y                                        |
    | Windows  | C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v<XX.Y> |

3. Set the environment variables `CUDA_PATH` and `CUDA_PATH_V11` if needed. These are usually set by the CUDA installer.

### CUDA 11.1, cuDNN 8.0.5 - not tested

### CUDA 11.2.1, cuDNN 8.1 - does not work

## Enable XLA for Neural Networks

For neural network training, there are flags defined to enable XLA and GPU options. Note that XLA and especially GPU acceleration may be slower than the defaults if you are not configuring a larger batch size. The default settings produce matrices that are too small to effectively take advantage of these features.

```bash
> load -t GME
> pred
> lstm -h  # display the help menu which lists all args
> lstm --xla_gpu --force_allow_gpu_growth true  # enable xla with gpu acceleration and flexible memory usage
```

## Globally enable XLA

XLA is a domain specific compiler for linear algebra that can accelerate TensorFlow models if you can get it working. https://www.tensorflow.org/xla

| Env var name              | Value                                                        |
| ------------------------- | ------------------------------------------------------------ |
| XLA_FLAGS                 | --xla_gpu_cuda_data_dir=CUDA_PATH_V11_0 |
| TF_XLA_FLAGS              | --tf_xla_cpu_global_jit --tf_xla_enable_xla_devices |
   To enable profiling (useful for debugging), add `--xla_hlo_profile` to `XLA_FLAGS`

## Globally enable GPU + XLA

By default, TensorFlow will allocate 100% of your available GPU memory before it starts doing work. Using `TF_FORCE_GPU_ALLOW_GROWTH` below will override this behavior so that it only allocates memory as needed.

| Env var name              | Value                                                        |
| ------------------------- | ------------------------------------------------------------ |
| TF_XLA_FLAGS              | --tf_xla_auto_jit=2 --tf_xla_enable_xla_devices              |
| TF_FORCE_GPU_ALLOW_GROWTH | true                                                         |
