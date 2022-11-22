---
title: Installation
sidebar_position: 2
---

### Steps

1. **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

   Download the `x86_64` Miniconda for your respective system and follow along
   with it's installation instructions. The Miniconda architecture MUST be
   `x86_64` in order to use certain features.

2. **Create Environment**

   ```shell
   conda create -n <environment> python=3.9.6 -y
   ```

   :::note (Optional) If you would like machine learning forecast features:

   ```shell
   conda install -c conda-forge u8darts-torch=0.22.0 -y
   conda install -c conda-forge pytorch-lightning=1.6.5 -y
   ```

3. **Install OpenBB Terminal**

   ```shell
   pip install openbbterminal
   ```

   :::note (Optional) If you would like machine learning forecast features:

   ```shell
   pip install "openbbterminal[prediction]"
   ```
