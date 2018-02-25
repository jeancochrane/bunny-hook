# Bunny Hook
🐇↩️ A simple but flexible webhook for deploying any kind of app directly from GitHub.

## Why use Bunny Hook?

Bunny Hook is useful for build and deployment setups that are too complicated for a static hosting provider, but too simple to merit using a complicated setup through a service like Jenkins or AWS CodeDeploy. With Bunny Hook, you can **build and deploy any app to any kind of server by pushing to a dedicated deployment branch on GitHub.**

Bunny Hook lets you define your builds and deployments in a sequence of bash scripts that will get run every time you push to a registered deployment branch on GitHub. Focus on writing code and let Bunny Hook do your deploying for you.

## Requirements

OS-level requirements:
- `git`
- `rsync`
- `bash`

These libraries are built-in on the majority of systems. If you're missing any, install them with your favorite package manager.

Install Python requirements with `pip`:

```bash
pip install -U -r requirements.txt
```

Copy the dummy secrets file so you can begin developing:

```bash
cp api/secrets.py.example api/secrets.py
```

## Running the hook

The hook requires two processes to run, an app server and a build queue. These processes are defined in the scripts `runserver.py` and `runqueue.py` respectively.

To run the hook locally, run one script in a shell:

```bash
# Run the app server
python runserver.py
```

Then, run the second script in another shell:

```bash
# Run the build queue
python runqueue.py
```

## Deploying the app

To deploy Bunny Hook to a server, you'll need some way of A) managing the two processes and B) exposing the app to the Internet so that it can receive payloads from GitHub. I like to use **supervisord** and **nginx** for these two tasks.

## Registering a new repo

Registering a new repo with Bunny Hook requires setting up a new webhook in the project's GitHub settings page. For context on how to setup a webhook, see [GitHub's documentation](https://developer.github.com/webhooks/creating/). You'll need to:

1. Add a new hook that sends a payload to `https://<hostname>/hooks/github/<deploy_branch>`
2. Register the new hook with a secret token
3. Update the secrets file (`api/secrets.py`) in your running instance of the app and add the new token to the `TOKENS` list
4. Restart the app server process to acknowledge your new token

To run a deployment, simply push a commit to the deployment branch that you registered (`deploy_branch`), and let Bunny Hook do its thing!

## Configuring a build

Bunny Hook expects a configuration file called `deploy.yml` to live in the root of your repo. Here's what `deploy.yml` should look like:

```yaml
# deploy.yml -- config file for build scripts

# Where you want the files to live on the server (Bunny Hook will clone the files here)
- home: "/path/to/your/repo/"

# Scripts to run before the build
# (e.g. decrypting build scripts or other secrets)
prebuild:
  - scripts/prebuild.sh

# Scripts to run during the build
# (e.g. compiling and minifying code)
build:
  - scripts/build.sh

# Scripts to run for deploying the app
# (e.g. restarting processes)
deploy:
- scripts/deploy.sh
```

There are three different kinds of deployment scripts you can define: **`prebuild`**, **`build`**, and **`deploy`**. Note that Bunny Hook expects these to be bash scripts and runs them naively, so the three kinds of scripts are functionally interchangeable in that they get run in the exact same fashion. Anything that you can put in `prebuild` can also go in `build`, and vice versa. The only caveat is that scripts will always get run in this order:

1. `prebuild`
2. `build`
3. `deploy`

So if you need things to happen sequentially, make sure to write them into the correct build script.

## Running tests

The tests use Python's builtin `unittest` framework. Use the `discover` subcommand to run the full suite:

```bash
python -m unittest discover -s tests
```

Note that `tests/test_integration.py` does some filesystem manipulation to make sure that cloning repos, moving files, and running bash commands/scripts works as expected. 
