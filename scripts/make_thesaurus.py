from pyld import jsonld
import json


def main(
    thesaurus_file, mapping_file, context_file, output_file="thesaurus/thesaurus.json"
):

    with open(thesaurus_file, "r") as f:
        thesaurus = json.load(f)

    with open(mapping_file, "r") as f:
        mapping = json.load(f)

    with open(context_file, "r") as f:
        context = json.load(f)

    compacted_thesaurus = jsonld.compact(thesaurus, context)

    for concept in compacted_thesaurus["@graph"]:
        concept_id = concept["@id"]
        if concept_id in mapping:
            concept["_TD"] = mapping[concept_id]

    with open(output_file, "w") as f:
        json.dump(compacted_thesaurus, f, indent=2)


if __name__ == "__main__":

    PP_THESAURUS_FILE = "data/pp_scheme_protestthesaurus.jsonld"
    TD_MAPPING_FILE = "data/TD_thesaurus.json"
    CONTEXT_FILE = "data/thesaurus_context.json"

    main(PP_THESAURUS_FILE, TD_MAPPING_FILE, CONTEXT_FILE)
