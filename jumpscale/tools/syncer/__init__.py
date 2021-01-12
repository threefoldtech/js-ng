"""Module to help syncing multiple machines with specific directories you have.
used in the jsync tool.
```
JS-NG> xmonader = j.clients.sshkey.new("xmonader")
JS-NG> xmonader.private_key_path = "/home/xmonader/.ssh/id_rsa"
JS-NG> xmonader.load_from_file_system()
JS-NG> xmonader.save()
JS-NG> xmonader = j.clients.sshclient.new("xmonader")
JS-NG> xmonader.sshkey = "xmonader"
JS-NG> s = j.tools.syncer.Syncer(["xmonader"], {"/home/xmonader/wspace/tfchain-py":"/tmp/tfchain-py"})
JS-NG> s.start()
2019-09-03T11:38:47.183394+0200 - paths: {'/home/xmonader/wspace/tfchain-py': '/tmp/tfchain-py'}
```
"""

__optional__ = True


def export_module_as():
    from . import syncer

    return syncer
