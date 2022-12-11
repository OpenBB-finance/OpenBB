---
title: Installation
sidebar_position: 2
---

# Installation

We provide a simple installation method in order to utilize the OpenBB SDK. You must first create an environment, which allows you to isolate the SDK from the rest of your system. It is our recommendation that you utilize a `conda` environment because there are optional features, such as `forecast`, that utilize libraries that are specifically sourced from `conda-forge`. Due to this, if you do not use a conda environment, you will not be able to use some of these features. As such, the installation steps will be written under the assumption that you are using conda.

## Steps

:::note NOTE
Make sure you meet all [requirements](requirements.md) before proceeding.
:::

### 1. **Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)**

   Download the `x86_64` Miniconda for your respective system and follow along
   with it's installation instructions. The Miniconda architecture MUST be
   `x86_64` in order to use certain features.

### 2. **Create the virtual environment**

```bash
conda create -n obb python=3.9.6 -y
```

### 3. **Activate the virtual environment**

```bash
conda activate obb
```

### 4. **Install OpenBB SDK Core package**

```bash
pip install openbb
```

### 5. **(Optional) Install the Toolkits**

#### 5.1 **If you would like to use the Portfolio Optimization features**

:::note NOTE
If on Apple Silicon Macs (M1/M2) you will need to install dependency from conda-forge first
```bash
conda install -c conda-forge cvxpy=1.2.2 -y
```
:::


Install the Portfolio Optimization Toolkit

```bash
pip install "openbb[optimization]"
```

#### 5.2 **If you would like ML Forecasting features**

:::note NOTE
If on Apple Silicon Macs (M1/M2) you will need to install the dependency from conda-forge first
```bash
conda install -c conda-forge lightgbm=3.3.3 -y
```
:::

Install the Forecasting Toolkit

```bash
pip install "openbb[prediction]"
```

#### 5.3 **If you would like to use both Portfolio Optimization and ML forecast features**

:::note NOTE
If on Apple Silicon Macs (M1/M2) you will need to install the dependencies from conda-forge first
```bash
conda install -c conda-forge lightgbm=3.3.3 cvxpy=1.2.2 -y
```
:::

Install all Toolkits

```bash
pip install "openbb[all]"
```

Congratulations! You have successfully installed `openbb` on an environment and are now able to begin using it. However, it is important to note that if you close out of your CLI you must re-activate your environment in order begin using it again. This can be done with the following:

```bash
conda activate obb
```

The OpenBB SDK can be imported to a Jupyter Notebook or any code editor with, `from openbb_terminal.sdk import openbb` as explained in the [How to use the SDK](https://docs.openbb.co/sdk/guides/basics) guides. By following the above process, the [OpenBB Terminal](https://docs.openbb.co/terminal) is automatically included as well which can be ran by typing `openbb`.

