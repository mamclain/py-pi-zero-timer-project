# py-pi-zero-timer-project

## About:
A Simplistic Python Project to Provide a Web GUI Controlled Timer (with hour, minute, second controls) to toggle a Pi Zero Rely Hat on the Timeout Event.

## Notes:
I am currently waiting to obtain a physical PI zero and relay hat, thus this code will have that portion missing until these items arrive.

Currently this project is just a minimalist Flask web app that is consolidated within run.py, If a real interest in this project occurs I will consider packaging a proper class with inheritable callbacks

## Usage:
The current use case would be to fork this source and modify the following run.py functions: 
* pi_after_timer_event
* pi_before_timer_event
* pi_timer_event_abort 

to perform the desired PI-Zero IO operations as needed...

Python 3 should be installed on the pi-zero

`pip install -r requirements.txt` should be run to install the required dependencies

the use of a virtual environment (`python -m venv .\venv`) on the pi is optional.

`systemd` or `rc.local` should be used where needed to launch the web server if a startup application is desired.

A primitive web GUI is provided to control, monitor, and cancel the timer.

This GUI is currently accessible to anyone with network access to the pi... if added security is needed, it is recommended that additional steps are taken to limit network access.


This Web Frontend utilizes: 
* Bootstrap
* Knockout.js
* JQuery
* CoffeeScript 
    - Note: This requires compilation of `.coffee` files at the developer "backend" level.
         
The Python Backend utilizes:
* Flask 
    - Note: A Flask PUG plugin was used, thus  no developer compilation for `.pug` files is required.

## Other Thoughts:
There is plenty of room for improvement, customize as needed, Have Fun!





  
  

