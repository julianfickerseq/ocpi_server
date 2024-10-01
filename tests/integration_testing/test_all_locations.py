
def test_get_all_with_wrong_user(client, headers):
    r_get=client.get("/ocpi/emsp/2.1.1/locations/",headers=headers)
    assert r_get.status_code==403
    print(r_get.json)

def test_get_all():
    assert False

def test_paginate():
    assert False
        
def test_link():
    assert False
    
def test_x_total_count():
    assert False