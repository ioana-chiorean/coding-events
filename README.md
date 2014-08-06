coding-events
=============

[![Build Status](https://travis-ci.org/codeeu/coding-events.svg?branch=master)](https://travis-ci.org/codeeu/coding-events)

This is an app that let's you add [Code Week](http://events.codeweek.eu/) events and displays them on a map.


Contributing
=======
Fork this repository, and clone it to your local machine (of course, use your own username instead of {username}):

	git clone https://github.com/{username}/coding-events.git
	cd coding-events

Install things in virtualenv.

Install requirements (first time):

	pip install -r requirements.txt
	
On a Mac use Homebrew to install `geoip`:

	brew install geoip
	
You'll also need `saas`, which is a ruby package that you need to have installed, so you can install it using:

	gem install sass
		
Create new user and environment:

	./manage.py setupdb
	./manate.py migrate


Make your changes, push to your fork and create a new Pull Request.

(Thanks!).

Bugs
=======
Please [open an issue](https://github.com/codeeu/coding-events/issues).


