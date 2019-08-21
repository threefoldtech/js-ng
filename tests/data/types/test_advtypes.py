from jumpscale.god import j


def test_email_check():
    e = j.data.types.Email()
    assert e.check("name@example.com")
    assert not e.check("anothername@example")


def test_path_check():
    p = j.data.types.Path()
    assert p.check("/home/me")
    assert not p.check("not path")


def test_url_check():
    u = j.data.types.URL()
    assert u.check("https://www.google.com")
    assert not u.check("www.google")


def test_ip_check():
    ip = j.data.types.IPAddress()
    assert ip.check("185.145.45.5")
    assert not ip.check("44.54.5")


def test_tel_check():
    tel = j.data.types.Tel()
    assert tel.check("010055471466")
    assert tel.check("(+20) 100 48 5555")


def test_datetime_check():
    dt = j.data.types.DateTime()
    assert dt.check("2003-12-31 23:59")
    assert not dt.check("2003/12/31 12:50")


def test_data_check():
    d = j.data.types.Date()
    assert d.check("2003-12-31")
    assert not d.check("2003/12/31")


def test_time_check():
    t = j.data.types.Time()
    assert t.check("23:59")
    assert not t.check("50:59")


def test_duration_check():
    d = j.data.types.Duration()
    assert d.check("22y 11m 4d")
    assert d.check("4d 22h 12m")

