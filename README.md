# Opengov.hk

We're making it easy to request information from the Hong Kong government! 

The Hong Kong government and civil service are bound by the [Code of Access to Information](http://www.access.gov.hk), but it's currently rather cumbersome to make a request for information under this Code. This website will change that, by making it as easy as writing a request in a textbox. It is inspired by the [UK](http://www.whatdotheyknow.com) and [German](https://fragdenstaat.de) Freedom of Information websites.

# The list of public bodies

There is currently no official directory of *email addresses* of Access to Information officers in Hong Kong, so we need to maintain one. Please help us by checking and editing our public spreadsheet which can be found at https://docs.google.com/spreadsheets/d/1x3WISjwPeC81n3GQTsqPxvKLnxpNehqyaWjdyCTX1bA/

# Translation

We want this website to function in both English and Chinese. Please help us in achieving this by providing translations at https://www.transifex.com/projects/p/froide/language/zh_HK/. Thank you so much for your help!

# Technical stuff

This is a basic Django project with a theme app that plugs into [Froide](https://github.com/stefanw/froide).

## Get started easily

In a Python virtualenv run:

    pip install -r requirements.txt -e .
    python manage.py syncdb --migrate
    python manage.py runserver


[Here is a complete guide of how to set this up on Heroku.](http://froide.readthedocs.org/en/latest/herokudeployment/)


## License

Froide Theme is licensed under the MIT License.
