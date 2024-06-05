# Nillion Python Helpers

This helpers are meant to be used with Nillion's Python Quickstart. This are meant not to be copied every time we need to include them in a separate project, as they have become the standard.

## Installation
### Using pip

```bash
pip install nillion-python-helpers
```

### From Sources
You can install the nada-algebra library using Poetry:

```bash
git clone https://github.com/NillionNetwork/nillion-python-helpers.git
pip3 install 
```

## Usage

The program contains a script that allows for the execution of run-local-cluster without needing to have it in the specific directory. It will also create a `.env` file in the directory where executed.
```bash
bootstrap-local-environment
```

To kill the Nillion Devnet:
```bash
bootstrap-local-environment --kill
```
## License

This project is licensed under the Apache2 License. See the LICENSE file for details.