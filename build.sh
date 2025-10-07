#!/usr/bin/env bash
# This script tells Render how to build the application,
# avoiding the pywin32 error by installing keyauth without its dependencies.

# Exit immediately if a command exits with a non-zero status.
set -o errexit

# Upgrade pip
pip install --upgrade pip

# 1. Install the keyauth library by itself, ignoring its dependencies (like pywin32).
pip install keyauth==1.0.2 --no-deps

# 2. Install all the other libraries as normal from the requirements.txt file.
pip install -r requirements.txt
