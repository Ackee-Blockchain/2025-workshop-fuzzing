# Install Wake on Windows

We will install wake and anvil for testing.

## Installing Wake

Open PowerShell and run:

```bash
> python
```

If Python is not installed, install Python 3.13 from the Microsoft Store.

Close PowerShell and open it again, then run:

```bash
pip install eth-wake
```

The installation may fail and ask you to install the C++ build tool.

Download the C++ build tool from suggested url(microsoft) and run the installation tool.

When installing the build tool, do not forget to select `Desktop development with C++`.

After installation, close and open PowerShell again and run:

```bash
pip install eth-wake
```

The installation should succeed with a warning about adding a path.

Open Settings, search for and open "Environment Variables".

Add the pip-given path to the `PATH` variable.

Close and open PowerShell again and run:

```bash
wake
```

This should show the usage of Wake

## Installing Anvil

Install Git from https://git-scm.com/downloads/win

After installation, open File Explorer, navigate to a folder, right-click, click `Show more options`, and select `Open Git Bash Here`.

Run:

```bash
curl -L https://foundry.paradigm.xyz | bash
```

Close Git Bash.

Open Git Bash again the same way and run:

```bash
foundryup
```

Add the environment variable path: `C:\Users\{username}\.foundry\bin`

Close PowerShell.
