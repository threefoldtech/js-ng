"""
This module defines main dirs in jumpscale to be used

```
JS-NG> j.core.dirs                                                                                                                                                        
ExportedModule(__doc__=None, _exportedas=<class 'jumpscale.core.dirs.dirs.Dirs'>, _loaded=True, _m=<module 'jumpscale.core.dirs' from '/home/ahmed/wspace/js/js-ng/jumpscale/core/dirs/__init__.py'>)

JS-NG> j.core.dirs.BASEDIR                                                                                                                                                
'/home/ahmed/sandbox'

JS-NG> j.core.dirs.BINDIR                                                                                                                                                 
'/home/ahmed/sandbox/bin'

JS-NG>                                                                                                                                                                    
JS-NG> j.core.dirs.CFGDIR                                                                                                                                                 
'/home/ahmed/sandbox/cfg'

JS-NG>                                                                                                                                                                    
JS-NG> j.core.dirs.CODEDIR                                                                                                                                                
'/home/ahmed/sandbox/code'

JS-NG>                                                                                                                                                                    
JS-NG> j.core.dirs.HOMEDIR                                                                                                                                                
'/home/ahmed'

JS-NG> j.core.dirs.LOGDIR                                                                                                                                                 
'/home/ahmed/sandbox/var/log'

JS-NG> j.core.dirs.TEMPLATEDIR                                                                                                                                            
'/home/ahmed/sandbox/var/templates'

JS-NG> j.core.dirs.TMPDIR                                                                                                                                                 
'/tmp/jumpscale'

JS-NG> j.core.dirs.VARDIR                                                                                                                                                 
'/home/ahmed/sandbox/var'
```


"""

import os


class Dirs:

    HOMEDIR = os.path.expanduser("~")  # TODO: check homedir defined in sal.fs
    BASEDIR = os.path.join(HOMEDIR, "sandbox")
    BINDIR = os.path.join(BASEDIR, "bin")
    CFGDIR = os.path.join(BASEDIR, "cfg")  # TODO: check conflict with core.config_root..
    CODEDIR = os.path.join(BASEDIR, "code")
    VARDIR = os.path.join(BASEDIR, "var")
    LOGDIR = os.path.join(VARDIR, "log")
    JSCFGDIR = os.path.join(HOMEDIR, ".config/jumpscale")
    TEMPLATEDIR = os.path.join(VARDIR, "templates")
    TMPDIR = "/tmp/jumpscale"
