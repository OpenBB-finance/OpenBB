# Jupyter Lab Extensions for using Gamestonk Terminal


## Development setup

In this section `gst` extension will be used as an example.

- In one terminal window `cd` into the launcher extension folder and build the extension:

```bash
cd gst
jlpm
pip install -e .
jlpm run build
jupyter labextension develop . --overwrite
jlpm run watch
```

- In the second tab run jupyter lab

```bash
jupyter lab
```

---