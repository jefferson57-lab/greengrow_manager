# GreenGrow Stock Manager CLI

A Command Line Interface (CLI) application for managing seedling inventory and sales for a nursery or personal plant collection. This project demonstrates the use of Python with SQLAlchemy ORM, Click for CLI development, and Pipenv for dependency management.

## Features

* **Tree Type Management:** Add and list different types of tree seedlings with their base selling prices.
* **Location Management:** Define and list various storage locations for your seedlings.
* **Stock Management:**
    * Add new batches of seedlings to specific locations.
    * View current inventory, filtered by type or location.
    * Move quantities of seedlings between different locations.
* **Sales Tracking:**
    * Record sales transactions, which automatically decrement stock from inventory.
    * View a history of all sales, with optional date filtering.

## Technologies Used

* **Python 3.8+:** The core programming language. Specifically tested for 3.8.13 compatibility.
* **SQLAlchemy ORM:** For interacting with the database in an object-oriented way.
* **SQLite:** A lightweight, file-based database used for local storage (`store.db`).
* **Click:** A modern, type-hint based library for building robust CLIs.
* **Pendulum:** For easier and more intuitive date and time handling.
* **Pipenv:** For managing project dependencies and creating isolated virtual environments.

## Setup Instructions

1.  **Clone the repository (if applicable) or create the project structure:**

    ```bash
    mkdir greengrow_manager
    cd greengrow_manager
    # Ensure all the Python files and the Pipfile are created within this directory
    ```

2.  **Install Pipenv (if you don't have it):**

    ```bash
    pip install pipenv
    ```

3.  **Install Project Dependencies using Pipenv:**

    Navigate to the `greengrow_manager` directory in your terminal. **Crucially, specify Python 3.8:**

    ```bash
    pipenv --python 3.8 install
    ```
    This command tells Pipenv to create (or use) a virtual environment with Python 3.8 and install all dependencies listed in the `Pipfile` into that environment.

4.  **Activate the Virtual Environment:**

    ```bash
    pipenv shell
    ```
    Your terminal prompt should change (e.g., to `(greengrow_manager) $`), indicating that the virtual environment is active. You must be in this environment to run the commands.

5.  **Initialize the Database:**

    Before you can use the application, you need to create the database file and its tables. This command will create a file named `store.db` in your `greengrow_manager` directory.

    ```bash
    python -m greengrow_manager.main init
    ```

## Usage

Make sure your Pipenv virtual environment is active (`pipenv shell`).

All commands are executed using the Python interpreter within the virtual environment, targeting the `main.py` module.

**General Command Structure:**

```bash
python -m greengrow_manager.main [COMMAND] [ARGS] [OPTIONS]