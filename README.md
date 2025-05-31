### Volunteer Matchmaker

Volunteer Matchmaker is an app designed to automatically match volunteers with organizations based on key criteria such as area of interest, age and preferences.

#### 📌 Features

- Registration and structured storage of volunteer and organization data
- Matching algorithm based on defined attrbutes
- Logging of system actions and errors

#### 🛠️ Technologies used 

- Python 3
- PostgreSQL, pgadmin4
- basic customtkinter for GUI

#### 🚀 How to Run
- Create a virtual environment and activate it
  - macOS & Linux `python3 -m venv venv` `.\venv\Scripts\Activate.ps1`
  - Windows `python -m venv venv`, `venv\Scripts\Activate`
- Install dependencies `pip install -r requirements.txt`
- Fill all the missing private data in the code (`models.py`) and use your own database
- run `python main.py`
