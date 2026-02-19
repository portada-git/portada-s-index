
# Development requirements

The objective of this document is to define the requirements for developing the library that will manage the calculation of similarity indices between citations (entity names) and their recognized voices (entity identifier names). Entities are often identified by multiple voices, so voices that identify the same entity are grouped under the abstract concept of "name" (see the [_preamble on disambiguation_ section of the document "_Process_flow_and_functions_for_curation_"](https://docs.google.com/document/d/1snHmADqL_xZrljKgl29TziMj90bVzKHKU8pgq9szyNc/edit?tab=t.0])).

In this project we are going to distinguish the cited entities, which appeared in different news and were extracted in the first phase of the project, and the known entities too. Each cited entity, will be composed by a structure with some optional fields plus the _id_ field and the _citated_name_ field. Each known entity, will be composed by a structure with some optional fields too, in addition to the _name_ field and the _voices_ field.

The library will be able to compare two lists of strings or combinations, and will generate a similarity matrix with all the similarity indices calculated for each pair of elements in the lists. 

The lists to be compared will, whenever possible, originate from known entities on one hand, and cited entities on the other. However, when it is necessary to work with unknown entities, that is, without the corresponding list of names and voices, the comparison will be made between two identical lists of their corresponding citations.

Using the similarity matrix, this library will be able to build different summary outputs.

## Inputs

The global inputs will consist of lists of known entities, lists of entity citations, and the configuration corresponding to the entity type to be processed. This configuration defines the specific comparison system and  method for each entity type. There are several entity types. For some, we will have lists of known entities, but for others, we will not. To process an entity type with a list of known entities, we will use both lists. For entity types without known entities, we will generate the similarity matrix by comparing the citations with each other.

### Configuration input

The configuration is in dictionary format and contains:
 - Field or combination of fields to use in the comparison of the entity citation list (required). Its format will be a string or a string list.
 - Field or combination of fields to use when comparing known entities. This attribute is optional, as it will only be indicated if the entity type has known entities. Normally, if defined, it will refer to a single known entity type, but in some cases with combined citation lists, various known entity types may be involved. Therefore, its format will contain a field, a list of fields, or a key-value set where the key indicates the known list type name and the value indicates the field or list of fields involved.
 - List of configurations for each similarity algorithm to be used in the comparison process (required). Each item list specifies: the algorithm name, a range of two values ​​indicating the acceptance threshold, the gray area, and the rejection threshold and a pondered vote rate. 

### Data input 
As data input we consider:
 - List of entity citations (required), which contains items with the citation referred to the name of one entity, the identifier and, optionally, the set of fields that act as characteristics or attributes associated to the cited entity.
 - List of the known entities if exists (optional). Known entity items are a structure with two fields, the name and the voice. The name can be repeated in several items, as can the voices. However, the combination of name and voice will be unique.

### More inputs
The name of the entity type will be passed too as extra information to add to the outputs.

## Outputs
We consider the similarity matrix as an output, because it is important information both to show and to calculate more information needed to the research.

In addition, the library can return too, several kind of outputs calculated using the similarity matrix.

### Similarity matrix
The similarity matrix is a 3-diemsional matrix of NxMxA, where N is the number of entity citations, M is the number of voices, and A is the number of algorithms applied. In those cases that entities are unknown, M will be equal to N.

### Statistical report
We define statistical report as structured information about the calculated similarity matrix. The report will contain:
 - The name of the entity type processed
 - The number of all citations
 - The number unique citations
 - The number of voices
 - The configuration used as a copy of the configurations used during the process
 - Results classified in 4 containers: agreed (when the qualified majority finds similarity above the accepted threshold in the same voice), weakly agreed (when the unqualified majority finds similarity with the same voice), gray zone (when the majority of votes are in the gray zone - between the acceptance threshold and the rejection threshold) and rejected (when none of the above conditions are met). Each container has total results (counters) and detailed results (each unique citation with the voices associated by different algorithms).  

### Result matrix
[TODO: ++/+-/-+/--]

## Architecture
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTY0NzgyOTY2LC0xNzE0MzYzOTU4XX0=
-->