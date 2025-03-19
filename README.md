# Nougat

A lightweight Python utility for safely accessing deeply nested dictionary values.

## Overview

Nougat solves the common problem of accessing nested dictionary values without raising KeyError exceptions. It provides a clean, chainable interface for traversing nested dictionaries, returning a default value when any key in the path doesn't exist.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nougat.git

# Install directly with pip
pip install git+https://github.com/yourusername/nougat.git
```

## Usage

```python
from nougat import initNougat

# Initialize a dictionary
data = {
    "user": {
        "profile": {
            "name": "John Doe",
            "address": {
                "city": "New York"
            }
        }
    }
}

# Add nougat method to your dictionary
initNougat(data)

# Safely access nested values
city = data.nougat("user", "profile", "address", "city")  # Returns "New York"
country = data.nougat("user", "profile", "address", "country")  # Returns None (default)

# Specify a custom default value
country = data.nougat("user", "profile", "address", "country", default="Unknown")  # Returns "Unknown"

# Works with any depth of nesting
nonexistent = data.nougat("user", "settings", "theme", "color")  # Returns None, no errors
```

## Features

- Zero dependencies - just pure Python
- Works with any dict-like object that implements a `get()` method
- Customizable default values
- Handles any depth of nesting
- Lightweight and fast

## When to Use Nougat

- Accessing configuration values that might not exist
- Processing API responses with varying structures
- Handling user input or preferences with optional fields
- Any situation where you need to safely navigate nested dictionaries

## License

MIT
