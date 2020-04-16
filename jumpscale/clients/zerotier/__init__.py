from jumpscale.core.base import StoredFactory

from .zerotier import ZerotierClient


export_module_as = StoredFactory(ZerotierClient)
