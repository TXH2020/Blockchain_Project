# Blockchain_Project

## Setup: Can be installed in windows and linux
1. Install Postgres. Create user admin_ems with password iamadmin@123
2. Install ipfs desktop.
3. Make sure postgres runs on port 5432 and ipfs runs on port 5001
4. Clone this repository. Goto the cloned folder. Create a python virtual environment using `` python -m venv virtualvenv ``
5. Activate the virtual environment using `` virtualenv\Scripts\activate `` in Windows and `` source virtualenv/bin/activate `` in Linux
6. Install all packages using `` pip install -r requirements.txt ``
7. Then follow the following steps:
- `` python manage.py makemigrations ``
- `` python manage.py migrate ``
- `` python manage.py runserver `` to start the server
