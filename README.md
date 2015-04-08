# nomenklatura

Nomenklatura is an entity database for information about companies, people and their relationships. It provides a comprehensive interface and API to query, de-duplicate and integrate different entities - people, organisations or public bodies. It helps clean imported source data to turn it into domain-specific intelligence.

## Features

* A full investigative data toolkit with a focus on modelling corporate structures, 
  connections between people, organizations and companies.
* A comprehensive graph query API inspired by [Freebase MQL](https://developers.google.com/freebase/mql/index).
* Interactive data enrichment via structured data spiders, with automatic queries to [OpenCorporates](https://opencorporates.com/) and a variety of other public databases.
* Each fact is associated with full source information, and material from specific sources
  can be revoked and re-introduced at will.
* Bulk data import from CSV and Excel with an interactive data model builder.
* Tools for user-controlled data de-duplication based on datamade's [dedupe](https://github.com/datamade/dedupe) library.
* Support for the [OpenRefine Reconciliation API](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API) to clean source data.

## How to use it

The software can be configured to model custom domains and load data in a variety of contexts. To keep the code base simple, each instance of ``nomenklatura`` will only host a single dataset and contain a single schema. This means that if you want to manage several fully separate data projects, you will need to deploy the platform multiple times.

## Implementation

``nomenklatura`` uses an RDF-inspired, specialised data representation. It is focussed on storing and integrating data about entities such as people, companies and other organisations.

Key features include:

* Information about entities is stored as a set of statements, i.e. properties with additional information attached to them.
* Data is stored in a SQL database internally to make it easy to query.
* Statements (and hence entities) are associated with contexts, which store comprehensive provenance information (data source, trust level, etc.)
* Data can be exported to flat files and re-imported easily.

The underlying ontology for the data can be modified, and stored in a YAML file located at: ``nomenklatura/fixtures/schema.yaml``. Core types like ``Object``, ``Node`` and ``Link`` should not be changed, while higher-level types and attributes can be extended and changed at will.

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

If you encounter any issues while installing numpy, please [refer to the package documentation](http://docs.scipy.org/doc/numpy/user/install.html). You may need to install a C and FORTRAN compiler.

Next, you need to customize the configuration file. Copy the template configuration file, ``settings.py.tmpl`` to a new file, e.g. ``settings.py`` in the project root, and set the required settings indicated in the template. Then export the environment variable ``NOMENKLATURA_SETTINGS`` to point at this file:

```bash
cp settings.py.tmpl settings.py
# edit settings.py
export NOMENKLATURA_SETTINGS =`pwd`/settings.py
```

You will also need to create a database in Postgres with the encoding set to UTF-8. To enable data reconciliation, please execute the folloing SQL command with superuser privileges:

```sql
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
```

To download all JavaScript dependencies, fixture country data and to create a new database, run the following command:

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

If you want to integrate this into a production environment, refer to the configurations in both the ``Procfile`` and the ``Makefile``, and consider using ``gunicorn`` to run the web clients.

## Contact, contributions etc.

``nomenklatura`` is developed as part of an [ICFJ Knight International Journalism](http://icfj.org) fellowship and the Open Societies-funded project "[Supercharging Transparency Mapping](http://influencemapping.org)". It has previously been developed with generous support from [Knight-Mozilla OpenNews](http://opennews.org) and the [Open Knowledge Foundation Labs](http://okfnlabs.org).

The codebase is licensed under the terms of an MIT license (see LICENSE.md).
