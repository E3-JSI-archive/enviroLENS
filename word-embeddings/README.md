# Notebooks

## Prerequisites

- Python 3
- Conda environment (optional but recommended)

## Install

1. Create a new python environment activate it. With `conda` you can run
    ```bash
    conda create --name envirolens
    ```

2. To install the required modules run

    ```bash
    pip install -r requirements.txt
    ```

3. Setup the connections to the existing modules
    ```bash
    python setup.py install
    ```
    This will link the modules found in [modules](./modules) folder so that you can use it with ease
    in the notebooks.
