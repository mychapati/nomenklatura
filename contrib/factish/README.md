# factish 

A factish is a simple format for storing and processing data that have 
provenance information associated with them. It is a line-based format,
based on notion of having RDF and CSV make babies.

It is intended to solve the problem of storing field-level attribution
in data, while remaining sane (fsvo sane). The need for such attribution exists when sharing data which has been integrated from multiple sources.


## Record types

A factish (``.fish``) contains three distinct types of records:

* ``Statements`` encapsulate the actual data, they could be fairly similar
  to RDF triples expressed in an n-quad format. What would be the 
  predicate of a triple is simply considered a field name, and lacks 
  semantics in the same way a CSV column header does.

* ``Source`` describes the origin of a set of statements, i.e. a web
  resource provided by an institution. Its description is given as a 
  set of DublinCore attributes. Future versions may assign a level of 
  trust to the source, e.g. differentiating between user-generated 
  content in a web application and data stemming from a government
  source.

* ``Attribution`` is the link between a statement and a source. It carries 
  metadata related to the process and circumstance during which the statement was derived from the source (e.g. when was it last updated, what type of
  program was used for transformation, where is the upstream data).


## Fun things to mess with

* GPG-signing individual statements via attributions.
* Do statements carry type information?


## Prior work

* [Open Provenance](http://openprovenance.org/)
* [Named Graphs, Provenance and Trust](http://wifo5-03.informatik.uni-mannheim.de/bizer/SWTSGuide/carroll-ISWC2004.pdf)
