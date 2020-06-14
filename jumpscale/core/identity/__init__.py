from jumpscale.core.base import StoredFactory
from jumpscale.data.nacl import NACL
from jumpscale.core.config import get_config, update_config
from jumpscale.core.exceptions import NotFound, Value, Input
from jumpscale.core.base import fields
from jumpscale.core.base import Base
from jumpscale.data.encryption import mnemonic


from jumpscale.sals.nettools import get_default_ip_config


class Identity(Base):
    def _explorer_url_update(self, value):
        self._explorer = None

    _tid = fields.Integer(default=-1)
    words = fields.Secret()
    email = fields.String()
    tname = fields.String()
    explorer_url = fields.String(on_update=_explorer_url_update)

    def __init__(self, tname=None, email=None, words=None, explorer_url=None, _tid=-1):
        """
        Get Identity

        Requires: tname, email and words or tid and words

        Arguments:
            tname (str, optional): Name eg. example.3bot
            email (str, optional): Email of identity
            words (str): Words used to secure identity
            explorer_url (str, optional): Url for the explorer to use
            tid (int, optional): When tid is passed tname, email will be verified against it

        Raises: NotFound incase tid is passed but does not exists on the explorer
        Raises: Input: when params are missing
        """
        super().__init__(tname=tname, email=email, words=words, explorer_url=explorer_url, _tid=_tid)
        self._nacl = None
        self._explorer = None
        self.verify_configuration()

    @property
    def nacl(self):
        if not self._nacl:
            seed = mnemonic.mnemonic_to_key(self.words.strip())
            self._nacl = NACL(private_key=seed)
        return self._nacl

    def verify_configuration(self):
        """
        Verifies passed arguments to constructor

        Raises: NotFound incase tid is passed but does not exists on the explorer
        Raises: Input: when params are missing
        """
        if not self.words:
            raise Input("Words are mandotory for an indentity")
        if self._tid != -1:
            user = self.explorer.users.get(tid=self._tid)
            if self.tname and self.tname != user.name:
                raise Input("Name of user does not match name in explorer")
            self.tname = user.name
            if self.nacl.get_verify_key_hex() != user.pubkey:
                raise Input(
                    "The verify key on your local system does not correspond with verify key on the TFGrid explorer"
                )
        else:
            for key in ["email", "tname"]:
                if not getattr(self, key):
                    raise Value("Threebot not configured")

    @property
    def explorer(self):
        if self._explorer is None:
            from jumpscale.clients.explorer import export_module_as  # Import here to avoid circular imports
            ex_factory = export_module_as()
            if self.explorer_url:
                self._explorer = ex_factory.get_by_url(self.explorer_url)
            else:
                self._explorer = ex_factory.get_default()
        return self._explorer

    @property
    def tid(self):
        if self._tid == -1:
            self.register()
        return self._tid

    def register(self, host=None):
        self.verify_configuration()
        try:
            user = self.explorer.users.get(name=self.tname)
        except NotFound:
            user = None

        tid = None
        if not user:
            if not host:
                try:
                    _, host = get_default_ip_config()
                except Exception:
                    host = "localhost"
            user = self.explorer.users.new()
            user.name = self.tname
            user.host = host
            user.email = self.email
            user.description = ""
            user.pubkey = self.nacl.get_verify_key_hex()
            try:
                tid = self.explorer.users.register(user)
            except Exception as e:
                msg = str(e)
                if msg.find("user with same name or email exists") != -1:
                    raise Input("A user with same name or email exists om TFGrid phonebook.")
                raise e
            tid = tid
        else:
            if self.nacl.get_verify_key_hex() != user.pubkey:
                raise Input(
                    "The verify key on your local system does not correspond with verify key on the TFGrid explorer"
                )
            tid = user.id
        self._tid = tid
        self.save()
        return tid


def get_identity():
    return IdentityFactory(Identity).me


class IdentityFactory(StoredFactory):
    _me = None

    def new(self, name, tname=None, email=None, words=None, explorer_url=None, tid=-1):
        instance = super().new(name, tname=tname, email=email, words=words, explorer_url=explorer_url, _tid=tid)
        return instance

    def add_admin(self, name):
        # TODO: ALIGN WITH NEW IDENTITY
        if(name in self._threebot_data["admins"]):
            raise j.exceptions.Value(f"Admin {name} already exists")
        self._threebot_data["admins"].append(name)
        j.core.config.set("threebot", self._threebot_data)

    def delete_admin(self, name):
        # TODO: ALIGN WITH NEW IDENTITY
        if(name not in self._threebot_data["admins"]):
            raise j.exceptions.Value(f"Admin {name} does not exist")
        self._threebot_data["admins"].remove(name)
        j.core.config.set("threebot", self._threebot_data)

    def list_admins(self):
        # TODO: ALIGN WITH NEW IDENTITY
        return self._threebot_data["admins"]

    @property
    def me(self):
        if not self._me:
            config = get_config()
            default = config["threebot"]["default"]
            if default:
                self.__class__._me = self.get(name=default)
            else:
                for identity in self.list_all():
                    self.__class__._me = self.get(identity)
                    break
                else:
                    raise Value("No configured identity found")
        return self._me

    def set_default(self, name):
        config = get_config()
        config["default"] = name
        update_config(config)
        self._me = None


def export_module_as():
    return IdentityFactory(Identity)
