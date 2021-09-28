# PACE 2021 S2 - EY Data and Analytics

## Overview

This is the current master branch for the development of the web based application for COVID-19 compliance analysis. Further changes will follow. 

## Setup Option 1 - Via local host

1. **Clone the Template Repo**

Clone a local copy of the repo onto your machine and `cd` into the project directory.

    $ git clone https://github.com/Noah-Carpenter/pace-2021-s2-group-37.git -b Master
    $ cd pace-2021-s2-group-37
    
 2. Install requirements via cmd terminal
```
$ pip install -r requirements.txt
```
W
 3. Launch app via cmd terminal
```
$cd app
$python app.py
```

## Setup Option 2 - Docker

1. **Clone the Template Repo**

Clone a local copy of the repo onto your machine and `cd` into the project directory.

    $ git clone https://github.com/Noah-Carpenter/pace-2021-s2-group-37.git -b Master
    $ cd pace-2021-s2-group-37

2. **Spin up the Docker Containers**

The applicaion built using Flask UI. For ease of use, a Docker Compose file has been set up in order to build the application in one command:

    $ docker-compose up --build

3. **Check the App is working!**

If your installation has worked correctly you should see your Flask application is visitable at the following url http://localhost:5000. 
