# The OWL Change Ontology

## Purpose and scope

The purpose of this project is to provide an ontology for tracking changes in OWL ontologies over time. It is designed to facilitate the detection, representation, and documentation of modifications, such as the addition, removal, or renaming of classes, properties, and individuals. By explicitly capturing the nature and context of changes, this ontology aims to improve version management, change analysis, and collaboration in ontology engineering projects.

This ontology is particularly valuable for:

**Ontology developers**: To track and document updates made to ontologies during development and maintenance cycles.

**Ontology users**: To understand how an ontology evolves and assess the impact of updates on their use cases.

**Tools and workflows**: To support automated processes for comparing ontology versions, generating changelogs, and integrating change-tracking into ontology lifecycle management tools.
The scope of this ontology includes, but is not limited to:

**Change representation**: A framework to represent types of changes (e.g., addition, deletion, renaming...) at various OWL entities (classes, properties, individuals).
**Provenance and context**: Capturing metadata about the changes, such as who made the change, when it was made, and what changes are related to it.
**Integration**: Compatibility with existing OWL standards, enabling adoption in ontology engineering workflows.

By providing a formalized and interoperable way to track ontology changes, this project supports transparency, reproducibility, and informed decision-making in ontology development and use.

## Vocabulary development
This ontology is developed following the guidelines provided by the [LOT methodology](https://lot.linkeddata.es/). 

### Requirements
The set of requirements for the OWL Change Ontology are written as a set of competency questions,  see the [Ontology Requirements Specification Document](requirements/). 

### Ontology model

The following diagram shows a general overview of the classes and properties of the Conceptual Mapping vocabulary. This diagram follows the [Chowlk notation](https://chowlk.linkeddata.es/notation.html). For a complete description of the ontology constructs, see the [documentation](http://w3id.org/def/och).

<p align="center"> 
 <img src="./diagrams/diagram.png?raw=true" alt="schema" width="950"/> 
</p>

### Ontology (OWL)
The encoded core ontology in OWL can be found [here](ontology/ontology.ttl). 

### Shapes
To check that a change KG is compliant with the OCH ontology, shapes SHACL are provided in the [shapes folder](shapes/).

### Mappings
To generate a change KG with the OCH ontology, we provide a mapping template in [YARRRML](https://w3id.org/kg-construct/yarrrml) in the [mappings folder](mappings/)

### Examples
Some examples of how the language can be used to describe data for RDF transformation is shown in the [examples folder](examples/).

## Contribute
The management of issues and improvements suggested for this vocabulary is done by addressing [issues]() in the repository. If you are interested in collaborate with us in a new version of the language, send us an email or open a new issue or discussion!

## Authors
* Diego Conde-Herreros
* María Poveda Villalón
* Romana Pernisch
* David Chaves-Fraga
