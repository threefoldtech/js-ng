# jsync command

`jsync` is a syncing tool to sync over certain set of directories against remote machine.

## list available clients
```
~> poetry run jsync list-ssh-clients           
['xmonader']

```

## sync with a client certain set of paths
~> poetry run jsync sync --clients "xmonader" --paths "~/wspace/tq,/tmp/proj:/tmp/proj2"
['xmonader'] {'~/wspace/tq': '~/wspace/tq', '/tmp/proj': '/tmp/proj2'}
```

```
poetry run jsync sync --clients "xmonader" --paths "~/wspace/tq:/tmp/tq" --sync
```

