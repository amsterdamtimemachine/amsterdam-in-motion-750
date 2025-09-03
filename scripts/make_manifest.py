import json
from datetime import datetime, timezone
import pandas as pd
import iiif_prezi3

iiif_prezi3.config.configs["helpers.auto_fields.AutoLang"].auto_lang = "nl"
iiif_prezi3.load_bundled_extensions()

URI_PREFIX = "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/"


def main(df_protest, df_photo, df_classification, target_folder="iiif"):
    """
    Generates IIIF manifests from protest and photo data.

    Data structure df_protest:
    slug	naam	beschrijving	datum_start	datum_eind	locatie's	classificatie's	thumbnail (foto op homepage)	wikidata	extra informatie

    Data structure df_photo:
    index	uri	protest	naam	beschrijving	datum_start	datum_eind	fotograaf	archief	url	locatie	iiif_canvas_id	iiif_info_json

    Args:
        df_protest (pd.DataFrame): DataFrame containing protest data.
        df_photo (pd.DataFrame): DataFrame containing photo data.
    """

    classification_label2concept = dict()
    for _, row in df_classification.iterrows():
        classification_label2concept[row["prefLabel"]] = {
            "@id": row["uri"],
            "@type": "skos:Concept",
            "skos:prefLabel": {"@language": "nl", "@value": row["prefLabel"]},
        }

    collection = iiif_prezi3.Collection(
        id=URI_PREFIX + "collection.json",
        label="Protest - Amsterdam in Motion 750",
        summary="Overzicht van protestfoto's uit Amsterdam.",
        items=[],
    )

    for _, protest_row in df_protest.iterrows():

        slug = protest_row["slug"]
        manifest_uri = URI_PREFIX + slug + ".json"

        print(manifest_uri)

        datum_start = protest_row["datum_start"]

        # Create nav_date in Europe/Amsterdam timezone at midnight from YYYY-mm-dd
        if pd.isna(datum_start):
            nav_date = None
        else:
            ts = pd.to_datetime(datum_start, format="%Y-%m-%d", errors="coerce")
            if pd.isna(ts):
                nav_date = None
            else:
                ts = (
                    ts.tz_localize("Europe/Amsterdam")
                    if ts.tzinfo is None
                    else ts.tz_convert("Europe/Amsterdam")
                )
                nav_date = ts.isoformat()

        protest_sdo = {
            "@type": "schema:Event",
            "schema:name": protest_row["naam"] if pd.notna(protest_row["naam"]) else "",
            "schema:description": (
                protest_row["beschrijving"]
                if pd.notna(protest_row["beschrijving"])
                else ""
            ),
            "schema:startDate": {
                "@type": "xsd:date",
                "@value": protest_row["datum_start"][:10],
            },
            "schema:endDate": {
                "@type": "xsd:date",
                "@value": protest_row["datum_eind"][:10],
            },
            "schema:location": [
                {
                    "@type": "schema:Place",
                    "schema:name": (
                        protest_row["locatie's"]
                        if pd.notna(protest_row["locatie's"])
                        else ""
                    ),
                }
            ],
            "schema:additionalType": [
                classification_label2concept.get(i.strip())
                for i in protest_row["classificatie's"].split(", ")
                if i in classification_label2concept
            ],
        }

        manifest = iiif_prezi3.Manifest(
            id=manifest_uri,
            label=protest_row["naam"] if pd.notna(protest_row["naam"]) else "",
            summary=(
                protest_row["beschrijving"]
                if pd.notna(protest_row["beschrijving"])
                else ""
            ),
            items=[],
            navDate=nav_date,
            metadata=[
                # iiif_prezi3.KeyValueString(label={"nl": ["Naam"]}, value={"nl": [protest_row['naam'] if pd.notna(protest_row['naam']) else ""]}),
                # iiif_prezi3.KeyValueString(label={"nl": ["Beschrijving"]}, value={"nl": [protest_row['beschrijving'] if pd.notna(protest_row['beschrijving']) else ""]}),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Datum (begin)"]},
                    value={
                        "nl": [
                            (
                                str(protest_row["datum_start"][:10])
                                if pd.notna(protest_row["datum_start"])
                                else ""
                            )
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Datum (eind)"]},
                    value={
                        "nl": [
                            (
                                str(protest_row["datum_eind"][:10])
                                if pd.notna(protest_row["datum_eind"])
                                else ""
                            )
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Locatie's"]},
                    value={
                        "nl": [
                            (
                                protest_row["locatie's"]
                                if pd.notna(protest_row["locatie's"])
                                else ""
                            )
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Classificatie's"]},
                    value={
                        "nl": [
                            (
                                protest_row["classificatie's"]
                                if pd.notna(protest_row["classificatie's"])
                                else ""
                            )
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Classificatie's (URI)"]},
                    value={
                        "nl": [
                            ", ".join(
                                [
                                    classification_label2concept[i.strip()]["@id"]
                                    for i in protest_row["classificatie's"].split(", ")
                                    if i in classification_label2concept
                                ]
                            )
                        ]
                    },
                ),
            ],
        )

        # Add photos to the manifest
        for i, photo_row in df_photo[
            df_photo["protest"] == protest_row["naam"]
        ].iterrows():

            if pd.isna(photo_row["iiif_info_json"]):
                continue

            canvas_id = f"{URI_PREFIX}{slug}/p1/canvas/{i+1}"

            manifest.make_canvas_from_iiif(
                url=photo_row["iiif_info_json"],
                id=canvas_id,
                anno_page_id=canvas_id + "/page",
                anno_id=canvas_id + "/anno",
                label=photo_row["naam"] if pd.notna(photo_row["naam"]) else "",
                metadata=[
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Naam"]},
                        value={
                            "nl": [
                                photo_row["naam"] if pd.notna(photo_row["naam"]) else ""
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Beschrijving"]},
                        value={
                            "nl": [
                                (
                                    photo_row["beschrijving"]
                                    if pd.notna(photo_row["beschrijving"])
                                    else ""
                                )
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Datum (begin)"]},
                        value={
                            "nl": [
                                (
                                    str(photo_row["datum_start"][:10])
                                    if pd.notna(photo_row["datum_start"])
                                    else ""
                                )
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Datum (eind)"]},
                        value={
                            "nl": [
                                (
                                    str(photo_row["datum_eind"][:10])
                                    if pd.notna(photo_row["datum_eind"])
                                    else ""
                                )
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Fotograaf"]},
                        value={
                            "nl": [
                                (
                                    photo_row["fotograaf"]
                                    if pd.notna(photo_row["fotograaf"])
                                    else ""
                                )
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Archief"]},
                        value={
                            "nl": [
                                (
                                    photo_row["archief"]
                                    if pd.notna(photo_row["archief"])
                                    else ""
                                )
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["URL"]},
                        value={
                            "nl": [
                                photo_row["url"] if pd.notna(photo_row["url"]) else ""
                            ]
                        },
                    ),
                    iiif_prezi3.KeyValueString(
                        label={"nl": ["Locatie"]},
                        value={
                            "nl": [
                                (
                                    photo_row["locatie"]
                                    if pd.notna(photo_row["locatie"])
                                    else ""
                                )
                            ]
                        },
                    ),
                ],
            )

        with open(f"{target_folder}/{slug}.json", "w", encoding="utf-8") as f:
            manifest_jsonld = json.loads(manifest.json())
            manifest_jsonld["@context"] = [
                "http://iiif.io/api/extension/navplace/context.json",
                "http://iiif.io/api/presentation/3/context.json",
            ]
            manifest_jsonld["seeAlso"] = [protest_sdo]
            json.dump(manifest_jsonld, f, indent=2, ensure_ascii=False)

        collection.add_item(manifest)

    # Save the collection as a JSON file
    with open(f"{target_folder}/collection.json", "w", encoding="utf-8") as f:
        collection_jsonld = json.loads(collection.json())
        json.dump(collection_jsonld, f, indent=2, ensure_ascii=False)

    print("Collection generated and saved to collection.json")


if __name__ == "__main__":

    df_protest = pd.read_excel(
        "data/Amsterdam in Motion 750 - Data.xlsx", sheet_name="Protest"
    )

    # parse datum_start and datum_eind as string
    df_protest["datum_start"] = df_protest["datum_start"].astype(str)
    df_protest["datum_eind"] = df_protest["datum_eind"].astype(str)

    df_photo = pd.read_excel(
        "data/Amsterdam in Motion 750 - Data.xlsx", sheet_name="Foto"
    )

    df_photo["datum_start"] = df_photo["datum_start"].astype(str)
    df_photo["datum_eind"] = df_photo["datum_eind"].astype(str)

    df_classification = pd.read_excel(
        "data/Amsterdam in Motion 750 - Data.xlsx", sheet_name="Classificatie"
    )

    main(df_protest, df_photo, df_classification)
