# nomenklatura

Nomenklatura is an entity database for information about companies, people and their relationships. It provides a comprehensive interface and API to query, de-duplicate and integrate different entities - people, organisations or public bodies. It helps clean imported source data to turn it into domain-specific intelligence.

## Installation

Before you can install ``storyweb``, the following dependencies are required:

* Python, and ``virtualenv``.
* Postgres, newer than 9.3.
* ``less`` and ``uglify-js``, installed via ``npm``.
* RabbitMQ for background process queueing

On a Debian-based operating system, this would come down to the following commands:

```bash
add-apt-repository -y ppa:chris-lea/node.js && apt-get update
apt-get install -y nodejs libpq-dev rabbitmq-server postgresql-9.4
npm install -g bower less uglify-js
```

Once these dependencies are satisfied, run the following commands to install the application:

```bash
git clone https://github.com/pudo/nomenklatura nomenklatura
cd nomenklatura
virtualenv env
source env/bin/activate
pip install "numpy>=1.9"
pip install -r requirements.txt
pip install -e .
```

Next, you need to customize the configuration file. Copy the template configuration file, ``settings.py.tmpl`` to a new file, e.g. ``settings.py`` in the project root and set the required settings. Then export the environment variable ``NOMENKLATURA_SETTINGS`` to point at this file:

```bash
cp settings.py.tmpl settings.py
export NOMENKLATURA_SETTINGS =`pwd`/settings.py
```

To download all JavaScript dependencies, country reference data and to create a new database, run the following command:

```bash
make install
```

Congratulations, you've installed ``nomenklatura``. You can run the application using:

```bash
make web
```

You will also need to operate a background worker process, launched via:

```bash
make worker
```

## Contact, contributions etc.

nomenklatura is developed as part of an ICFJ Knight International Journalism fellowship and the Open Societies-funded project "Supercharging Transparency Mapping". It has previously been developed with generous support from [Knight-Mozilla OpenNews](http://opennews.org) and the [Open Knowledge Foundation Labs](http://okfnlabs.org).

The codebase is licensed under the terms of an MIT license (see LICENSE.md).
