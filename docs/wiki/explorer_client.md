# Explorer
The explorer is the component that is responsible to host all the public information about the nodes running 0-OS, the farms, the users identity and the capacity reservations.

The explorer exposes both a web UI and a REST API.

- The web UI allows users to discover all the nodes and farms in the grid.
- The API is used by nodes and users.

# Explorer Client

- Get explorer client
```python
explorer = j.clients.explorer.get("explore_client","http://explorer.grid.tf/explorer")
```
### Users
- List all users in explorer
```python
explorer.users.list()
```
- Get specific user
```python
explorer.users.get(tid="USER_TID", name="3BOT_NAME", email="3BOT_EMAIL")
```
- Create new user
```python
user = explorer.users.new()
user.email="3BOT_EMAIL"
user.name = "3BOT_NAME"
```
- Register user in explorer
```python
explorer.users.register(user)
```

### Farms
- List all farms in explorer
```python
explorer.farms.list()
```
-  get specific farm
```python
explorer.farms.get(farm_id="ID", farm_name="NAME")
```
-  Create new farm
```python
farm = explorer.farms.new()
farm.name = "FARM_NAME"
farm.email = "FARM_EMAIL"
farm.wallet_addresses = "WALLET_ADDRESSESS"
```
- Register new farm
```python
explorer.farms.register(farm)
```

### Nodes
- List all nodes in explorer
```python
explorer.nodes.list()
```
- List all nodes with the possibility of filtering them based on resources specified
```python
explorer.nodes.list(country="COUNTRY",city="CITY",cru="CPU",sru="SSD_SIZE",mru="MEMORY_SIZE",hru="HDD_SIZE")
```
- Get Specific node
```python
explorer.nodes.get(node_id="NODE_ID")
```
- Check if node free to use or not
```python
explorer.nodes.configure_free_to_use(node_id="NODE_ID",free=True)
```

### Reservations
- List all reserations of specific 3bot user with the possibility of filtering
```python
explorer.reservations.list(customer_tid="TID", next_action="NEXT_ACTION_OF_RESERVATION", page="NUMBER_OF_PAGE")
```

- Create new reservation
```python
res = explorer.reservations.new()
res.customre_tid = "CUSTOMER_TID"
res.data_reservation = YOUR_DATA_RESERVATION
res.json = "RESERVATION_JSON"
```
- Get reservation
```python
explorer.reservations.get(reservation_id="ID")
```
- Delete reservation
```python
explorer.reservations.sign_delete(reservation_id="ID",tid="CUSTOMER_TID",signature="3BOT_signature")
```
