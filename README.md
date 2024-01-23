# Quizmaster 
This repository contains the web application 'The Quiz Boutique', which is a quiz creation, playing and hosting tool, powered by Django, and created using Python (Backend) and HTML, CSS, JavaScript and Django Template (Front End). While this can be used live, it is also intended
for everyday usage by anyone to wants to host or play quizzes with friends and family.

## About the Quiz Boutique

### Registration
To use the Quiz Boutique, you must sign up by creating a username and password.

### Names and Team Members
Registered users can create a public name (your author name for created content), a team name, and team members with optional member avatars.

### Quiz creation
Quizzes can be created and set as either private or public. Private quizzes are only accessible via a URL, and can be password protected (default), while public quizzes can be found via the 'Browse' page. Each quiz can have a title, description, and upto 4 categories.

### Question creation
Questions always require 4 answers, and can include a text based question, or text plus an image or audio file. There is a limit of 200 questions per quiz.

### Playing Quizzes
Quizzes that are listed as public can be played by any user at anytime, and gives a simple question/multi-choice answer process until the final score is awarded. It's also possible to play a public quiz with friends, by providing them with the URL, and then at the end of quiz players are ranked. Private quizzes
must be hosted by the author.

### Hosted Quizzes
For hosted quizzes by the author, quizzes can be played with a family or friends, and players can either give open answers for more points (3 points), or answer based on the multi-choice answer (1 point). Open answers are checked automatically, but if they do not based the answer
in the database directly, then the host is able to mark as correct or incorrect. The final scores are ranked at the end.

## How to run the application
The application is currently in debug mode, which means it can easily be run from your PC/laptop. However, to do so this requires a few steps. Please see below some basic instructions on installing the application.

### Installation
Required software:
* Python (https://www.python.org/downloads/)
* Visual Studio (VS) Code (https://code.visualstudio.com/download)

VS Code Setup (after installing VS Code):
* Install the Python (Microsoft!) extension
* Select the Python interpretor (help here: https://code.visualstudio.com/docs/python/environments)
* In the terminal, install the dependencies ('pip install django' and 'pip install pillow')

Running the project
* Open the folder with all the files in VS Code (your terminal will show showing like: 'C:\Users\YOURNAME\Documents\quizmaster')
* In the terminal, type 'python manage.py runserver', to start the test server
* Now simply navigate to the development server URL e.g. 'http://127.0.0.1:8000/'

### Sharing with friends and family in your local wifi Network
If you have successfully installed, and have the application running, then you may be ready to play quizzes with friends and family. If they're connected to your home wifi network, it's very easy:

* Identify your PC/laptop's IP address by opening CMD, and typing ipconfig. Look for the IPv4 Address, something like 192.168.0.10
* Run the project with this IP address. In the terminal type: 'python manage.py runserver 192.168.0.10:8000'
* Anyone who wants to join, can type '192.168.0.10:8000' into their browser, PC or smartphone browsers are all fine.

It's also possible to play with friends not on your wifi network, but you'll need to configured Port Forwarding on your router. 







