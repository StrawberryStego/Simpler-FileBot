# Simpler FileBot 🗃️
This is a batch file-renaming GUI tool for movies and tv shows.

`Simpler FileBot is built using PySide6 and is designed with Windows 11 in mind!`

*Special thanks* to [guessit](https://github.com/guessit-io/guessit) for analyzing and providing the metadata for filenames.

## Requirements
**You might be able to skip this section if using the Executable installation option.**

- [Python 3.10 - 3.14](https://www.python.org/downloads/) - 
  `Installation help:` [[Windows](https://www.geeksforgeeks.org/how-to-install-python-on-windows/)] [[Mac](https://www.geeksforgeeks.org/how-to-install-python-on-mac/)] [[Linux](https://www.geeksforgeeks.org/how-to-install-python-on-linux/)]

  Make sure `pip` is installed and `Python` is added to your environment variables.

## Modern PySide6 UI
<img src="https://github.com/user-attachments/assets/5168d8e2-c09d-46ba-99f4-dbcf78b573a2" width="75%">

## Light & Dark Mode
<img src="https://github.com/user-attachments/assets/a5d634e1-1861-4c98-b5e3-9d962c2afa35" width="75%">

## Installation
[Download Source Code](https://github.com/StrawberryStego/Simpler-FileBot/releases)

### Executable (Currently only for Windows)

- Download `Simpler-FileBot.exe` from the Releases section

- Run the executable

### Python

- `pip install -r requirements.txt`

- `py main.py`

### Windows
- `Run install_dependencies.bat`

- `Use launcher.bat to open Simpler FileBot`

## Supported Databases
`Simpler FileBot uses the following databases/APIs but is not endorsed, certified, or otherwise approved.`

<br/><br/>

<img src="https://static.tvmaze.com/images/tvm-header-logo.png" alt="Alt Text" height="50">

[Source](https://www.tvmaze.com/) [[Python Library](https://github.com/yakupadakli/python-tvmaze)]

<br/><br/>

<img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_long_1-8ba2ac31f354005783fab473602c34c3f4fd207150182061e425d366e4f34596.svg" alt="Alt Text" width="300">

[Source](https://www.themoviedb.org/) [[Python Library](https://github.com/celiao/tmdbsimple/)] (Requires an API key at [Link](https://www.themoviedb.org/settings/api))

<br/><br/>

<img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Omdb-logo.png" alt="Alt Text" width="height=40">

[Source](https://www.omdb.org/en/us) [[Python Library](https://github.com/dgilland/omdb.py)] (Requires an API key at [Link](https://www.omdbapi.com/apikey.aspx))

<br/><br/>

### `Simpler FileBot also supports matching solely using the guessit library.`
