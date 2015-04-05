# Open Data Enrichment / Integration Service

## Candidates for data enrichment

* https://www.personadeinteres.org/personas/1760
* http://api.corpwatch.org/ 

## Rationale

This experimental API assembles relevant public data about a set of
companies, organizations or people. Such data could includes any
relevant facts, from company records to social network profiles.

Data is collected from remote services upon request: when a user
requests more information about an entity (or a set of entities),
relevant spiders are activated and tasked to retrieve information
about similar entities from on-line databases.

Once data has been retrieved for an entity, an assessment of whether
these results are correct matches to the initial request is
performed and fitting candidate results are returned to the user.

## Domain Model

As this is an exercise in data integration, it makes sense to
adopt a Linked Data-inspired data model. In such a model, there
is no un-ambiguous set of attributes that a person or company has.
Instead, all information is given in the form of statements, which
assign a property value to an entity. Each statement is part of a
context, which states the source of the information and how
trusted it is.

Assessing whether a given entity in the context A is the same as
another entity in context B then becomes an explicit mapping task
which may require user input.

## Spider API

Spiders must have an easy-to-use API which they can use to receive
search requests from the system core and generate potential matches.

## Origins

The design of this API is inspired by discussions on the
[uf6 (data enrichment)](http://github.com/uf6) group. It can also be
seen as a scoping experiment for the upcoming SuperTraMp project.

## Loom data model

```python
is_a = Predicate('type', 'Type', 'is a', implicit=False)
label = Predicate('label', 'Label', 'is called', implicit=True)
alias = Predicate('alias', 'Alias', 'is also known as', implicit=False)
url = Predicate('url', 'URL', 'is described at', implicit=True)
identity = Predicate('identifier', 'Identifier', 'is identified as',
                     implicit=True)

# company
jurisdiction = Predicate('jurisdiction', 'Jurisdiction',
                         'in the jurisdiction', implicit=True)
company_number = Predicate('company_number', 'Company number',
                           'with the company number', implicit=True)
company_type = Predicate('company_type', 'Company type',
                         'has the legal form', implicit=True)

# officer
officer_of = Predicate('officer', 'Officer', 'is an officer of')
position = Predicate('position', 'Position', 'with the role', implicit=True)
start_date = Predicate('start_date', 'Start date', 'started at', implicit=True)
end_date = Predicate('end_date', 'End date', 'ended at', implicit=True)
```
