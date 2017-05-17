from requests import get
from json import load, loads, dumps, decoder
from jsondiff import diff
from codecs import open
from os import remove
from glob import glob
from pystache import render
from jsonschema import validate, Draft3Validator
from os.path import basename, splitext, isfile


def render_template(template_loc, response_loc):
    if isfile(template_loc):
        for response in glob(response_loc):
            print(response)
            with open(template_loc, "r", "utf-8") as f:
                template = f.read()
            with open(response, "r", "utf-8") as f:
                content = load(f)
                pagename = splitext(basename(response))[0]
            with open("rendered_pages/" + pagename + ".html", "w", "utf-8") as f:
                f.write(render(template, content))


def validate_received_responses(schema_loc, response_loc, array=False):
    # assuming 10to1 will do tests to validate api output against swagger defined json schema,
    # TODO it turns out they don't, so I'll do it myself
    for response in glob(response_loc):
        test_name = splitext(basename(response))[0]
        with open(response, "r", "utf-8") as f:
            v = Draft3Validator(definitions[schema_loc])
            full_doc = load(f)
            if array:
                doc = full_doc[0] if len(full_doc) > 0 else {}
            else:
                doc = full_doc
            validation_errors = sorted(v.iter_errors(doc), key=str)
            filtered_errors = []
            for error in validation_errors:
                if "None is not of type" not in error.message:
                    filtered_errors.append(str(error))
            if len(filtered_errors) > 0:
                with open("validation_errors/" + test_name + ".txt", "w", "utf-8") as f:
                    f.write("\n\n--------------------------------------\n\n".join([error for error in filtered_errors]))


base_path = "http://web01.kunsten-staging.skyscrape.rs/api"

with open("swagger.json") as f:
    swagger_json = load(f)
    definitions = swagger_json["definitions"]

tests = {
    "organiteiten": "/organiteiten?offset=0&limit=1",  # lijst van organiteiten
    "organiteiten_met_beginletter": "/organiteiten?organiteit_naam_begint_met=a&offset=0&limit=3",  # lijst van organiteiten met beginletter
    "organiteiten_van_type": "/organiteiten?organiteit_type_id=241&limit=3&offset=0",  # lijst van organiteiten van type, 2 = data.kunsten.be, 4 = person_types, 1 = kunstenaars
    "organiteiten_van_genre": "/organiteiten?genre_id=282458,282457&offset=0&limit=3",  # lijst van organiteiten met een genre
    "organiteiten_met_instrument": "/organiteiten?instrument_id=161111&offset=0&limit=3",  # lijst van organiteiten met een instrument
    "organiteiten_active": "/organiteiten?active=true&offset=0&limit=3",  # lijst van actieve organiteiten
    "organiteiten_met_beginletter_en_active": "/organiteiten?organiteit_begint_met=a&active=True&offset=0&limit=3",  # lijst van actieve organiteiten die beginnen met a
    "organiteiten_met_beginletter_genre_en_active": "/organiteiten?organiteit_begint_met=a&genre_id=[251]&active=True&offset=0&limit=3",  # lijst van actieve organiteiten die beginnen met a en een genre hebben
    "organiteit_benjamin_verdonck": "/organiteiten/211888740",  # een organiteit persoon
    "organiteit_mauro_pawlowski": "/organiteiten/211911801",  # een organiteit persoon
    "organiteit_kvs": "/organiteiten/22360690",  # een organiteit organisatie
    "tentoonstellingen_in_jaar": "/tentoonstellingen?jaar=2016&offset=0&limit=1",  # tentoonstellingen in een jaar
    "tentoonstellingen_in_jaar_en_maand": "/tentoonstellingen?jaar=2016&maand=12&offset=0&limit=1",  # tentoonstellingen in een jaar en een maand
    "tentoonstellingen_in_land": "/tentoonstellingen?land_id=2112986&offset=0&limit=1",  # lijst van tentoonstellingen in een land
    "tentoonstellingen_van_kunstenaar": "/tentoonstellingen?organiteit_id=211906274&offset=0&limit=1",  # lijst van tentoonstellingen van een kunstenaar
    "tentoonstellingen_aan_organisatie": "/tentoonstellingen?organiteit_id=22377206&offset=0&limit=1",  # lijst van tentoonstellingen die aan een organisatie hangen
    "tentoonstelling_": "/tentoonstellingen/20462656",  # specifieke tentoonstelling
    "recent_gewijzigde_activiteiten": "/recent_gewijzigde_activiteiten",
    "recent_gewijzigde_buitenlandse_concerten": "/recent_gewijzigde_activiteiten/concert",
    "recent_gewijzigde_muziekreleases": "/recent_gewijzigde_activiteiten/muziekrelease",
    "binnenkort": "/binnenkort",
    "binnenkort_podiumproducties": "/binnenkort/podiumproductie",
    "binnenkort_muziekreleases": "/binnenkort/muziekrelease",
    "tien_jaar_geleden": "/tien_jaar_geleden",
    "bcs_": "/buitenlandse_concerten?offset=0&limit=3",  # lijst van buitenlandse concerten
    "bcs_in_jaar": "/buitenlandse_concerten?jaar=2016&offset=0&limit=5",
    "bcs_in_land": "/buitenlandse_concerten?land_id=12928&offset=0&limit=3",
    "bcs_in_stad": "/buitenlandse_concerten?location_id=4778&offset=0&limit=3",
    "bcs_door_mcv_artist": "/buitenlandse_concerten?organiteit_id=21154637&offset=0&limit=3",
    "bcs_door_dkb_artist": "/buitenlandse_concerten?organiteit_id=211950063&offset=0&limit=3",
    "bcs_in_periode": "/buitenlandse_concerten?from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=3",
    "bcs_in_periode_en_land": "/buitenlandse_concerten?country_id=12928from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=3",
    "bc_": "/buitenlandse_concerten/261992253",  # een specifiek buitenlands concert
    "podiumproducties_in_seizoen": "/podiumproducties?seizoen_id=1712&offset=0&limit=3",
    "podiumproducties_met_genre": "/podiumproducties?genre_id=[272301]&offset=0&limit=3",
    "podiumproducties_met_beginletter": "/podiumproducties?activiteit_naam_begint_met=a&offset=0&limit=3",
    "podiumproducties_van_jan_decleir": "/podiumproducties?organiteit_id=211878826&offset=0&limit=3",
    "podiumproducties_die_gelinkt_zijn_aan_andere_producties": "/podiumproducties?podium_productie_id=452507&offset=0&limit=3",
    "podiumproducties_in_seizoen_met_genre": "/podiumproducties?seizoen_id=1712&genre_id=[272301]&offset=0&limit=3",
    "podiumproducties_in_seizoen_van_jan_decleir": "/podiumproducties?seizoen_id=1712&organiteit_id=211878826&offset=0&limit=3",
    "podiumproductie_welwillenden": "/podiumproducties/20452507",
    "podiumvoorstelling_": "/podiumvoorstellingen/261990147",
    "podiumvoorstellingen_in_seizoen": "/podiumvoorstellingen?seizoen_id=1712&offset=0&limit=3",
    "muziekrelease_pop": "/muziekreleases/1586517",
    "muziekrelease_klassiek": "/muziekreleases/1582773",
    "muziekreleases_blues": "/muziekreleases?genre_id=18196&offset=0&limit=3",
    "muziekreleases_2015": "/muziekreleases?jaar=2015&offset=0&limit=3",
    "muziekreleases_sukilove": "/muziekreleases?organiteit_id=11132341&offset=0&limit=3",
    "muziekreleases_muziekcentrum": "/muziekreleases?organiteit_id=1214215&offset=0&limit=3",
    "muziekreleases_pop_maart2015": "/muziekreleases?from_date=2015-03-01&until_date=2015-03-31&genre_id=18196"
}

for folder in ["received_responses", "rendered_pages", "validation_errors"]:
    for f in glob(folder + "/*"):
        remove(f)

for test in tests:
    try:
        response_text = get(base_path + tests[test]).text
        response = loads(response_text)
        with open("received_responses/" + test + ".json", "w", "utf-8") as f:
            f.write(dumps(loads(response_text), indent=2))
        print(test, "".join(["."]*(60 - len(test))), "response received")
    except decoder.JSONDecodeError:
        response = None
        print(test, "".join(["."]*(60 - len(test))), "no response")

# Organiteit
validate_received_responses("Organiteit", "received_responses/organiteit_*.json")
render_template("mustache/organiteit.mstch", "received_responses/organiteit_*.json")

# Organiteiten
validate_received_responses("OrganiteitenItem", "received_responses/organiteiten_*.json", array=True)
render_template("mustache/organiteiten.mstch", "received_responses/organiteiten_*.json")

# Tentoonstellling
validate_received_responses("Tentoonstelling", "received_responses/tentoonstelling_*.json")
render_template("mustache/tentoonstelling.mstch", "received_responses/tentoonstelling_*.json")

# Tentoonstellingen
validate_received_responses("TentoonstellingenItem", "received_responses/tentoonstellingen_*.json", array=True)
render_template("mustache/tentoonstellingen.mstch", "received_responses/tentoonstellingen_*.json")

# Buitenlands concert
validate_received_responses("BuitenlandsConcert", "received_responses/bc_*.json")
render_template("mustache/buitenlands_concert.mstch", "received_responses/bc_*.json")

# Buitenlandse concerten
validate_received_responses("BuitenlandseConcertenItem", "received_responses/bcs_*.json", array=True)
render_template("mustache/buitenlandse_concerten.mstch", "received_responses/bcs_*.json")

# Podiumproductie
validate_received_responses("PodiumProductie", "received_responses/podiumproductie_.json")
render_template("mustache/podiumproductie.mstch", "received_responses/podiumproductie_*.json")

# Podiumproducties
validate_received_responses("PodiumProductiesItem", "received_responses/podiumproducties_*.json", array=True)
render_template("mustache/podiumproducties.mstch", "received_responses/podiumproducties_*.json")

# Podiumvoorstelling
validate_received_responses("PodiumVoorstelling", "recevied_responses/podiumvoorstelling_*.json")
render_template("mustache/podiumvoorstelling.mstch", "received_responses/podiumvoorstelling_*.json")

# Podiumvoorstellingen
validate_received_responses("PodiumVoorstellingenItem", "received_responses/podiumvoorstellingen_*.json", array=True)
render_template("mustache/podiumvoorstellingen.mstch", "received_responses/podiumvoorstellingen_*.json")

# Muziekrelease
validate_received_responses("Muziekrelease", "received_responses/muziekrelease_*.json")
render_template("mustache/muziekrelease.mstch", "received_responses/muziekrelease_*.json")

# Muziekreleases
validate_received_responses("MuziekreleasesItem", "received_responses/muziekreleases_*.json", array=True)
render_template("mustache/muziekreleases.mstch", "received_responses/muziekreleases_*.json")

# Tien jaar geleden
validate_received_responses("KorteLijstActiviteitenItem", "received_responses/tien_jaar_geleden*.json", array=True)
render_template("mustache/tienjaargeleden.mstch", "received_responses/tien_jaar_geleden*.json")

# Binnenkort
validate_received_responses("KorteLijstActiviteitenItem", "received_responses/binnenkort*.json", array=True)
render_template("mustache/binnenkort.mstch", "received_responses/binnenkort*.json")
