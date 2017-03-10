from requests import get
from json import load, loads, dump, decoder
from jsondiff import diff

# assuming 10to1 will do tests to validate api output against swagger defined json schema,
# these are "functional" tests to see if output corresponds to what we expect

base_path = "http://data.kunsten.be"

tests = {
    "bc_in_jaar": "/buitenlandse_concerten/?jaar=2016&offset=0&limit=30",
    "bc_in_land": "/buitenlandse_concerten/?land_id=12928&offset=0&limit=30",
    "bc_in_stad": "/buitenlandse_concerten/?city_id=100&offset=0&limit=30",
    "bc_door_mcv_artist": "/buitenlandse_concerten/?organiteit_id=212345346&offset=0&limit=30",
    "bc_door_dkb_artist": "/buitenlandse_concerten/?organiteit_id=112345&offset=0&limit=30",
    "bc_in_periode": "/buitenlandse_concerten/?from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=30",
    "bc_in_periode_en_land": "/buitenlandse_concerten/?country_id=12928from_date=01/01/2017&until_date=31/01/2017&offset=0&limit=30"
}

diffs = {}
for test in tests:
    try:
        response = loads(get(base_path + tests[test]).text)
    except decoder.JSONDecodeError:
        response = None
    with open("expected_responses/" + test + ".json", "r") as f:
        expected = load(f)
    diffs[test] = diff(response, expected, dump=True)

with open("diff.json", "w") as f:
    dump(diffs, f, indent=2)
