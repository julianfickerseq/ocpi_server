import json
import sys
def test_put_location(client):
    print(sys.path)
    with open(f'{sys.path}/location.json', 'r') as file:
        data = json.load(file)
    r=client.put("/ocpi/emsp/2.1.1/locations/BE/TEST/89900877",json=data)
    print(r.request.url)
    assert r.status_code==200

# def test_get(client):
#     app = client.application
#     for rule in app.url_map.iter_rules():
#             methods = ', '.join(sorted(rule.methods))
#             print(f"{rule.endpoint}: {rule.rule} [{methods}]")