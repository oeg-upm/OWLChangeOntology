# ELI ontological changelog

> Generated from `/Users/dchavesf/Documents/proyectos/student-thesis/diego/OWLChangeOntology/examples/ELI/eli_changelog.ttl`. **23 ontological changes.**

## Added (19)

### Annotations

- <a id="change-718015689520400"></a>**[cited_by](http://data.europa.eu/eli/ontology#cited_by)** `Add Annotation to Entity` [permalink](#change-718015689520400)
  - Added annotation on [eli:cited_by](http://data.europa.eu/eli/ontology#cited_by): [skos:historyNote](http://www.w3.org/2004/02/skos/core#historyNote) = "v1.5 : was made a subproperty of [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by) v1.2 : improved definition"@en
- <a id="change-718015690138000"></a>**[cited_by](http://data.europa.eu/eli/ontology#cited_by)** `Add Annotation to Entity` [permalink](#change-718015690138000)
  - Added annotation on [eli:cited_by](http://data.europa.eu/eli/ontology#cited_by): [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) = "modified in v1.5"^^[xsd:string](http://www.w3.org/2001/XMLSchema#string)
- <a id="change-718015690226200"></a>**[cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law)** `Add Annotation to Entity` [permalink](#change-718015690226200)
  - Added annotation on [eli:cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law): [skos:historyNote](http://www.w3.org/2004/02/skos/core#historyNote) = "v1.5 : was made a subproperty of [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)"@en
- <a id="change-718015690302600"></a>**[cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law)** `Add Annotation to Entity` [permalink](#change-718015690302600)
  - Added annotation on [eli:cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law): [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) = "modified in v1.5"@en
- <a id="change-718015690491800"></a>**[cites](http://data.europa.eu/eli/ontology#cites)** `Add Annotation to Entity` [permalink](#change-718015690491800)
  - Added annotation on [eli:cites](http://data.europa.eu/eli/ontology#cites): [skos:historyNote](http://www.w3.org/2004/02/skos/core#historyNote) = "v1.5 : was made a subproperty of [eli:refers_to](http://data.europa.eu/eli/ontology#refers_to)"@en
- <a id="change-718015690587900"></a>**[cites](http://data.europa.eu/eli/ontology#cites)** `Add Annotation to Entity` [permalink](#change-718015690587900)
  - Added annotation on [eli:cites](http://data.europa.eu/eli/ontology#cites): [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) = "modified in v1.5"@en
- <a id="change-718015692633600"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Add Annotation to Entity` [permalink](#change-718015692633600)
  - Added annotation on [eli:number](http://data.europa.eu/eli/ontology#number): [skos:historyNote](http://www.w3.org/2004/02/skos/core#historyNote) = "v1.5 : broaden the domain to Work or Expression instead of LegalResource or LegalExpression."@en
- <a id="change-718015692833200"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Add Annotation to Entity` [permalink](#change-718015692833200)
  - Added annotation on [eli:number](http://data.europa.eu/eli/ontology#number): [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) = "modified in v1.5"@en
- <a id="change-718015693227900"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Add Annotation to Entity` [permalink](#change-718015693227900)
  - Added annotation on [eli:number](http://data.europa.eu/eli/ontology#number): [rdfs:comment](http://www.w3.org/2000/01/rdf-schema#comment) = "An identifier or other disambiguating feature for a work or expression. This can be the number of a legislation, the number of an article, or the issue number of an official journal."@en

### Domains

- <a id="change-718015690818800"></a>**[is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)** `Add Domain` [permalink](#change-718015690818800)
  - Added domain [owl:Thing](http://www.w3.org/2002/07/owl#Thing) to [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)
- <a id="change-718015692900100"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Add Domain` [permalink](#change-718015692900100)
  - Added domain not specified to [eli:number](http://data.europa.eu/eli/ontology#number)
- <a id="change-718015691778700"></a>**[refers_to](http://data.europa.eu/eli/ontology#refers_to)** `Add Domain` [permalink](#change-718015691778700)
  - Added domain not specified to [eli:refers_to](http://data.europa.eu/eli/ontology#refers_to)

### Object properties

- <a id="change-718015690668300"></a>**[is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)** `Add Object Property` [permalink](#change-718015690668300)
  - Added object property: [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)
- <a id="change-718015690973100"></a>**[is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)** `Add Range Object Property` [permalink](#change-718015690973100)
  - Added object range not specified to [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)
- <a id="change-718015691544200"></a>**[refers_to](http://data.europa.eu/eli/ontology#refers_to)** `Add Object Property` [permalink](#change-718015691544200)
  - Added object property: [eli:refers_to](http://data.europa.eu/eli/ontology#refers_to)
- <a id="change-718015691708200"></a>**[refers_to](http://data.europa.eu/eli/ontology#refers_to)** `Add Range Object Property` [permalink](#change-718015691708200)
  - Added object range [owl:Thing](http://www.w3.org/2002/07/owl#Thing) to [eli:refers_to](http://data.europa.eu/eli/ontology#refers_to)

### Property relations

- <a id="change-718015689866600"></a>**[cited_by](http://data.europa.eu/eli/ontology#cited_by)** `Add Sub Property` [permalink](#change-718015689866600)
  - Added subproperty relation: [eli:cited_by](http://data.europa.eu/eli/ontology#cited_by) subproperty of [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)
- <a id="change-718015690359500"></a>**[cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law)** `Add Sub Property` [permalink](#change-718015690359500)
  - Added subproperty relation: [eli:cited_by_case_law](http://data.europa.eu/eli/ontology#cited_by_case_law) subproperty of [eli:is_referred_to_by](http://data.europa.eu/eli/ontology#is_referred_to_by)
- <a id="change-718015690424700"></a>**[cites](http://data.europa.eu/eli/ontology#cites)** `Add Sub Property` [permalink](#change-718015690424700)
  - Added subproperty relation: [eli:cites](http://data.europa.eu/eli/ontology#cites) subproperty of [eli:refers_to](http://data.europa.eu/eli/ontology#refers_to)

## Removed (4)

### Annotations

- <a id="change-718015683595800"></a>**[cited_by](http://data.europa.eu/eli/ontology#cited_by)** `Remove Annotation from Entity` [permalink](#change-718015683595800)
  - Removed annotation from [eli:cited_by](http://data.europa.eu/eli/ontology#cited_by): [skos:historyNote](http://www.w3.org/2004/02/skos/core#historyNote) = "v1.2 : improved definition"@en
- <a id="change-718015689156700"></a>**[cited_by](http://data.europa.eu/eli/ontology#cited_by)** `Remove Annotation from Entity` [permalink](#change-718015689156700)
  - Removed annotation from [eli:cited_by](http://data.europa.eu/eli/ontology#cited_by): [owl:versionInfo](http://www.w3.org/2002/07/owl#versionInfo) = "modified in v1.2"^^[xsd:string](http://www.w3.org/2001/XMLSchema#string)
- <a id="change-718015692058700"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Remove Annotation from Entity` [permalink](#change-718015692058700)
  - Removed annotation from [eli:number](http://data.europa.eu/eli/ontology#number): [rdfs:comment](http://www.w3.org/2000/01/rdf-schema#comment) = "An identifier or other disambiguating feature for a legal resource or legal expression. This can be the number of a legislation, the number of an article, or the issue number of an official journal."@en

### Domains

- <a id="change-718015692231000"></a>**[number](http://data.europa.eu/eli/ontology#number)** `Remove Domain` [permalink](#change-718015692231000)
  - Removed domain not specified from [eli:number](http://data.europa.eu/eli/ontology#number)
  - Remove Domain From Property: [eli:number](http://data.europa.eu/eli/ontology#number)

---

Generated by `tools/och_changelog_html.py`.
