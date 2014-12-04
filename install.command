#!/bin/bash
sudo easy_install pip
pip install requests
pip install beautifulsoup4
pip install flask

open http://127.0.0.1:5000
python webscraper.py
