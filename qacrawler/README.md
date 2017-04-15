# Build

## Virtual environment

If you prefer to work in a new Python virtual environment first create one via 
A) [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) (easier) or
B) [virtualenv](https://virtualenv.pypa.io)

A) `mkvirtualenv qasearch` to create the environment. 
(By default this creates `~/.virtualenvs/qasearch/` directory.) 
Then `workon qasearch` to activate the environment.

B) `virtualenv ENV_DIR` to create the environment.
Then `source ENV_DIR/bin/activate` to activate the environment.

## Requirements 

Type `pip install -r requirements.txt` in the project folder to install the required Python packages. 
(If you don't create a virtual environment packages will be added to your system Python installation) 

# Drivers

Put driver executables to system's PATH. (Ugur: "I sudo-copied them into `/usr/local/bin`" ^_^)

- [Chrome driver](https://sites.google.com/a/chromium.org/chromedriver/downloads).
- [Firefox driver](https://developer.mozilla.org/en-US/docs/Mozilla/QA/Marionette/WebDriver). 
    - Use [v0.9.0](https://github.com/mozilla/geckodriver/releases/tag/v0.9.0) 
    - For some reason you have to rename the executabe to `wires` (from `geckodriver`)
    

# Run

Example command to run the crawler.

```
$ workon PROJECT_VIRTUAL_ENVIRONMENT
$ cd /PROJECT_GIT_REPOSITORY_FOLDER/qacrawler
$ python main.py --jeopardy-json PATH_TO_JEOPARDY_QUESTIONS1.json --first 0 --last 1000 --output-folder OUTPUT_FOLDER --wait-duration 2 --log-level DEBUG --driver Firefox --disable-javascript --num-pages 1 --results-per-page 50
```

Then to follow the logs `tail -f jeopardy_crawler.log`.
