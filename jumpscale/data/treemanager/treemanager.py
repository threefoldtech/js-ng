class TreeNode:
    def __init__(self, name, parent, data=None):
        self.name = name
        self.parent = parent
        self.data = data
        self.children = {}

    def add_child(self, node):
        child_name = node.name
        if child_name in self.children:
            # throw an error or override? (overriding for now)
            pass
        self.children[child_name] = node

    def search_by_name(self, name):
        return self.search_custom(lambda x: x.name == name)

    def search_by_value(self, val):
        return self.search_custom(lambda x: x.value == val)

    def search_custom(self, func):
        result = []
        for v in self.children.values():
            result.extend(v.search_custom(func))

        if self.name != "" and func(self):
            result.append(self)
        return result

    def get_child_by_name(self, name):
        return self.children.get(name)

    def remove_child(self, node):
        self.remove_child_by_name(node.name)

    def remove_child_by_name(self, name):
        if name in self.children:
            del self.children[name]

    def __str__(self, indentation=0):
        result = "\t" * indentation + self._string_repr() + "\n"
        for v in self.children.values():
            result += v.__str__(indentation + 1)
        return result

    def _string_repr(self):
        if self.name == "":
            return "dummy_root"
        else:
            return self.name + str(self.data).replace("\n", "\\n")


class Tree:
    def __init__(self):
        self.root = TreeNode("", None)

    def search_by_value(self, value):
        return self.root.search_by_value(value)

    def search_by_name(self, name):
        return self.root.search_by_name(name)

    def search_custom(self, func):
        return self.root.search_custom(func)

    def get_by_path(self, path):
        path_arr = path.split(".")
        current_node = self.root
        for name in path_arr:
            next_node = current_node.get_child_by_name(name)
            if next_node is None:
                return None
            current_node = next_node
        return current_node

    def remove_node(self, node):
        if node == self.root:
            raise RuntimeError("Can't remove the root node")
        node.parent.remove_child(node.name)

    def add_node_by_path(self, path, data=None):
        path_arr = path.split(".")
        current_node = self.root
        for path_name in path_arr[:-1]:
            next_node = current_node.get_child_by_name(path_name)
            if next_node is None:
                # Create along the way or throw an error? (creating for now)
                next_node = TreeNode(path_name, current_node)
                current_node.add_child(next_node)
            current_node = next_node
        new_node = TreeNode(path_arr[-1], current_node, data)
        return current_node.add_child(new_node)

    def remove_node_by_path(self, path, data=None):
        path_arr = path.split(".")
        current_node = self.root
        parent_node = None
        for path_name in path_arr:
            next_node = current_node.get_child_by_name(path_name)
            if next_node is None:
                return None
            parent_node = current_node
            current_node = next_node
        return parent_node.remove_child(current_node)

    def __str__(self):
        return self.root.__str__(0)


if __name__ == "__main__":
    tree = Tree()
    tree.add_node_by_path("root", {"file_name": "root", "modified": "12/3/2019"})
    tree.add_node_by_path("etc", {"file_name": "etc", "modified": "13/3/2018"})
    tree.add_node_by_path("etc.hosts", {"file_name": "hosts", "modified": "14/3/2017"})
    tree.add_node_by_path("etc.passwd", {"file_name": "passwd", "modified": "14/3/2016"})
    too_old = tree.search_custom(lambda x: x.data["modified"].split("/")[-1] < "2018")
    print("Too old files (before 2018):\n")
    for f in too_old:
        print(f.name + "\n")
    print("Tree before removing /etc/hosts")
    print(tree)
    print("Tree after removing /etc/hosts")
    tree.remove_node_by_path("etc.hosts")
    print(tree)
    passwd_file = tree.get_by_path("etc.passwd")
    passwd_date = passwd_file.data["modified"]
    print("Last time /etc/passwd was modified is: " + passwd_date)
