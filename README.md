# Amsterdam Protest Time Machine - Amsterdam in Motion 750

- [Amsterdam Protest Time Machine - Amsterdam in Motion 750](#amsterdam-protest-time-machine---amsterdam-in-motion-750)
  - [About](#about)
  - [Data](#data)
    - [Protest data](#protest-data)
    - [Thesaurus](#thesaurus)
  - [Model](#model)
  - [Scripts](#scripts)
    - [Setup with uv](#setup-with-uv)
    - [IIIF Collection and Manifest](#iiif-collection-and-manifest)
    - [Thesaurus](#thesaurus-1)
  - [Citation](#citation)
  - [License](#license)

## About

This repository contains the code and data for the Amsterdam Protest Time Machine's Amsterdam in Motion 750 application (which can be seen at the [Amsterdam in Motion 750](https://amsterdaminmotion.nl/) exposition at the Westergasterrein, Amsterdam), a tool that visualizes the history of protest in Amsterdam. The application allows users to explore historical images of protests in Amsterdam from 1535 to 2015, drawn from the public image banks of the Amsterdam City Archives, the National Archives of the Netherlands, and the North Holland Archives. It allows users to explore protest history by protest type, theme, and location across multiple archives in a single interface.

The application was created within the Amsterdam Protest Time Machine project at the CREATE Lab of the University of Amsterdam's Faculty of Humanities, which develops open digital infrastructure for Amsterdam's history.

## Data

### Protest data

The manifest generation script reads three sheets from `data/Amsterdam in Motion 750 - Data.xlsx`: `Protest`, `Foto_kopie`, and `Classificatie`. Only the columns below are used.

| Sheet           | Column                         | Used for                                                                                                                                  |
| --------------- | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `Protest`       | `slug`                         | Builds the manifest filename and public IIIF manifest URI.                                                                                |
| `Protest`       | `naam`                         | Sets the protest title and matches protest rows to related photo rows through `Foto_kopie.protest`.                                       |
| `Protest`       | `beschrijving`                 | Becomes the manifest summary and the schema.org event description.                                                                        |
| `Protest`       | `datum_start`                  | Used for the manifest `navDate`, manifest metadata, and schema.org start date.                                                            |
| `Protest`       | `datum_eind`                   | Used for manifest metadata and schema.org end date.                                                                                       |
| `Protest`       | `locaties`                     | Written into manifest metadata and schema.org location.                                                                                   |
| `Protest`       | `classificaties`               | Split into labels that are resolved against the `Classificatie` sheet and written into manifest metadata and schema.org `additionalType`. |
| `Protest`       | `thumbnail (foto op homepage)` | If present, used as the preferred IIIF thumbnail for the manifest.                                                                        |
| `Foto_kopie`    | `protest`                      | Links each photo row to a protest row by matching the protest name.                                                                       |
| `Foto_kopie`    | `naam`                         | Used as the canvas label and image title metadata.                                                                                        |
| `Foto_kopie`    | `beschrijving`                 | Written into image metadata on the canvas.                                                                                                |
| `Foto_kopie`    | `datum_start`                  | Written into image metadata as the start date.                                                                                            |
| `Foto_kopie`    | `datum_eind`                   | Written into image metadata as the end date.                                                                                              |
| `Foto_kopie`    | `fotograaf`                    | Written into image metadata.                                                                                                              |
| `Foto_kopie`    | `archief`                      | Written into image metadata.                                                                                                              |
| `Foto_kopie`    | `url`                          | Written into image metadata as the source record URL.                                                                                     |
| `Foto_kopie`    | `locatie`                      | Written into image metadata.                                                                                                              |
| `Foto_kopie`    | `iiif_info_json`               | Used to construct the IIIF canvas, fetch image dimensions, and derive thumbnails when no protest thumbnail is supplied.                   |
| `Classificatie` | `uri`                          | Supplies the concept URI for each classification used in the manifest.                                                                    |
| `Classificatie` | `prefLabel`                    | Matches the labels stored in `Protest.classificaties` and is also used as the SKOS preferred label.                                       |

The script joins the workbook through two relationships:

1. `Protest.naam` -> `Foto_kopie.protest` to attach photos to a protest manifest.
2. `Protest.classificaties` -> `Classificatie.prefLabel` to expand classification labels into concept URIs.

### Thesaurus

The thesaurus is generated by `scripts/make_thesaurus.py` from three input files:

| File                                     | Role                                                                                            |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `data/pp_scheme_protestthesaurus.jsonld` | Source protest thesaurus in JSON-LD / SKOS form.                                                |
| `data/thesaurus_context.json`            | JSON-LD context used to compact the thesaurus into a simpler structure.                         |
| `data/TD_thesaurus.json`                 | Local mapping keyed by concept URI, used to add application-specific metadata, such as colours. |

The final output is written to `thesaurus/thesaurus.json` and provides the controlled vocabulary used to organize protest types and themes in the application.

## Model

The repository models protest history at two connected levels:

1. **Event level:** each protest becomes a `IIIF Manifest` (cf. https://iiif.io/api/presentation/3.0/) with a title, summary, date range, locations, classifications, and linked schema.org event data.
2. **Image level:** each related photograph becomes a `IIIF Canvas` within that manifest, with metadata such as title, description, photographer, archive, archival URL, and location.

This is accompanied by a thesaurus in SKOS format that provides a controlled vocabulary for protest classifications. The thesaurus is used to enrich the manifest metadata and support faceted browsing in the application.

This produces a browsable `IIIF Collection` for publication The thesaurus output adds a compacted JSON-LD vocabulary layer for protest classifications used in the application.

<details>
<summary>Example Manifest</summary>

```json
{
  "@context": [
    "http://iiif.io/api/extension/navplace/context.json",
    "http://iiif.io/api/presentation/3/context.json"
  ],
  "id": "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/palingoproer.json",
  "type": "Manifest",
  "label": {
    "nl": ["Palingoproer"]
  },
  "metadata": [
    {
      "label": {
        "nl": ["Datum (begin)"]
      },
      "value": {
        "nl": ["1886-08-01"]
      }
    },
    {
      "label": {
        "nl": ["Datum (eind)"]
      },
      "value": {
        "nl": ["1916-07-31"]
      }
    },
    {
      "label": {
        "nl": ["Locatie's"]
      },
      "value": {
        "nl": ["Eerste Lindendwarsstraat"]
      }
    },
    {
      "label": {
        "nl": ["Classificatie's"]
      },
      "value": {
        "nl": ["Binnenlandse politiek, Politiek, Oproeren, Rellen"]
      }
    },
    {
      "label": {
        "nl": ["Classificatie's (URI)"]
      },
      "value": {
        "nl": [
          "https://digitaalerfgoed.poolparty.biz/atm/f9ee5edc-2fb1-48fa-a4e6-d34cb38913c3, https://digitaalerfgoed.poolparty.biz/atm/fbe8f879-659e-473c-aa96-9af6a84474c2, https://digitaalerfgoed.poolparty.biz/atm/3c4ae90b-a1be-45f5-b869-41362c8579ad, https://digitaalerfgoed.poolparty.biz/atm/6cc7d868-3702-4744-a5c1-b8d96afc42f5"
        ]
      }
    }
  ],
  "summary": {
    "nl": [""]
  },
  "navDate": "1886-08-01T00:00:00Z",
  "thumbnail": [
    {
      "id": "https://stadsarchiefamsterdam.memorix.io/resources/records/media/5608388b-baf8-d80e-3d83-3828291b2725/iiif/3/57583842/full/637,485/0/default.jpg",
      "type": "Image",
      "height": 485,
      "width": 637,
      "service": [
        {
          "id": "https://stadsarchiefamsterdam.memorix.io/resources/iiif/3/ef76bf9d-0c86-47cd-a5d3-ddc7a884e201",
          "type": "ImageService3",
          "profile": "level2",
          "format": "image/jpeg"
        }
      ],
      "format": "image/jpeg"
    }
  ],
  "items": [
    {
      "id": "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/palingoproer.json/p1/canvas/44",
      "type": "Canvas",
      "label": {
        "nl": ["Palingtrekken op de Lindengracht, 25 juli 1886"]
      },
      "height": 1940,
      "width": 2548,
      "metadata": [
        {
          "label": {
            "nl": ["Naam"]
          },
          "value": {
            "nl": ["Palingtrekken op de Lindengracht, 25 juli 1886"]
          }
        },
        {
          "label": {
            "nl": ["Beschrijving"]
          },
          "value": {
            "nl": [
              "De reprofoto verscheen dertig jaar later, bij de herdenking van het Palingoproer."
            ]
          }
        },
        {
          "label": {
            "nl": ["Datum (begin)"]
          },
          "value": {
            "nl": ["1886-07-01"]
          }
        },
        {
          "label": {
            "nl": ["Datum (eind)"]
          },
          "value": {
            "nl": ["1886-07-31"]
          }
        },
        {
          "label": {
            "nl": ["Fotograaf"]
          },
          "value": {
            "nl": [""]
          }
        },
        {
          "label": {
            "nl": ["Archief"]
          },
          "value": {
            "nl": ["Stadsarchief Amsterdam"]
          }
        },
        {
          "label": {
            "nl": ["URL"]
          },
          "value": {
            "nl": [
              "https://archief.amsterdam/beeldbank/detail/5608388b-baf8-d80e-3d83-3828291b2725"
            ]
          }
        },
        {
          "label": {
            "nl": ["Locatie"]
          },
          "value": {
            "nl": [""]
          }
        }
      ],
      "items": [
        {
          "id": "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/palingoproer.json/p1/canvas/44/page",
          "type": "AnnotationPage",
          "items": [
            {
              "id": "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/palingoproer.json/p1/canvas/44/anno",
              "type": "Annotation",
              "motivation": "painting",
              "body": {
                "id": "https://stadsarchiefamsterdam.memorix.io/resources/iiif/3/ef76bf9d-0c86-47cd-a5d3-ddc7a884e201/full/max/0/default.jpg",
                "type": "Image",
                "height": 1940,
                "width": 2548,
                "service": [
                  {
                    "id": "https://stadsarchiefamsterdam.memorix.io/resources/iiif/3/ef76bf9d-0c86-47cd-a5d3-ddc7a884e201",
                    "type": "ImageService3",
                    "profile": "level2"
                  }
                ],
                "format": "image/jpeg"
              },
              "target": "https://amsterdamtimemachine.github.io/amsterdam-in-motion-750/iiif/palingoproer.json/p1/canvas/44"
            }
          ]
        }
      ]
    }

    [...more ]

  ],
  "seeAlso": [
    {
      "@type": "schema:Event",
      "schema:name": "Palingoproer",
      "schema:description": "",
      "schema:startDate": {
        "@type": "xsd:date",
        "@value": "1886-08-01"
      },
      "schema:endDate": {
        "@type": "xsd:date",
        "@value": "1916-07-31"
      },
      "schema:location": [
        {
          "@type": "schema:Place",
          "schema:name": "Eerste Lindendwarsstraat"
        }
      ],
      "schema:additionalType": [
        {
          "@id": "https://digitaalerfgoed.poolparty.biz/atm/f9ee5edc-2fb1-48fa-a4e6-d34cb38913c3",
          "@type": "skos:Concept",
          "skos:prefLabel": {
            "@language": "nl",
            "@value": "Binnenlandse politiek"
          }
        },
        {
          "@id": "https://digitaalerfgoed.poolparty.biz/atm/fbe8f879-659e-473c-aa96-9af6a84474c2",
          "@type": "skos:Concept",
          "skos:prefLabel": {
            "@language": "nl",
            "@value": "Politiek"
          }
        },
        {
          "@id": "https://digitaalerfgoed.poolparty.biz/atm/3c4ae90b-a1be-45f5-b869-41362c8579ad",
          "@type": "skos:Concept",
          "skos:prefLabel": {
            "@language": "nl",
            "@value": "Oproeren"
          }
        },
        {
          "@id": "https://digitaalerfgoed.poolparty.biz/atm/6cc7d868-3702-4744-a5c1-b8d96afc42f5",
          "@type": "skos:Concept",
          "skos:prefLabel": {
            "@language": "nl",
            "@value": "Rellen"
          }
        }
      ]
    }
  ]
}
```

</details>

## Scripts

This repository uses `uv` for dependency management and reproducible Python environments.

### Setup with uv

```bash
uv sync
```

This installs the dependencies defined in `pyproject.toml` and pinned in `uv.lock`.

### IIIF Collection and Manifest

```bash
uv run python scripts/make_manifest.py
```

### Thesaurus

```bash
uv run python scripts/make_thesaurus.py
```

## Citation

Dataset:

- Zomer Zeijlemaker, Leon van Wissen, Ingeborg Verheul. (2026). Amsterdam Protest Dataset [Data set]. University of Amsterdam.

Conference contribution citing the dataset:

- Zomer Zeijlemaker, Leon van Wissen, Ingeborg Verheul. (2026, June). The Amsterdam Protest Dataset: Linking Visual Archives for Future Research. DH Benelux 2026, Maastricht, The Netherlands. https://doi.org/10.5281/zenodo.20309170

## License

This repository is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. You may share and adapt the material, including for commercial use, provided that you give appropriate credit, link to the license, and indicate whether changes were made.

See [`LICENSE`](./LICENSE) or <https://creativecommons.org/licenses/by/4.0/> for the full license text.
