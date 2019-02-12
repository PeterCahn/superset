# Superset on Docker

This repository contains the Dockerfile and the related files to run an instance of Superset on Docker.

It starts and extends the image of *amancevice* ([GitHub](https://github.com/amancevice/superset) / [Docker Hub](https://hub.docker.com/r/amancevice/superset/)) by adding some customizations, mainly small fixes for an ad-hoc usage in an enterprise environment.

## Main features

* Double login mode:
    * **Standard**
    
        Built-in login mode through the standard login form (*username/password*).
        The first user (Admin role) is generated through the *superset-init* script to access the web UI.
        
    * **Shibboleth**
    
        External Single Sign-On system to authenticate the users.
        Some custom code reads Shibboleth configuration headers which have been set after the login on the Shibboleth system, check resources on Superset (creates *users* if not present and assigns them a *role* according to Shibboleth info) and *redirects* the user to the page it has called.

* JDBC Dremio Connector

    A JDBC Dremio Connector ([ahmadimtcs/sqlalchemy_dremio](https://github.com/ahmadimtcs/sqlalchemy_dremio)) has been added to connect to an instance of Dremio in Superset.

    [This tips](https://github.com/apache/incubator-superset/issues/4192#issuecomment-424148215) have been followed and the script [install-dremio.sh](https://github.com/PeterCahn/superset/blob/master/superset/bin/install-dremio.sh) is in charge of implementing the main installation steps.
    
    The resources provided in *superset/lib/python3.6/site-packages/superset/dataframe.py* and *superset/lib/python3.6/site-packages/superset/sql_lab.py* are parts of the installation procedure as well and are added directly through the Dockerfile. 

## Execution

### Custom configuration

A configuration script can be added by providing its path name into a volume attached to the image:
* `/etc/superset/`: the volume where to put the configuration file
* `PYTHON_CONFIG_PATH`: the environmental variable where to specify the complete path of the configuration script inside the previous (or another) volume (e.g. *PYTHON_CONFIG_PATH=/etc/superset/superset_config.py*)

The init script will read the configuration file if the environmental variable `PYTHON_CONFIG_PATH` is specified. If not, the [custom-config.py](https://github.com/PeterCahn/superset/blob/master/superset/bin/custom-config.py) (with the basic modifications) is used as default.

*P.S.: Start adding new properties from custom-config.py*

### Volumes
* `/etc/superset` and `/home/superset`

    These path are both included into the `PYTHONPATH` and can be used as volumes where to add custom configuration files.
    
* `/var/lib/superset`

    This volume corresponds to the data volume. Here it is stored the default SQLlite DB used as default metadata.

### Environment variables

*  `SUPERSETUSER`, `SUPERSETPASSWORD`, `SUPERSETFIRSTNAME`, `SUPERSETLASTNAME`, `SUPERSETEMAIL`:

    These are all optional variables used to initialize the first Superset user (with Admin role). 
    
    If none of them is specified, the user created will be *superset* with password '*password*' and an example email, first name and last name.
    
    If the first and last name are provided only, all the other will be set accordingly (e.g.: *username: first-name.last-name*, *email: first-name.last-name@csi.it*). You can still set the email, the username and the password to change them indipendently.
    
* `LOGOUT_REDICECTURL`: the URL where to redirect for the logout (needed for Shibboleth).
* `SHIB_HEADERS`: the list of comma separated strings representing the headers that Shibboleth will set to call the Superset login.
* `SUPERSET_CONFIG_PATH`: the complete path where to put the custom configuration file (e.g. */etc/superset/superset_config.py*). This path must be inside a Docker volume.
* `SQLALCHEMY_METADATA_URI`: the SQLalchemy string for connecting to the metadata DB. For example, ff changed to PostgteSQL, it would be something like this: *postgresql://username:password@hostname:port/db-name*.

You can set these variables in the `.env` file and reference them into a *docker-compose.yml*.

### Run

Use the `docker-compose.yml` to start Superset with its volumes and a PostgreSQL DB to use it as external DB for data or metadata.

