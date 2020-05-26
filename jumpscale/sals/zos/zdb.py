from .crypto import encrypt_for_node
from jumpscale.core.exceptions import Input
from .id import _next_workload_id
from jumpscale.clients.explorer.models import TfgridWorkloadsReservationZdb1


class ZDB:
    def __init__(self, explorer):
        self._nodes = explorer.nodes

    def create(self, reservation, node_id, size, mode, password, disk_type="SSD", public=False):
        """add a 0-db namespace workload to the reservation

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation obejct to add the volume to
            node_id (str): id of the node to reserve the volume
            size (int): size of the namespace in GiB
            mode (str): mode of the 0-db, can be 'seq' or 'user'
            password (str): password of the namespace. if you don't want password use an empty string
            disk_type (str, optional): type of disk,can be SSD or HDD. Defaults to "SSD".
            public (bool, optional): if public is True, anyone can write to the namespace without being authenticated. Defaults to False.

        Raises:
            Input: if disk_type os not supported
            Input: if mode is not suported

        Returns:
            [type]: newly created zdb workload
        """
        if disk_type not in ["SSD", "HDD"]:
            raise Input("disk type can only be SSD or HDD")
        if mode not in ["seq", "user"]:
            raise Input("mode can only be 'seq' or 'user'")

        zdb = TfgridWorkloadsReservationZdb1()
        zdb.workload_id = _next_workload_id(reservation)
        zdb.node_id = node_id
        zdb.size = size
        zdb.mode = mode
        if password:
            node = self._nodes.get(node_id)
            zdb.password = encrypt_for_node(node.public_key_hex, password)
        zdb.disk_type = disk_type.lower()
        reservation.data_reservation.zdbs.append(zdb)
        return zdb
