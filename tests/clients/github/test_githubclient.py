# i created new fake github account
# email: fakefortestcs@gmail.com
# password: codescalers72
# username: fakeForTest
# name: Codescalers Test
# organization: fakeForTest2

from jumpscale.god import j
import pytest
import time


def test_github_client():
    # test sign in by email
    j.clients.github.new("omar")
    j.clients.github.omar.username = "fakeForTest"
    j.clients.github.omar.password = "codescalers72"
    assert j.clients.github.omar.get_userdata()["name"] == "Codescalers Test"
    # test with accesstoken can't be tested on travice because we can't store access token in a repo
    # j.clients.github.delete('omar')
    # j.clients.github.new("omar")
    # j.clients.github.omar.accesstoken = ""
    # assert j.clients.github.omar.get_userdata()["name"] == "Codescalers Test"
    j.clients.github.omar.create_repo("hi")
    assert "hi" in j.clients.github.omar.get_repos()
    j.clients.github.omar.delete_repo("hi")
    # time.sleep(.5)
    # assert not "hi" in j.clients.github.omar.get_repos()
    assert "fakeForTest2" in j.clients.github.omar.get_orgs()
    j.clients.github.delete("omar")
