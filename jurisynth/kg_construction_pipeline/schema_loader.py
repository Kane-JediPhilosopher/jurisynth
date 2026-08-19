from rdflib import RDF, RDFS, OWL, Namespace, Graph
import rdflib
import os

def extract_resources(graph, resource_type):
    """
    Extract resources of a given RDF type.

    Returns:
        resources: URI -> label
        metadata: URI -> metadata dict
    """

    resources = dict()
    metadata = dict()

    resource_types = {
        "class": OWL.Class,
        "object property": OWL.ObjectProperty,
        "datatype property": OWL.DatatypeProperty,
        "datatype": RDFS.Datatype
    }

    chosen_type = resource_types[resource_type]

    deprecated_count = 0

    for uri in set(graph.subjects(RDF.type, chosen_type)):

        if isinstance(uri, rdflib.term.BNode):
            continue

        label = graph.value(uri, RDFS.label)
        comment = graph.value(uri, RDFS.comment)

        label = (
            str(label)
            if label
            else uri.split("#")[-1]
        )

        comment = (
            str(comment)
            if comment
            else ""
        )

        # --------------------------------------------------
        # Detect deprecated resources
        # --------------------------------------------------

        is_deprecated = False

        deprecated = graph.value(uri, OWL.deprecated)

        if deprecated is not None:
            if str(deprecated).casefold() == "true":
                is_deprecated = True

        if "deprecated" in label.casefold():
            is_deprecated = True

        if "deprecated" in comment.casefold():
            is_deprecated = True

        if is_deprecated:
            deprecated_count += 1
            continue

        # --------------------------------------------------
        # Build NLP-friendly resource description
        # --------------------------------------------------

        text = label

        if comment:
            text += ". " + comment

        resources[str(uri)] = label

        metadata[str(uri)] = {
            "type": resource_type,
            "label": label,
            "comment": comment,
            "text": text,
            "domain": (
                set(graph.objects(uri, RDFS.domain))
                if resource_type in {"object property", "datatype property"}
                else set()
            ),
            "range": (
                set(graph.objects(uri, RDFS.range))
                if resource_type in {"object property", "datatype property"}
                else set()
            )
        }

    print(
        f"Filtered {deprecated_count} deprecated "
        f"{resource_type.replace('_', ' ')} resources."
    )

    return resources, metadata

def main():
    # Define your own custom namespaces for your knowledge graph:
    JS_DATA = Namespace("http://jurisynth/data/")
    JS_SOURCE = Namespace("http://jurisynth/source/")

    # Load schema/ontology files, if any
    schema_folder = "../schema"
    schema_files = [os.path.join(schema_folder, file) for file in os.listdir(schema_folder)]

    schema_graph = Graph()

    index = 1
    for file in schema_files:
        schema_graph.parse(file, format="xml")
        print(f"Finished parsing RDF file {index}.")
        index += 1

    print()

    # Only retrieves declared namespaces
    schema_namespaces = set(schema_graph.namespaces())

    print("Schema Namespaces:")
    for ns in schema_namespaces:
        print(ns)

    print()

    # Classes
    classes, class_metadata = extract_resources(schema_graph, "class")
    print(f"Found {len(classes)} classes.")

    # Object properties
    obj_properties, obj_metadata = extract_resources(schema_graph, "object property")
    print(f"Found {len(obj_properties)} object properties/relations.")

    # Datatype properties
    datatype_properties, data_prop_metadata = extract_resources(schema_graph, "datatype property")
    print(f"Found {len(datatype_properties)} datatype properties/relations.")

    # Datatypes
    datatypes, datatype_metadata = extract_resources(schema_graph, "datatype")
    print(f"Found {len(datatypes)} datatypes.")

    # Resource Metadata
    resource_metadata = dict()

    resource_metadata.update(class_metadata)
    resource_metadata.update(obj_metadata)
    resource_metadata.update(data_prop_metadata)
    resource_metadata.update(datatype_metadata)

    rdf_resources = list(classes.keys()) +  list(obj_properties.keys()) + list(datatype_properties.keys()) + list(datatypes.keys())
    rdf_dict = {**classes, **obj_properties, **datatype_properties, **datatypes}

if __name__ == "__main__":
    main()