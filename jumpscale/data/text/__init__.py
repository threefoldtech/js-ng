"""helpers around string manipulation.


## Remove prefix 
```
JS-NG> j.data.text.removeprefix("ahhmed", "ah")                                                                                                                                          
'hmed'
```

## Remove suffix

```
JS-NG> j.data.text.removesuffix("ahhmed.3bot", ".3bot")                                                                                                                                  
'ahhmed'
```
"""

# TO BE REMOVED when https://www.python.org/dev/peps/pep-0616/ is implemented
def removeprefix(s: str, prefix: str) -> str:
    """Remove a prefix string `prefix` from a string `s`.

    Args:
        s (str): string the contains prefix we want to remove
        prefix (str): prefix we want to remove

    Returns:
        str: string without the prefix part

    """
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s[:]

def removesuffix(s: str, suffix: str) -> str:
    """Remove a suffix string `suffix` from a string `s`.

    Args:
        s (str): string the contains suffix we want to remove
        suffix (str): suffix we want to remove

    Returns:
        str: string without the suffix part

    """
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s[:]