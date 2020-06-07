# Identity

Identity contains information that identify the user to other threebot machines.

## configuring identity

To configure your identity:

```python
j.core.identity.configure("threebot_name", "threebot_mail", "path of file containing your seed words")
```

To access his threebot id:

```python
j.core.identity.tid
```

The tool gets the id as follows:

- If user already registered on the same machine will get directly from config
- If is a new registration will contact the explorer to gets the user information and verifies it against local config and set the id
- If a new user will create the user and register it on the explorer and continue like the preceding point

## Encryption

`nacl` property wrapes some signing/encrypting functionalities using the user private key which is generated from his seed words.

The user private key can be accessed from the identity:

```python
j.core.identity.nacl.private_key
<nacl.public.PrivateKey at 0x7f2749f4e510>
```

Same with the signing key:

```python
j.core.identity.nacl.signing_key
<nacl.signing.SigningKey at 0x7f2760aecf10>
```
