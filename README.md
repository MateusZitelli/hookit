<h1 align="center">
Hookit
<br/>
<i>WebHooks as easy as it can get</i>
<br/>
<img width=150 src="https://cdn.rawgit.com/MateusZitelli/hookit/9f57d2aaac0eb2903d941f35a34b27edf773cf94/assets/logo.svg" ></img>
</h1>

Hookit automatically creates and listens to GitHub WebHooks, running a specified command after push events.

* Simple usage - see the [example](#usage).
* Signated WebHooks by default.
* No dependencies.

[![Hookit usage](https://raw.githubusercontent.com/MateusZitelli/hookit/master/assets/preview.gif)](https://asciinema.org/a/125096)

## Setup

Download and **make Hookit Python script available** for usage:

```sh
$ curl https://raw.githubusercontent.com/MateusZitelli/hookit/master/hookit > /usr/local/bin/hookit; chmod +x /usr/local/bin/hookit
```

## Usage

### 1. Create GitHub Access Token

**Create an access token** [here](https://github.com/settings/tokens/new) with the `write:repo_hook` scope.

<img width=800 src="https://cdn.rawgit.com/MateusZitelli/hookit/master/assets/access-token-info.png" ></img>

### 2. Create a configuration file

With the GitHub access token in hands **create a configuration file** named `.env`:

```
GITHUB_ACCESS_TOKEN=<The created Access Token>
REPOSITORY_NAME=Username/Repository
CALLBACK_URL=http://HOST:PORT
HOOK_SECRET=<A hash to be used for validation>
ON_PUSH_CALL=echo "Such a push"
```

### 3. Execute Hookit
And then **execute Hookit** on the folder with the `.env` file:

```sh
$ hookit
```

Now every push to the repository `Username/Repository` will trigger the script `echo "Such a push"`.

## Licence

[MIT License](http://opensource.org/licenses/MIT)

