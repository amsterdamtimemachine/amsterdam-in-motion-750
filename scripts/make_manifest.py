import json
from datetime import datetime, timezone
import pandas as pd
import iiif_prezi3

iiif_prezi3.config.configs["helpers.auto_fields.AutoLang"].auto_lang = "nl"
iiif_prezi3.load_bundled_extensions()

URI_PREFIX = "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/"


def main(df_protest, df_photo, target_folder="iiif"):

    """
    Generates IIIF manifests from protest and photo data.

    Data structure df_protest:
    slug	naam	beschrijving	datum_start	datum_eind	locatie's	classificatie's	thumbnail (foto op homepage)	wikidata	extra informatie

    Data structure df_photo:
    index	uri	protest	naam	beschrijving	datum	fotograaf	url	locatie	iiif_info_json

    Args:
        df_protest (pd.DataFrame): DataFrame containing protest data.
        df_photo (pd.DataFrame): DataFrame containing photo data.
    """

    c = iiif_prezi3.Collection(
        id="https://example.org/collection",
        label="Example Collection",
        summary="This is an example collection of IIIF resources.",
        items=[],
    )

    for index, protest_row in df_protest.iterrows():

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

        manifest = iiif_prezi3.Manifest(
            id=manifest_uri,
            label=protest_row["naam"],
            summary=protest_row["beschrijving"],
            items=[],
            navDate=nav_date,
            metadata=[
                # iiif_prezi3.KeyValueString(label={"nl": ["Naam"]}, value={"nl": [protest_row['naam'] if pd.notna(protest_row['naam']) else ""]}),
                # iiif_prezi3.KeyValueString(label={"nl": ["Beschrijving"]}, value={"nl": [protest_row['beschrijving'] if pd.notna(protest_row['beschrijving']) else ""]}),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Datum (begin)"]},
                    value={
                        "nl": [
                            str(protest_row["datum_start"])
                            if pd.notna(protest_row["datum_start"])
                            else ""
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Datum (eind)"]},
                    value={
                        "nl": [
                            str(protest_row["datum_eind"])
                            if pd.notna(protest_row["datum_eind"])
                            else ""
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Locatie's"]},
                    value={
                        "nl": [
                            protest_row["locatie's"]
                            if pd.notna(protest_row["locatie's"])
                            else ""
                        ]
                    },
                ),
                iiif_prezi3.KeyValueString(
                    label={"nl": ["Classificatie's"]},
                    value={
                        "nl": [
                            protest_row["classificatie's"]
                            if pd.notna(protest_row["classificatie's"])
                            else ""
                        ]
                    },
                ),
            ],
        )

        # Add photos to the manifest
        for i, photo_row in df_photo[
            df_photo["protest"] == protest_row["naam"]
        ].iterrows():

            canvas_id = f"{URI_PREFIX}{slug}/p1/canvas/{i+1}"

            manifest.make_canvas_from_iiif(
                url=photo_row["iiif_info_json"],
                id=canvas_id,
                anno_page_id=canvas_id + "/page",
                anno_id=canvas_id + "/anno",
            )

        with open(f"{target_folder}/{slug}.json", "w", encoding="utf-8") as f:
            manifest_jsonld = json.loads(manifest.json())
            manifest_jsonld["@context"] = [
                "http://iiif.io/api/extension/navplace/context.json",
                "http://iiif.io/api/presentation/3/context.json",
            ]
            json.dump(manifest_jsonld, f, indent=2, ensure_ascii=False)

        c.items.append(manifest)

    # Save the collection as a JSON file
    with open(f"{target_folder}/collection.json", "w", encoding="utf-8") as f:
        f.write(c.json())

    print("Collection generated and saved to collection.json")


if __name__ == "__main__":

    df_protest = pd.read_excel(
        "data/Amsterdam in Motion 750 - Data.xlsx", sheet_name="Protest"
    )
    df_photo = pd.read_excel(
        "data/Amsterdam in Motion 750 - Data.xlsx", sheet_name="Foto"
    )

    main(df_protest, df_photo)
