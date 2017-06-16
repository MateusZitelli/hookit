# Hookit

> WebHooks management and monitoring tool

Hookit automatically creates and listen to GitHub WebHooks, running a specified command after push events.

* Simple usage - see [example](#usage)
* Signated WebHooks by default 
* No dependencies

## Setup

Download and make Hookit Python script available for usage:

```sh
curl https://raw.githubusercontent.com/MateusZitelli/hookit/master/hookit > /usr/local/bin/hookit; chmod +x /usr/local/bin/hookit
```

## Usage

Create an access token [here](https://github.com/settings/tokens/new) with the `write:repo_hook` scope.

With the GitHub access token in hands create a configuration file named `.env`:

```sh
GITHUB_ACCESS_TOKEN=<The created Access Token>
REPOSITORY_NAME=Username/Repository
CALLBACK_URL=http://HOST:PORT
HOOK_SECRET=<An hash to be used for validation>
ON_PUSH_CALL=echo "Such a push"
```

And then execute Hookit

```sh
hookit
```

Now every push to the repository `Username/Repository` will trigger the script `echo "Such a push"`.

## Licence

[MIT License](http://opensource.org/licenses/MIT)
