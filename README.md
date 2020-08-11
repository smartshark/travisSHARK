# TravisSHARK
[![Build Status](https://travis-ci.org/smartshark/travisSHARK.svg?branch=master)](https://travis-ci.org/smartshark/travisSHARK)

## Introduction

This introduction highlights the requirements of **travisSHARK**, how it is installed, tested, and executed. 
Furthermore, a small tutproal in the end will show step by step how travisSHARK can be used. In the end, we highlight 
how travisSHARK can be extended.

Travisshark is used to gather and parse build logs from [Travis](http://travis-ci.org). It gathers meta-data about
builds (e.g., how long the build took, what it end status was, etc.) and their jobs. For each job log file parsers
are executed, which can add more information to the Travis Job model that is later on stored in the database.

We use a vanilla Ubuntu 16.04 operating system as basis for the steps that we describe. If necessary, we give hints
on how to perform this step with a different operating system.

**This software is still in development**


### Documentation
TODO

### Model Documentation
The documentation for the used database models can be found [here](https://smartshark.github.io/pycoSHARK/api.html).

### Installation
The installation process is straight forward. For a vanilla Ubuntu 16.04, we need to install the following packages:

	sudo apt-get install git python3-pip python3-cffi

Furthermore, you need a running MongoDB. The process of setting up a MongoDB is
explained here: https://docs.mongodb.com/manual/installation/


After these requirements are met, first clone the **travisSHARK**[repository](https://github.com/smartshark/travisSHARK/>)
repository to a folder you want. In the following, we assume that you have cloned the repository to **~/travisSHARK**. 
Afterwards, the installation of **travisSHARK** can be done in two different ways:

#### via Pip
    sudo pip3 install https://github.com/smartshark/travisSHARK/zipball/master --process-dependency-links
    
#### via setup.py
    sudo python3.5 ~/travisSHARK/setup.py install


Note that it is advisable to change the location, where the logs are written to.
They can be changed in the **loggerConfiguration.json**. There are different file handlers defined.
Just change the "filename"-attribute to a location of your wish.

### Tests
The tests of **travisSHARK** can be executed by calling
    
    python3.5 ~/travisSHARK/setup.py test
    
The tests can be found in the folder "tests", but they just test the **basic** functionality.


### Execution
In this chapter, we explain how you can execute **travisSHARK**. Furthermore, the different execution parameters are
explained in detail.

1) Checkout the repository from which you want to collect the data.

2) Make sure that your MongoDB is running!
    ```
    sudo systemctl status mongodb
    ```

3) Execute [vcsSHARK](https://github.com/smartshark/vcsSHARK) on the checked our project


4) Execute **travisSHARK** by calling
    ```
	python3.5 ~/travisSHARK/main.py
    ```

**travisSHARK** supports different commandline arguments:

--help, -h: shows the help page for this command

--version, -v: shows the version

--db-user <USER>, -U <USER>: mongodb user name; Default: None

--db-password <PASSWORD>, -P <PASSWORD>: mongodb password; Default: None

--db-database <DATABASENAME>, -DB <DATABASENAME>: database name; Default: smartshark

--db-hostname <HOSTNAME>, -H <HOSTNAME>: hostname, where the mongodb runs on; Default: localhost

--db-port <PORT>, -p <PORT>: port, where the mongodb runs on; Default: 27017

--db-authentication <DB_AUTHENTICATION> -a <DB_AUTHENTICATION>: name of the authentication database; Default: None

--ssl: enables ssl for the connection to the mongodb; Default: False

--debug <DEBUG_LEVEL>, -d <DEBUG_LEVEL>: Debug level (INFO, DEBUG, WARNING, ERROR); Default: DEBUG

--url, -u: VCS url of the project that should be analyzed

--ignore-errors: Switch on, if errors should be ignored

--only-failed: Switch on, if only failed jobs should be mined

--rerun: Switch on, if you want to rerun on all builds

--token <TOKEN>, -t <TOKEN>: Token to use for accessing Travis (see: https://developer.travis-ci.com/authentication)

--proxy-host <PROXYHOST>, -PH <PROXYHOST>: Proxy hostname or IP address; Default: None

--proxy-port <PROXYPORT>, -PP <PROXYPORT>: Port of the proxy to use; Default: None

--proxy-password <PROXYPASSWORD>, -Pp <PROXYPASSWORD>: Password to use the proxy (HTTP Basic Auth); Default: None

--proxy-user <PROXYUSER>, -PU <PROXYUSER>: Username to use the proxy (HTTP Basic Auth); Default: None


### Tutorial

In this section we show step-by-step how you can collect travis data from the project
 [zxing](https://github.com/zxing/zxing) and store the data in a mongodb.

1.	First, if you need to have a mongodb running (version 3.2+).
How this can be achieved is explained here: https://docs.mongodb.org/manual/.

2. Add zxing to the projects table in MongoDB.
    ```
	mongo
	use smartshark
	db.project.insert({"name": "zxing"})
	```

3. Install [vcsSHARK](https://github.com/smartshark/vcsSHARK). 

4. Enter the **vcsSHARK** directory via
    ```
    cd vcsSHARK
    ```

5. Clone the zxing repository to your home directory (or another place)
    ```
    git clone https://github.com/zxing/zxing ~/zxing
    ```
    
6. Execute **vcsSHARK**:
    ```
    cd ~/vcsSHARK
    python3.5 ~/vcsSHARK/vcsshark.py -D mongo -DB smartshark -H localhost -p 27017 -n zxing --path ~/zxing
    ```

7. Install **travisSHARK**. An explanation is given above.

8. Enter the **travisSHARK** directory via
    ```
		$ cd travisSHARK
    ```
9. Test if everything works as expected

    ```
    python3.5 main.py --help
    ```

10. Execute **travisSHARK**:
    ```
    cd ~/travisSHARK
    python3.5 main.py -DB smartshark -H localhost -p 27017 -u https://github.com/zxing/zxing -t <TOKEN> --ignore-errors --only-failed
    ```

Thats it. The results are explained in the database documentation
of [SmartSHARK](http://smartshark2.informatik.uni-goettingen.de/documentation/).