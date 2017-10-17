
Notify CKAN Extension
=========================

A CKAN extension to provide options for organizations to receive notifications when a data request (with the organization's name) is created, commented on or closed.
Only members of an organization who have the `Admin` role (or have authorization to manage the organization) are authorized to view or modify notification channels.
The interface (named `Channels`) which Notify extension exposes is available in the `Manage` section of every organization.

Requirements
------------

This extension requires an installation of CKAN. To install and set up CKAN, visit [CKAN Documentation](http://docs.ckan.org/en/latest/maintaining/installing/index.html)



Installation
------------

Step 1:

* Activate your virtual environment using the path to your virtual environment. If you have followed the default path when installing CKAN on Mac OSX, you may have to use `/usr/local/lib/ckan/default/bin/activate`. You can copy the code as is below, including the preceeding dot.

```bash
. /usr/lib/ckan/default/bin/activate
```

Step 2:

* Install the extension


>You can download the source code and install the extension manually. To do so, execute the following command:
> ```bash
> pip install -e git+https://github.com/CodeForAfricaLabs/ckanext-notify.git#egg=ckanext-notify
> ```
> **Alternatively**: You can clone this repo (preferably into the /src directory where you installed CKAN), cd into ckanext-notify and run
>```bash
> python setup.py develop
> ```


Step 3:

* Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `notify` to the `ckan.plugins` property.

```bash
ckan.plugins = notify <OTHER_PLUGINS>
```

Step 4:

* Restart your server:

```bash
paster serve /etc/ckan/default/production.ini
```

OR

```bash
paster serve --reload /etc/ckan/default/production.ini
```

With `--reload`, your server is restarted automatically whenever you make changes to your source code.


Support
-------

If you've found a bug/issue in the extension, please open a new issue [here](https://github.com/CodeForAfricaLabs/ckanext-notify/issues/new) (try
searching first to see if there's already an [issue](https://github.com/CodeForAfricaLabs/ckanext-notify/issues) for your bug).



Contributing to Notify CKAN Extension
---------------------------------------------

If you have interest in contributing to the development of Notify extension, you are welcome. A good starting point
will be reading the CKAN general [Contributing guide](http://docs.ckan.org/en/ckan-2.7.0/contributing/index.html). Then you can check out 
existing [issues](https://github.com/CodeForAfricaLabs/ckanext-notify/issues) that are open for contribution; new features and issues are welcome.
To work on any issue, comment on the issue to indicate your interest and the issue will be assigned to you. It is always a good idea to seek
for clarification (where necessary) on any issue before you work on it.

**It is important that changes that require some form of configuration be documented in the README.**

Copying and License
--------------------

This project is copyright (c) 2017 CodeForAfrica.

It is open and licensed under the MIT License.