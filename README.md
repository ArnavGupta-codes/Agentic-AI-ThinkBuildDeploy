# Python Primer

This directory contains all the python code that was discussed in Lec-2. For your own reference it's advised to learn the basics of python from [geekforgeeks](https://www.geeksforgeeks.org/python/introduction-to-python/)

```
project/
├── call_model
|   └── main.py
├── file_handling
|   ├── data.json
|   └── file_handling.py
├── oops
|   ├── car.py
|   ├── main.py
|   └── vehicle.py
├── 1-intro.py
├── 2-types.py
├── 3-numbers.py
├── 4-strings.py
├── 5-arrays.py
├── 6-comparision.py
├── 7-conditionals.py
├── 8-functions.py
├── 9-loops.py
└── README.md
```

## Running LLMs Locally

Our implementation of running LLMs locally involves the user of Docker so it is recommended to download Docker Desktop and downloading a small model like Gemma (used in the lecture) for use.

Docker Model Runner runs the model on our RAM and provides us with an endpoint to interact with the model which has been utilised to call it in /call_model/main.py

Below this is given a short guide to Virtual Environments in Python.


# Virtual Environments

## What is a virtual environment?

A virtual environment (venv) is an isolated Python environment that has its own Python interpreter and installed packages, separate from the system-wide Python installation.

## Why are virtual environments important?

### Virtual environments help you:

- Avoid dependency conflicts
  Different projects can require different versions of the same package.

- Keep projects reproducible
  Dependencies installed in a venv can be listed in requirements.txt and recreated exactly.

- Protect system Python
  Prevents accidentally breaking OS-level or globally installed Python packages.

- Match production environments
  Ensures the same package versions locally and in deployment.

## Creating and using a venv

### Create a virtual environment
```
python -m venv env_name
```

### Activate (Linux / macOS)
```
source env_name/bin/activate
```

### Activate (Windows)
```
env_name\Scripts\activate
```

### Deactivate
```
deactivate
```


Once activated, all pip install commands install packages only inside the venv and not on the system wide installation

## Best practices

- Create one venv per project

- Never commit the venv/ directory to git

- Always commit requirements.txt

- Activate the venv before running or installing anything

### Feel free to discuss any queries in class or reach out to any instructor on Whatsapp