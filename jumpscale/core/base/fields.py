"""
`fields` have all possible fields where they can be used as a class variables for any Base classselfself.

Field instances will not hold the value or any date, they will be converted by Base to function descriptors,
where the data itself resides in Base objects (instances).

See `jumpscale.core.base.meta`.

Example:

```python
from enum import Enum

class Permission(Base):
    read_posts = fields.Boolean()
    write_posts = fields.Boolean()
    open_ticket = fields.Boolean()


class UserType(Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    emails = fields.List(fields.String())
    permissions = fields.List(fields.Object(Permission))
    custom_config = fields.Typed(dict)
    type = fields.Enum(UserType)

user = User()
emails = ["a@b.com"]
perm1 = Permission()
perm1.open_portal = True
permissions = [perm1]

user.emails = emails
user.permissions = permissions
user.save()
```

Every field type is responsible dealing with the actual value of this field in the Base objects (instances), mainly:

* validation
* converting from raw primitive types to special types if any, which would help in serialization

In addition to custom options every field can accept and define, they can be used in the following methods:

* `validate`:  raises a `ValidationError` in case it's not valid.
* `to_raw`: returns a raw (primitive type) object from a value of this field
* `from_raw`: returns a new object of the field type (if any) from a raw value

No need for `from_raw` to raise an error on e.g. type mismatch, as `validate` will do the validation.

"""
import arrow
import datetime
import ipaddress
import json
import re
import uuid

from urllib.parse import urlparse

from .factory import Factory as BaseFactory, StoredFactory


class ValidationError(Exception):
    """
    base type for any validation error
    """


class Field:
    def __init__(
        self,
        default=None,
        required=False,
        indexed=False,
        readonly=False,
        validators=None,
        stored=True,
        on_update=None,
        compute=None,
        **kwargs,
    ):
        """
        Base field for all field types, have some common options that can be used any other field type too.

        Args:
            default (any, optional): default value. Defaults to None.
            required (bool, optional): required or not. Defaults to False.
            indexed (bool, optional): indexed or not. Defaults to False.
            readonly (bool, optional): can only get the value. Defaults to False.
            validators (list of function, optional): a list of functions that takes a value and raises ValidationError if not valid. Defaults to None.
            stored (bool, optional): if the fields should be stored or not, useful for computed fields. Defaults to True.
            on_update (callable, optional): a callable that takes the instance and new value on field updates. Defaults to None.
            compute (callable, optional): a callable that takes the instance and returns a computed value for this field. `on_update` won't be called in this case. Defaults to None.
        """
        self.default = default
        self.required = required
        self.indexed = indexed
        self.readonly = readonly
        self.kwargs = kwargs

        self.validators = validators
        if self.validators is None:
            self.validators = []

        self.stored = stored
        self.on_update = on_update
        self.compute = compute

    def preprocess(self, value):
        # TODO: make from/to raw methods only for serialization
        # and let preprocess/validate do the cleanup/checking step
        # and return the correct value that current field should hold
        # so, from_raw and to_raw are used only for serialization
        return value

    def validate_with_name(self, value, name):
        """
        validates the value using validate method and prepends the field name
        in case an exception was thrown

        Args:
            value (any): in case value is not valid
            name  (str): the field name

        Raises:
            ValidationError: The original validation error with the field name prepended to the message

        """
        try:
            self.validate(value)
        except ValidationError as e:
            raise ValidationError(f"{name}: " + str(e))

    def validate(self, value):
        """
        validate value if required and call custom self.validators if any

        Args:
            value (any): in case value is not valid

        Raises:
            ValidationError: [description]
        """
        if value is None:
            if self.required:
                raise ValidationError("field is required")

        for validator in self.validators:
            validator(value)

    def from_raw(self, value):
        """
        get the value of this field from primitive raw types

        Args:
            value (any): support value by this field type (if any)

        Returns:
            any: raw value
        """
        return value

    def to_raw(self, value):
        """
        get the raw value of this field

        Args:
            value (any): current value of this field

        Returns:
            any: a primitive raw value
        """
        return value

    @property
    def trigger_updates(self):
        return callable(self.on_update)

    @property
    def computed(self):
        return callable(self.compute)


class Typed(Field):
    def __init__(self, type_, **kwargs):
        """
        Base field for any type, it will hold values of `type_`

        Args:
            type_ (type): any type (class)
            kwargs: any keyword arguments supported by `Field`
        """
        self.type = type_
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None:
            if not isinstance(value, self.type):
                raise ValidationError(f"value '{value}' is not of type {self.type.__name__}")


class Boolean(Typed):
    def __init__(self, default=False, **kwargs):
        """
        Boolean fields to hold a `bool` value.

        values can be set using strings or numbers and will be converted to `bool` like:

        - "on", "off"
        - "yes", "no"
        - "true", "false"
        - 0, 1
        - 0, 1+2j

        Args:
            default (bool, optional): default value. Defaults to False.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=bool, default=default, **kwargs)

    def from_raw(self, value):
        """
        get bool value from strings and numbers

        Args:
            value (str or int or float or complex)

        Returns:
            bool: boolean value
        """
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ("yes", "on", "true"):
                return True
            if value in ("no", "off", "false"):
                return False
        elif isinstance(value, (int, float, complex)):
            return bool(value)

        # validate will do the check
        return value


class Integer(Typed):
    def __init__(self, default=0, min=None, max=None, **kwargs):
        """
        Intger field, the same as `Typed`, but with a type of `int`

        It can have a minimum value, if min is not set, it will ignore it.

        values can be set using strings like (will be converted to `int`):

        - "12", "1212  "

        Args:
            default (int, optional): default value. Defaults to 0.
            min (int, optional): minimum value (inclusive). Defaults to None.
            max (int, optional): maximum value (inclusive). Defaults to None.
            kwargs: any keyword arguments supported by `Field`
        """
        self.min = min
        self.max = max
        super().__init__(type_=int, default=default, min=min, **kwargs)

    def validate(self, value):
        super().validate(value)
        if value and self.min is not None:
            if value < self.min:
                raise ValidationError(f"cannot set values less than {self.min}")

        if value and self.max is not None:
            if value > self.max:
                raise ValidationError(f"cannot set values greater than {self.max}")

    def from_raw(self, value):
        if isinstance(value, str):
            try:
                value = int(value.strip())
            except ValueError:
                pass
        return value


class Float(Typed):
    def __init__(self, default=0.0, **kwargs):
        """
        Same as `Integer` field, but with a type of `float`.

        values can be set using strings like (will be converted to `float`):

        - "12.3", " 1212.23  "

        Args:
            default (float, optional): default value. Defaults to 0.0.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=float, default=default, min=min, **kwargs)

    def from_raw(self, value):

        if isinstance(value, str):
            value = value.strip()
        try:
            value = float(value)
        except ValueError:
            pass

        return value


class String(Typed):
    def __init__(self, maxlen=None, allow_empty=True, **kwargs):
        """
        Same as `Typed`, but with a type of `str`.

        If maxlen is set, it will validate the length of the string.

        Args:
            maxlen (int): maximum length allowed. Defaults to None
            allow_empty (bool): if empty string values are allowed or not. Defaults to True
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=str, **kwargs)
        self.maxlen = maxlen
        self.allow_empty = allow_empty

    def validate(self, value):
        super().validate(value)

        if not self.allow_empty and value == "":
            raise ValidationError("field does not allow empty values")

        if self.maxlen is not None:
            if value and len(value) > self.maxlen:
                raise ValidationError(f"length of the string exceeds {self.maxlen}")


class Secret(String):
    """
    Same as `String`, but encrypted by default.

    Should be used with sensitive data.

    Args:
        kwargs: any keyword arguments supported by `String`
    """


class Object(Typed):
    def __init__(self, type_, type_kwargs=None, **kwargs):
        """
        An embedded Base object field of any type.

        Args:
            type_ (type): Base object type (class)
            type_kwargs (dict, optional): kwargs as a dict to be passed to Base instance when created. Defaults to None.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=type_, **kwargs)
        self.type_kwargs = type_kwargs

        if self.type_kwargs is None:
            self.type_kwargs = {}

        if not self.default:
            # make it callable to create different objects
            # not a single one as a default for all
            self.default = lambda: self.type(**self.type_kwargs)

    def validate(self, value):
        """
        validate Base objects

        Args:
            value (Base): object
        """
        super().validate(value)
        if value:
            value.validate()

    def to_raw(self, obj):
        """
        get raw value of an object as dict

        Args:
            obj (Base): base object

        Returns:
            dict: raw data
        """
        if obj:
            return obj._get_data()

    def from_raw(self, data):
        """
        get an object from dict

        Args:
            data (dict): data dict

        Returns:
            Base: base object
        """
        if isinstance(data, dict):
            return self.type(**data)
        return data


class List(Field):
    def __init__(self, field, **kwargs):
        """
        A list field for any field types.

        Args:
            field (Field): a field instance of any fields, e.g. `fields.String(maxlen=14)`.
            kwargs: any keyword arguments supported by `Field`
        """
        self.field = field
        super().__init__(**kwargs)

    def validate(self, value):
        """
        validate the value of every item in the list
        Will just call the field.validate of the given field
        """
        super().validate(value)

        if value is None:
            value = []

        for item in value:
            self.field.validate(item)

    def to_raw(self, values):
        """
        get a list of values as raw

        Args:
            values (list): list of items of field type

        Returns:
            list: list of raw values
        """
        if not values:
            return []

        return [self.field.to_raw(value) for value in values]

    def from_raw(self, values):
        """
        get a list of field type from raw values

        Args:
            values (list): list of raw values

        Returns:
            list: list of objects of field type
        """
        if not values:
            return []

        return [self.field.from_raw(value) for value in values]


class Enum(Typed):
    def __init__(self, enum_type, **kwargs):
        """
        Enum field, to be used with `enum.Enum`.

        Example:

        ```python
        class UserType(Enum):
            USER = "user"
            ADMIN = "admin"

        class User(Base):
            field = fields.Enum(UserType)
        ```

        Will hold values of type `enum.Enum`.

        Args:
            enum_type (type): enum type (class)
            kwargs: any keyword arguments supported by `Field`
        """
        # default is the first value
        default = next(iter(enum_type))
        super().__init__(type_=enum_type, default=default, **kwargs)
        self.enum_type = enum_type

    def to_raw(self, enum_obj):
        """
        get enum value

        Args:
            enum_obj (enum.Enum): enum object

        Returns:
            any: enum value
        """
        if enum_obj:
            return enum_obj.value

    def from_raw(self, value):
        """
        get an enum object from value

        Args:
            value (any): any value

        Returns:
            enum: enum object of enum type of the field
        """
        try:
            return self.enum_type(value)
        except ValueError:
            # let validate() do the validation
            return value


class Email(String):
    def __init__(self, default="", **kwargs):
        """
        Email field, will validate the value of emails

        will hold string email values.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: other keyword arguments supported by `string`
        """
        super().__init__(default=default, **kwargs)
        self.regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def validate(self, value):
        """
        check whether provided value is a valid email representation

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not a telephone
        """
        super().validate(value)
        if value and not re.match(self.regex, value):
            raise ValidationError(f"'{value}' is not a valid Email address")


class Path(String):
    # TODO: Validate that it is working on windows
    def __init__(self, default="", **kwargs):
        """
        Path field, will validate the value of file system paths

        Will hold string path values.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: other keyword arguments supported by `Field`
        """
        super().__init__(default, **kwargs)
        self.regex = r"^(/[^/ ]*)+/?$"

    def validate(self, value):
        """
        check whether provided value is a valid path representation

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not a telephone
        """
        super().validate(value)
        if value and not re.match(self.regex, value):
            raise ValidationError(f"'{value}' is not a valid Path")


class URL(String):
    def __init__(self, default="", **kwargs):
        """
        URL field, will validate the value of urls

        Will hold string URLs.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: other keyword arguments supported by `Field`
        """
        super().__init__(default=default, **kwargs)
        self.regex = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"

    def validate(self, value):
        """
        check whether provided value is a valid URL representation

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not a telephone
        """
        super().validate(value)
        if value:
            url = urlparse(value)
            if not url.scheme or not url.netloc:
                raise ValidationError(f"'{value}' is not a valid URL address")


class Tel(String):
    def __init__(self, default="", **kwargs):
        """
        Telephone field, will validate the value of telephone numbers

        Will hold telephone values as strings.

        It will strip any additional characters that are not numbers.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: other keyword arguments supported by `String`
        """
        super().__init__(default=default, **kwargs)
        self.regex = r"^\+?[0-9]{6,15}(?:x[0-9]+)?$"

    def validate(self, value):
        """
        check whether provided value is a valid telephone number representation

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not a telephone
        """
        super().validate(value)
        if value and not re.search(self.regex, value):
            raise ValidationError(f"'{value}' is not a valid Telephone")

    def from_raw(self, value):
        """clean the telephone value from unwanted signs like , - ( )"""
        if value is not None:
            value = value.replace(",", "")
            value = value.replace("-", "")
            value = value.replace("(", "")
            value = value.replace(")", "")
            value = value.replace(" ", "")
            return value
        return value


class IPMixin:
    def is_a(self, value, *types):
        """
        try creating any type of `types` from the given value

        Args:
            value (str)

        Returns:
            bool: `True` if any matched, `False` otherwise
        """
        matched = False

        for type_ in types:
            try:
                type_(value)
                matched |= True
            except ValueError:
                continue

        return matched

    def is_ipv4(self, value):
        """
        check if a given value is a v4 IP address

        Args:
            value (str): ip address

        Returns:
            bool: `True` if it's a valid v4 IP address
        """
        return self.is_a(value, ipaddress.IPv4Address)

    def is_ipv6(self, value):
        """
        check if a given value is a v6 IP address

        Args:
            value (str): IP address

        Returns:
            bool: `True` if it's a valid v6 IP address
        """
        return self.is_a(value, ipaddress.IPv6Address)

    def is_ip(self, value):
        """
        check if a given value is a v4/v6 IP address

        Args:
            value (str): IP address

        Returns:
            bool: `True` if it's a valid  v4/v6 IP address
        """
        return self.is_ipv4(value) or self.is_ipv6(value)

    def is_iface(self, value):
        """
        check if a given value is an IP interface

        Args:
            value (str): IP interface

        Returns:
            bool: `True` if it's a valid v4/v6 IP interface
        """
        return self.is_a(value, ipaddress.IPv4Interface, ipaddress.IPv6Interface)


class IPAddress(IPMixin, String):
    def __init__(self, default="0.0.0.0", **kwargs):
        """
        IP address field, will validate the value of ip address (v4 and v6)

        Will hold string ip addresses.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(default=default, **kwargs)

    def validate(self, value):
        """
        check whether provided value is a valid IPaddress representation
        including IPv4,IPv6 and network

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not an IPAddress
        """
        super().validate(value)
        if value and not self.is_ip(value):
            raise ValidationError(f"'{value}' is not a valid IP address")

    def from_raw(self, value):
        if isinstance(value, str):
            if value.strip().lower() == "localhost":
                value = "127.0.0.1"
        return value


class IPRange(IPMixin, String):
    def __init__(self, default="::/128", **kwargs):
        """
        ip range field, will validate the value of ip ranges (v4 and v6)

        will be stored as a string.

        Args:
            default (str, optional): default value. Defaults to ""
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(default=default, **kwargs)

    def validate(self, value):
        """
        check whether provided value is a valid IPaddress representation
        including IPv4,IPv6 and network

        Args:
            value (str)

        Raises:
            ValidationError: in case the value is not an IPAddress
        """

        super().validate(value)
        if value and not self.is_iface(value):
            raise ValidationError(f"'{value}' is not a valid IP range/interface")


class Port(Integer):
    def __init__(self, **kwargs):
        """
        Port field, will check if the given port is within the range of 0-65535.

        Will hold integers, but also accepts string values like `"8080"`.

        Args:
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(min=0, max=65535, **kwargs)

    def validate(self, value):
        try:
            super().validate(value)
        except ValidationError:
            raise ValidationError("value is not in range of 0-65535")


class GUID(String):
    def __init__(self, default=None, **kwargs):
        """
        UUID v4 field, will be auto-generated by default.

        Will hold the UUID as a string.

        It accepts setting UUID value by many ways and converts them to strings:

        - Strings like: `"12345678-1234-4678-9234-567812345678"`
        - Bytes like: `b"\x12\x34\x56\x78" * 4`
        - Integer like: `0x12345678123456781234567812345678`
        - UUID objects of type uuid.UUID

        Args:
            default (str, optional): default value, will be auto-generated if None. Defaults to None
            kwargs: other keyword arguments supported by `String`
        """
        if not default:
            default = lambda: str(uuid.uuid4())
        super().__init__(default=default, **kwargs)

    def validate(self, value):
        super().validate(value)

        if not value:
            return

        try:
            uuid.UUID(value, version=4)
        except ValueError as valexc:
            raise ValidationError(f"''{value}'' is invalid, {valexc}") from valexc

    def from_raw(self, value):
        """
        convert string, bytes, int to UUID object, then to a string

        Args:
            value (int or str or bytes or uuid.UUID): [description]

        Returns:
            str: UUID string
        """

        if isinstance(value, uuid.UUID):
            return str(value)

        try:
            uuid_obj = None
            if isinstance(value, int):
                uuid_obj = uuid.UUID(int=value, version=4)
            elif isinstance(value, str):
                uuid_obj = uuid.UUID(value, version=4)
            elif isinstance(value, bytes):
                uuid_obj = uuid.UUID(bytes=value, version=4)

            if uuid_obj:
                return str(uuid_obj)

            # return as is to be validated later
            return value
        except ValueError:
            # failed to get uuid from raw value
            # return as is to be validated later
            return value


class DateTimeMixin:
    def get_arrow_obj(self, value):
        """
        get an arrow object from int, float and str and `datetime.time` objects.

        Args:
            value (int or float or str): timestamp (utc) or e.g. "1998-01-03"

        Returns:
            arrow.Arrow: arrow object in utc
        """
        if isinstance(value, datetime.time):
            # convert to string, as there's no direct way i know of
            # to convert from datetime.time objects to arrow directly
            value = value.strftime(self.format)

        if isinstance(value, str):
            return arrow.Arrow.strptime(value, self.format).to("utc")

        return arrow.get(value)

    def get_timestamp(self, obj):
        """
        get a utc timestamp from datetime/date/time objects


        Args:
            obj (datetime.datetime or datetime.date or datetime.time): date/time or datetime object

        Returns:
            int or float: utc timestamp
        """
        return arrow.get(obj).to("utc").timestamp

    def from_raw(self, value):
        """
        get a datetime object from a numberic (epoch) or string value


        Args:
            value (str or int or float): value as a number or a string

        Returns:
            datetime.datetime or datetime.date or datetime.time: datetime or date/time object
        """
        if isinstance(value, (int, float, str)):
            try:
                obj = self.get_arrow_obj(value)
                if self.type == datetime.datetime:
                    return obj.datetime
                elif self.type == datetime.date:
                    return obj.date()
                elif self.type == datetime.time:
                    return obj.time()
            except (ValueError, arrow.parser.ParserError):
                # will be caught by validate
                pass
        return value

    def to_raw(self, dt_obj):
        """
        get a utc timestamp from datetime object

        Args:
            dt_obj (datetime.datetime or datetime.date or datetime.time): datetime object

        Returns:
            int or float: utc timestamp
        """
        if dt_obj:
            return self.get_arrow_obj(dt_obj).to("utc").timestamp

    def validate(self, value):
        if isinstance(self.from_raw(value), str):
            # cannot convert from string, still an invalid format
            raise ValidationError(f"'{value}' is not in the format of '{self.format}'")

        super().validate(value)


class DateTime(DateTimeMixin, Typed):
    # maybe add something like auto_now and auto_today for date/time fields
    def __init__(self, default=None, format_=None, **kwargs):
        """
        datetime field, will hold datetime.datetime objects.

        values can be set using strings in the given `format_` too like "12/1/2020" or a utc timestamp,
        they will converted to objects.

        Args:
            default (datetime): default value. Defaults to None.
            format_ (str, optional): datetime format. Defaults to "%Y-%m-%d %H:%M" if None.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=datetime.datetime, default=default, **kwargs)
        if not format_:
            format_ = "%Y-%m-%d %H:%M"
        self.format = format_


class Date(DateTimeMixin, Typed):
    def __init__(self, default=None, format_=None, **kwargs):
        """
        date field, will hold datetime.date objects.

        values can be set using strings in the given `format_` too like "12/1/2020" or a utc timestamp,
        they will converted to objects.

        Args:
            default (date): default value. Defaults to None.
            format_ (str, optional): date format. Defaults to "%Y-%m-%d" if None.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(type_=datetime.date, default=default, **kwargs)
        if not format_:
            format_ = "%Y-%m-%d"
        self.format = format_


class Time(DateTimeMixin, Typed):
    def __init__(self, default=None, format_=None, **kwargs):
        """
        time field, will hold utc datetime.time objects

        values can be set using strings in the given `format_` too like "12:13" or a utc timestamp,
        they will converted to objects.

        Args:
            default (date): default value. Defaults to None.
            format_ (str, optional): time format. Defaults to "%H:%M" if None.
            kwargs: any keyword arguments supported by `Field`
        """
        super().__init__(default=default, type_=datetime.time, **kwargs)
        if not format_:
            format_ = "%H:%M"
        self.format = format_


class Bytes(Typed):
    def __init__(self, default=b"", encoding="utf-8", **kwargs):
        """
        same as string field, but will hold `bytes`.

        Args:
            default (b"", optional): default value. Defaults to b""
            encoding: encoding to be used when serializing the value. Defaults to "utf-8"
            kwargs: any keyword arguments supported by `Field`
        """
        self.encoding = encoding
        super().__init__(default=default, type_=bytes, **kwargs)

    def from_raw(self, value):
        if isinstance(value, str):
            return value.encode(self.encoding)
        return value

    def to_raw(self, value):
        if value:
            return value.decode(self.encoding)


class Json(String):
    def __init__(self, default="{}", encoding="utf-8", **kwargs):
        """
        Json field, will check if the value is a valid json string.

        It will hold json strings, if the value is not string, it will be converted.

        Args:
            default (str, optional): default value. Defaults to "{}"
            encoding: encoding to be used when serializing the value. Defaults to "utf-8"
            kwargs: other keyword arguments supported by `String`
        """
        self.encoding = encoding
        super().__init__(default=default, **kwargs)

    def validate(self, value):
        """
        check whether provided value is a valid json

        Args:
            value (str)

        Raises:
            ValidationError: in case the value isn't a valid json
        """
        super().validate(value)

        if not value:
            return

        # if it's a string, try to load it
        try:
            json.loads(value, encoding=self.encoding)
        except Exception as e:
            raise ValidationError(f"'{value}' isn't a valid json, {e}") from e

    def from_raw(self, value):
        """
        convert non-string values to json string

        Args:
            value (any): non-string value

        Returns:
            str: a json string
        """
        if not isinstance(value, (str, bytes, bytearray)):
            try:
                value = json.dumps(value)
            except:
                pass
        return value


class Factory(Field):
    def __init__(self, type_, factory_type=None, **kwargs):
        """
        A factory field for any `Base` type, also, you can specify your factory type/class

        Example:

        ```python
        class User(Base):
            name = fields.String()

        class Server(Base):
            users = fields.Factory(User)
        ```

        Another example with a custom factory class:

        ```python
        class User(Base):
            name = fields.String()

        class UserFactory(StoredFactory):

            def list_from_remote(self):
                # list users from remote storage
                # ...

        class Server(Base):
            users = fields.Factory(User, factory_type=UserFactory)
        ```

        Args:
            type_ (Base): any base type to be used by the factory
            factory_type (`BaseFactory`, optional): factory class/type. Defaults to None.
        """
        # value type will be factory
        # make sure stored default value is True
        kwargs["stored"] = kwargs.get("stored", True)
        super().__init__(readonly=True, **kwargs)
        # but we keep the type of any Base class
        # so, we can init a Factory with it
        self.type = type_
        if factory_type:
            self.factory_type = factory_type
        else:
            if self.stored:
                self.factory_type = StoredFactory
            else:
                self.factory_type = BaseFactory

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, self.factory_type):
            raise ValidationError(f"factory type is not {self.factory_type}")

    def from_raw(self, value):
        return value

    def to_raw(self, value):
        return None
