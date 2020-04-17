# Developing SALs

SAL is an abbreviation for `System Abstraction Layer` It provides a higher level `DSL` to execute/manipulate certain functionality that has a dry or daunting interface with a simpler API

## Code structure
Sals are a sub namespace in Jumpscale namespace, they exist in directory `jumpscale/sals`. To develop a new SAL you need to make a new package in `sals` directory in your `js-next` project.


```
➜  js-ng git:(development) ✗ tree jumpscale/sals
jumpscale/sals
├── fs
│   └── __init__.py
├── hostsfile
│   └── __init__.py
├── nettools
│   └── __init__.py
└── process
    └── __init__.py
```

In each you will find a package `fs`, `hostsfile`, `nettools`, `process` as sal packages.

## Writing code
You can put all of your code directly in the `__init__.py` of your SAL package.


## Accessing code
Code will be auto registered in the god object `j` like that `j.sal.YOUR_NEW_SAL`


