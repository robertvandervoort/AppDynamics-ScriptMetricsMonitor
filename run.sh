#!/bin/bash

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Function to find the Python 3 executable
get_"$PYTHON3"() {
    for executable in "$PYTHON3" python; do
        if command -v "$executable" >/dev/null 2>&1 && "$executable" --version 2>&1 | grep -q "Python 3"; then
            echo "$executable"
            return
        fi
    done
    echo "Error: No suitable Python 3 executable found." >&2
    exit 1
}

# Find the Python 3 executable
"$PYTHON3"="$(get_"$PYTHON3")"

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    # Determine the shell type
    SHELL_TYPE="$(basename $SHELL)"

    # Activate virtual environment based on shell type
    case "$SHELL_TYPE" in
        zsh)
            source "$VENV_DIR"/bin/activate
            ;;
        bash | sh)
            . "$VENV_DIR"/bin/activate  
            ;;
        csh | tcsh)
            source "$VENV_DIR"/bin/activate.csh
            ;;
        *)
            echo "Unsupported shell type: $SHELL_TYPE"
            exit 1
            ;;
    esac

    # Check if requirements are already installed (redirecting stderr to /dev/null)
    if ! "$PYTHON3" -m pip list --format=freeze --disable-pip-version-check 2>/dev/null | grep -q -F -f "$REQUIREMENTS_FILE"; then 
        echo "Installing missing requirements from $REQUIREMENTS_FILE..."
        "$PYTHON3" -m pip install -r "$REQUIREMENTS_FILE" --disable-pip-version-check

        if [ $? -ne 0 ]; then
            echo "Failed to install requirements. Exiting."
            exit 1
        fi
    fi
else
    echo "Virtual environment not found. Creating..."

    # Create virtual environment (adjust for your Python version if needed)
    "$PYTHON3" -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Exiting."
        exit 1
    fi

    # Install requirements (since venv was just created)
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "Installing requirements from $REQUIREMENTS_FILE..."
        # Activate the virtual environment first before installing requirements.
        . "$VENV_DIR"/bin/activate 
        "$PYTHON3" -m pip install -r "$REQUIREMENTS_FILE" --disable-pip-version-check

        if [ $? -ne 0 ]; then
            echo "Failed to install requirements. Exiting."
            exit 1
        fi
    fi
fi

# Execute Python script using the found Python 3 executable within the venv
"$VENV_DIR"/bin/python AsyncScriptMetricsMonitor.py

# Optionally, deactivate the virtual environment after the script finishes
deactivate 
