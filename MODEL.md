# Statement-based storage

``nomenklatura`` uses an RDF-inspired, specialised graph representation.
It is focussed on storing and integrating data about entities such as
people, companies and other organisations.

Key features include:

* Information about entities is stored as a set of statements, i.e. 
  properties with additional information attached to them.
* Data is stored in a SQL database internally to make it easy to
  query.
* Statements (and hence entities) are associated with contexts, which
  store comprehensive provenance information (data source, trust level,
  etc.)
* Data can be exported to flat files and re-imported easily.


