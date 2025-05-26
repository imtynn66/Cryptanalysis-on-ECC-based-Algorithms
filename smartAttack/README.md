# Smart's Attack Demo on ECC

This project demonstrates **Smart's Attack** on an ECC system where the trace of Frobenius is 1. The demo includes a vulnerable ECC server and a client that exploits this vulnerability to recover the private key and decrypt a challenge message.

## 📁 File Structure

* `server.py`: ECC server with a curve vulnerable to Smart's Attack.
* `client.py`: Client to perform the attack and decrypt the server's challenge.
* `run_demo.py`: Script to automatically launch the server and then run the client after a short delay.

## Requirements

Make sure you have the following installed:

* [SageMath](https://www.sagemath.org/) (>= 9.0)
* Python 3.x
* Python packages:

  * `pycryptodome`

### Install dependencies (Ubuntu/Debian example)

```bash
sudo apt install sagemath
pip install pycryptodome
```

Or using Sage's Python:

```bash
sage -pip install pycryptodome
```

## How to Run

1. Open terminal and ensure you're in the project directory.
2. Run the demo script using Sage:

```bash
sage -python run_demo.py
```

This will:

* Start the ECC server.
* Wait 3 seconds for it to initialize.
* Launch the client which:

  * Retrieves the server's public curve info.
  * Performs Smart's Attack to recover the private key.
  * Decrypts a secret challenge using the recovered key.




