## Binder
Binder allows you to create custom computing environments that can be shared and used by many remote users. It is powered by BinderHub, which is an open-source tool that deploys the Binder service in the cloud. One-such deployment lives here, at [mybinder.org](https://mybinder.org/)

### What is a Binder?

A Binder (also called a Binder-ready repository) is a code repository that contains at least two things:

1. Code or content that you’d like people to run. This might be a Jupyter Notebook that explains an idea, or an R script that makes a visualization.

2. Configuration files for your environment. These files are used by Binder to build the environment needed to run your code.
for more information [check](https://mybinder.readthedocs.io/en/latest/introduction.html)

### Configuration available files
For a list of all configuration files available:

- environment.yml - Install a Python environment

- Pipfile and/or Pipfile.lock - Install a Python environment
- requirements.txt - Install a Python environment¶
- setup.py - Install Python packages¶
- Project.toml - Install a Julia environment¶
- REQUIRE - Install a Julia environment (legacy)¶
- install.R - Install an R/RStudio environment
- apt.txt - Install packages with apt-get¶
- DESCRIPTION - Install an R package¶
- manifest.xml - Install Stencila¶
- postBuild - Run code after installing the environment¶
- start - Run code before the user sessions starts¶
- runtime.txt - Specifying runtimes¶
- default.nix - the nix package manager¶
- Dockerfile - Advanced environments¶

for more information [check](https://mybinder.readthedocs.io/en/latest/config_files.html#config-files)


#### In js-ng we made our configuration using on docker file

### Preparing your Dockerfile
For a Dockerfile to work on Binder, it must meet the following requirements:

1. It must install a recent version of Jupyter Notebook. This should be installed via pip with the notebook package. So in your dockerfile, you should have a command such as:

``` docker
RUN pip install --no-cache-dir notebook==5.*
```

2. It must explicitly specify a tag in the image you source.

When sourcing a pre-existing Docker image with FROM, a tag is required. The tag cannot be latest. Note that tag naming conventions differ between images, so we recommend using the SHA tag of the image.

Here’s an example of a Dockerfile FROM statement that would work
```docker
FROM jupyter/scipy-notebook:cf6258237ff9
```

###### Note

The following examples would not work:
```docker
FROM jupyter/scipy-notebook
```
or
```docker
FROM jupyter/scipy-notebook:latest
```

3. It must set up a user whose uid is 1000. It is bad practice to run processes in containers as root, and on binder we do not allow root container processes. If you are using an ubuntu or debian based container image, you can create a user easily with the following directives somewhere in your Dockerfile:

```docker
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
```

This is the user that will be running the jupyter notebook process when your repo is launched with binder. So any files you would like to be writeable by the launched binder notebook should be owned by this user.


4. It must copy its contents to the $HOME directory and change permissions.

To make sure that your repository contents are available to users, you must copy all contents to $HOME and then make this folder owned by the user you created in step 3. If you used the snippet provided in step 3, you can accomplish this copying with the following snippet:

``` docker
# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
```

This chown is required because Docker will be default set the owner to root, which would prevent users from editing files. Note that the repository should in general be clone with COPY; although RUN git clone ... is a valid command for the Dockerfile, it does not invalidate the build cache of mybinder. Thus, if available, the the cached repository will be used even after changes to the repository.

5. It must accept command arguments. The Dockerfile will effectively be launched as:

```bash
docker run <image> jupyter notebook <arguments from the mybinder launcher>
```
where <arguments …> includes important information automatically set by the binder environment, such as the port and token.

If your Dockerfile sets or inherits the Docker ENTRYPOINT instruction, the program specified as the ENTRYPOINT must exec the arguments passed by docker. Inherited Dockerfiles may unset the entrypoint with ENTRYPOINT [].

#### For more information about dockerfile in binder [check](https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html)

### How to use binder ?
after the docker file is ready place it in your repo. root

1. Go to [mybinder](https://mybinder.org/)
2. Enter github repository name or URL
3. Enter Git branch, tag or commit
4. Enter Path to notebook file
5. press launch

Then [mybinder] (https://mybinder.org/) will give you URL to share the Binder with others and it will build the image
