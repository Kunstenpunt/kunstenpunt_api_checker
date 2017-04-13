from requests import get
from json import load, loads, dumps, decoder
from jsondiff import diff
from codecs import open
from os import remove
from glob import glob
from pystache import render

# assuming 10to1 will do tests to validate api output against swagger defined json schema,
# these are "semantic" tests to see if output corresponds to what we expect

base_path = "http://web01.kunsten-staging.skyscrape.rs/api"

tests = {
    "organiteiten": "/organiteiten?offset=0&limit=1",  # lijst van organiteiten
    "organiteiten_met_beginletter": "/organiteiten?organiteit_naam_begint_met=a&offset=0&limit=1",  # lijst van organiteiten met beginletter
    "organiteiten_van_type": "/organiteiten?organiteit_type_id=241&limit=1&offset=0",  # lijst van organiteiten van type, 2 = data.kunsten.be, 4 = person_types, 1 = kunstenaars
    "organiteiten_van_genre": "/organiteiten?genre_id=282458,282457&offset=0&limit=1",  # lijst van organiteiten met een genre
    "organiteiten_met_instrument": "/organiteiten?instrument_id=161111&offset=0&limit=1",  # lijst van organiteiten met een instrument
    "organiteiten_active": "/organiteiten?active=true&offset=0&limit=1",  # lijst van actieve organiteiten
    "organiteiten_met_beginletter_en_active": "/organiteiten?organiteit_begint_met=a&active=True&offset=0&limit=1",  # lijst van actieve organiteiten die beginnen met a
    "organiteiten_met_beginletter_genre_en_active": "/organiteiten?organiteit_begint_met=a&genre_id=[251]&active=True&offset=0&limit=1",  # lijst van actieve organiteiten die beginnen met a en een genre hebben
    "organiteit_benjamin_verdonck": "/organiteiten/211888740",  # een organiteit persoon
    "organiteit_mauro_pawlowski": "/organiteiten/211911801",  # een organiteit persoon
    "organiteit_kvs": "/organiteiten/22360690",  # een organiteit organisatie
    "tentoonstellingen_in_jaar": "/tentoonstellingen?jaar=2016&offset=0&limit=1",  # tentoonstellingen in een jaar
    "tentoonstellingen_in_jaar_en_maand": "/tentoonstellingen?jaar=2016&maand=12&offset=0&limit=1",  # tentoonstellingen in een jaar en een maand
    "tentoonstellingen_in_land": "/tentoonstellingen?land_id=2112986&offset=0&limit=1",  # lijst van tentoonstellingen in een land
    "tentoonstellingen_van_kunstenaar": "/tentoonstellingen?organiteit_id=211906274&offset=0&limit=1",  # lijst van tentoonstellingen van een kunstenaar
    "tentoonstellingen_aan_organisatie": "/tentoonstellingen?organiteit_id=22377206&offset=0&limit=1",  # lijst van tentoonstellingen die aan een organisatie hangen
    "tentoonstelling": "/tentoonstellingen/20462656",  # specifieke tentoonstelling
    "recent_gewijzigde_activiteiten": "/recent_gewijzigde_activiteiten",
    "recent_gewijzigde_buitenlandse_concerten": "/recent_gewijzigde_activiteiten/concert",
    "binnenkort": "/binnenkort",
    "binnenkort_podiumproducties": "/binnenkort/podiumproductie",
    "tien_jaar_geleden": "/tien_jaar_geleden",
    "bcs": "/buitenlandse_concerten?offset=0&limit=1",  # lijst van buitenlandse concerten
    "bc_in_jaar": "/buitenlandse_concerten?jaar=2016&offset=0&limit=5",
    "bc_in_land": "/buitenlandse_concerten?land_id=12928&offset=0&limit=1",
    "bc_in_stad": "/buitenlandse_concerten?location_id=4778&offset=0&limit=1",
    "bc_door_mcv_artist": "/buitenlandse_concerten?organiteit_id=21154637&offset=0&limit=1",
    "bc_door_dkb_artist": "/buitenlandse_concerten?organiteit_id=211950063&offset=0&limit=1",
    "bc_in_periode": "/buitenlandse_concerten?from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=1",
    "bc_in_periode_en_land": "/buitenlandse_concerten?country_id=12928from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=1",
    "bc": "/buitenlandse_concerten/261992253",  # een specifiek buitenlands concert
    "podiumproducties_in_seizoen": "/podiumproducties?seizoen_id=123451&offset=0&limit=1",
    "podiumproducties_met_genre": "/podiumproducties?genre_id=[272301]&offset=0&limit=1",
    "podiumproducties_met_beginletter": "/podiumproducties?activiteit_naam_begint_met=a&offset=0&limit=1",
    "podiumproducties_van_organiteit": "/podiumproducties?organiteit_id=211878826&offset=0&limit=1",
    "podiumproducties_die_gelinkt_zijn_aan_andere_producties": "/podiumproducties?podium_productie_id=452507&offset=0&limit=10",
    "podiumproducties_in_seizoen_met_genre": "/podiumproducties?seizoen_id=1712&genre_id=[272301]&offset=0&limit=1",
    "podiumproducties_in_seizoen_van_organiteit": "/podiumproducties?seizoen_id=1712&organiteit_id=211878826&offset=0&limit=3",
    "podiumproductie_welwillenden": "/podiumproducties/20452507"
}

for f in glob("received_responses/*"):
    remove(f)

for f in glob("diffs/*"):
    remove(f)

diffs = {}
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
    with open("expected_responses/" + test + ".json", "r", "utf-8") as f:
        expected = load(f)
    diffs[test] = diff(response, expected, dump=True)

for test in diffs:
    with open("diffs/" + test + ".json", "w", "utf-8") as f:
        f.write(diffs[test])

for response in glob("received_responses/organiteit_*.json"):
    with open("moustache/organiteit.mstch", "r") as f:
        template = f.read()
    with open(response, "r") as f:
        content = load(f)
        pagename = response.split("\\")[-1].rstrip(".json")
    with open("rendered_pages/" + pagename + ".html", "w") as f:
        f.write(render(template, content))
