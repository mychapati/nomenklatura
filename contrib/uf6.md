# Open Data Enrichment / Integration Service API

This experimental API assembles relevant public data about a set of
companies, organizations or people. Such data could includes any
relevant facts, from company records to social network profiles.

Data is collected from remote services upon request: when a user
requests more information about an entity (or a set of entities),
relevant spiders are activated and tasked to retrieve information about
similar entities from on-line databases.

Once data has been retrieved for an entity, an assessment of whether these
results are correct matches to the initial request is performed and fitting candidate results are returned to the user.

## Domain Model

As this is an exercise in data integration, it makes sense to adopt a
Linked Data-inspired data model. In such a model, there is no
un-ambiguous set of attributes that a person or company has. Instead,
all information is given in the form of statements, which assign a 
property value to an entity. Each statement is part of a context, which
states the source of the information and how trusted it is.

Assessing whether a given entity in the context A is the same as another
entity in context B then becomes an explicit mapping task which may 
require user input.


## Spider API

Spiders must have an easy-to-use API which they can use to receive
search requests from the system core and generate potential matches.


## Web API

Submitting a crawl request:

```
POST /api/1.0/crawl
```

This expects a JSON-formatted search query, and will return a simple crawl ID reference which the client can check as spider information is retrieved. This is an example request:

```json
{
    "entities": [
        {
            "type": "Company",
            "label": "Chevron Inc."
        },
        {
            "type": "Person",
            "label": "William Gates"
        }
    ]
}
```

A response could look like this:

```json
{
    "status": "pending",
    "crawl_id": "5b5b9278-0bf7-4cb6-9e7f-289bb9a893e1",
    "crawl_uri": "http://uf6.service.org/api/1/crawls/5b5b9278-0bf7-4cb6-9e7f-289bb9a893e1"
}
```


## Origins

The design of this API is inspired by discussions on the
[uf6 (data enrichment)](http://github.com/uf6) group. It can also be
seen as a scoping experiment for the upcoming SuperTraMp project.



