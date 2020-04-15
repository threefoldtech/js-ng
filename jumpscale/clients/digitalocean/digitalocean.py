"""This module is used to manage your digital ocean account, create droplet,list all the droplets, destroy droplets, create project, list all the projects and delete project
# prerequisites
    ## you must have a sshkey client  and loaded with you public key 
'''python
ssh = j.clients.sshkey.get(name= "test")
ssh.private_key_path = "/home/rafy/.ssh/id_rsa" 
ssh.load_from_file_system()
'''
    ## 
"""
from jumpscale.god import j
from jumpscale.clients.base import Client
from jumpscale.core.base import fields
from .project import ProjectManagement
import digitalocean
from jumpscale.core.base import StoredFactory


class VM:
    name = fields.String()
    do_id = fields.String()


def convert_to_valid_identifier(name):
    return "_" + name.replace(" ", "_")


class ProjectFactory(StoredFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # def new(self, name, *args, **kwargs):
    #     valid_name = convert_to_valid_identifier(name)
    #     instance = super().new(valid_name, *args, **kwargs)
    #     instance.name = name
    #     return instance

    def list_remote(self):
        """
        Returns list of projects on Digital Ocean
        """
        return ProjectManagement.list(self.parent_instance.client)

    def check_project_exist_remote(self, name):
        for project in self.list_remote():
            if project.name == name:
                return True
        return False

    # def list_all_projects(self):
    #     """
    #     Returns list of projects, if there is not projects created it will return
    #     the projects created on Digital Ocean
    #     """
    #     projects = self.list_all()
    #     if not projects:
    #         for project in self.list_project_in_digital_ocean():
    #             # project_temp = self.new("_" + project.name.replace(" ", "_"))
    #             # project_temp.project_name = project.name
    #             self.new(project.name)
    #     return self.list_all()

    # def _project_get(self, name):
    #     for project in self.projects:
    #         if project.name.lower() == name.lower():
    #             return project
    #     return None

    # def get(self, name):
    #     for project in self.list_all_projects():
    #         project.project_name


class Project(Client):
    do_name = fields.String()

    def create_project(self):
        print("project created")

    def set_digital_ocean_name(self, name):
        self.do_name = name

    def deploy(self, name, purpose, description="", environment="", is_default=False):
        """Create a digital ocean project

        :param name: name of the project
        :type name: str
        :param purpose: purpose of the project
        :type purpose: str
        :param description: description of the project, defaults to ""
        :type description: str, optional
        :param environment: environment of project's resources, defaults to ""
        :type environment: str, optional
        :param is_default: make this the default project for your user
        :type is_default: bool
        :return: project instance
        :rtype: Project
        """
        if self._project_get(name):
            raise j.exceptions.Value("A project with the same name already exists")

        project = ProjectManagement(
            token=self.token_,
            name=name,
            purpose=purpose,
            description=description,
            environment=environment,
            is_default=is_default,
        )
        project.create()

        if is_default:
            project.update(is_default=True)

        # self._projects.append(project) this for cashing

        return project

    # def project_list(self):
    #     print("project list ")


# class Droplet


class DigitalOcean(Client):
    name = fields.String()
    token_ = fields.String()
    # project_name = fields.String()
    vms = fields.List(fields.Object(VM))
    # projects = ProjectFactory(Project)
    projects = fields.Factory(Project, factory_type=ProjectFactory)
    # listing_project

    def __init__(self):
        super().__init__()
        self._client = None
        self.reset()

    def reset(self):
        self._droplets = []
        self._projects = []  # list_all
        self._digitalocean_images = None
        self._digitalocean_sizes = None
        self._digitalocean_regions = None
        self._sshkeys = None

    @property
    def client(self):
        """If client not set, a new client is created

        :raises RuntimeError: Auth token not configured
        :return: client
        :rtype:
        """

        if not self._client:
            self._client = digitalocean.Manager(token=self.token_)
        return self._client

    @property
    def digitalocean_images(self):
        if not self._digitalocean_images:
            self._digitalocean_images = self.client.get_distro_images()
        return self._digitalocean_images

    @property
    def digitalocean_myimages(self):
        return self.client.get_images(private=True)

    @property
    def digitalocean_sizes(self):
        if not self._digitalocean_sizes:
            self._digitalocean_sizes = self.client.get_all_sizes()
        return self._digitalocean_sizes

    @property
    def digitalocean_regions(self):
        if not self._digitalocean_regions:
            self._digitalocean_regions = self.client.get_all_regions()
        return self._digitalocean_regions

    @property
    def digitalocean_region_names(self):
        return [i.slug for i in self.digitalocean_regions]

    @property
    def sshkeys(self):
        if not self._sshkeys:
            self._sshkeys = self.client.get_all_sshkeys()
        return self._sshkeys

    def droplet_exists(self, name):
        for droplet in self.droplets:
            if droplet.name.lower() == name.lower():
                return True
        return False

    def _droplet_get(self, name):
        for droplet in self.droplets:
            if droplet.name.lower() == name.lower():
                return droplet
        return False

    def _sshkey_get_default(self):
        pubkeyonly = self.sshkey.public_key
        for item in self.sshkeys:
            if item.public_key.find(pubkeyonly) != -1:
                return item
        return None

    def sshkey_set_default(self, default_sshkey):
        self.sshkey = default_sshkey

    def sshkey_get(self, name):
        for item in self.sshkeys:
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find key:%s" % name)

    def region_get(self, name):
        for item in self.digitalocean_regions:
            if name == item.slug:
                return item
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find region:%s" % name)

    @property
    def digitalocean_account_images(self):
        return self.digitalocean_images + self.digitalocean_myimages

    def image_get(self, name):
        for item in self.digitalocean_account_images:
            if item.description:
                name_do1 = item.description.lower()
            else:
                name_do1 = ""
            name_do2 = item.distribution + " " + item.name
            print(f" - {name_do1}--{name_do2}")
            if name_do1.lower().find(name.lower()) != -1 or name_do2.lower().find(name.lower()) != -1:
                return item
        raise j.exceptions.Base("did not find image:%s" % name)

    def image_names_get(self, name=""):
        res = []
        name = name.lower()
        for item in self.digitalocean_images:
            if item.description:
                name_do = item.description.lower()
            else:
                name_do = item.distribution + " " + item.name
            if name_do.find(name) != -1:
                res.append(name_do)
        return res

    def droplet_create(
        self,
        name="test",
        sshkey=None,
        region="Amsterdam 3",
        image="ubuntu 18.04",
        size_slug="s-1vcpu-2gb",
        delete=True,
        project_name=None,
    ):
        """

        :param name:
        :param sshkey:
        :param region:
        :param image:
        :param size_slug: s-1vcpu-2gb,s-6vcpu-16gb,gd-8vcpu-32gb
        :param delete:
        :param mosh: when mosh will be used to improve ssh experience
        :param project_name: project to add this droplet it. If not specified the default project will be used.
        :return: droplet,sshclient
        """
        project = None
        if project_name:
            project = self._project_get(project_name)
            if not project:
                raise j.exceptions.Input("could not find project with name:%s" % project_name)

        # Get ssh
        if not sshkey:
            sshkey_do = self._sshkey_get_default()

            if not sshkey_do:
                # means we did not find the sshkey on digital ocean yet, need to create
                key = digitalocean.SSHKey(token=self.token_, name=self.sshkey.name, public_key=self.sshkey.public_key)
                key.create()
            sshkey_do = self._sshkey_get_default()
            assert sshkey_do
            sshkey = sshkey_do.name

        if self.droplet_exists(name):
            dr0 = self._droplet_get(name=name)
            if delete:
                dr0.destroy()
            else:
                sshcl = j.clients.sshclient.get(name="do_%s" % name, host=dr0.ip_address, sshkey=sshkey)
                # sshcl.save()
                return dr0, sshcl

        sshkey = self.sshkey_get(sshkey)

        region = self.region_get(region)

        imagedo = self.image_get(image)

        img_slug_or_id = imagedo.slug if imagedo.slug else imagedo.id
        droplet = digitalocean.Droplet(
            token=self.token_,
            name=name,
            region=region.slug,
            image=img_slug_or_id,
            size_slug=size_slug,
            ssh_keys=[sshkey],
            backups=False,
        )
        droplet.create()
        self._droplets.append(droplet)
        self.reset()

        if project:
            project.assign_resources(["do:droplet:%s" % droplet.id])

        vm = self._vm_get(name)
        vm.do_id = droplet.id

    def _vm_get(self, name, new=True):
        vm = None
        for single_vm in self.vms:
            if single_vm.name == name:
                vm = single_vm
                break
        if new:
            if not vm:
                vm = VM()
                vm.name = name
                self.vms.append(vm)
        return vm

    def _vm_exists(self, name):
        return self._vm_get(name, new=False) != None

    def droplet_get(self, name):
        if not self.droplet_exists(name):
            raise j.exceptions.Input("could not find vm with name:%s" % name)
        return self._droplet_get(name)

    @property
    def droplets(self):
        if not self._droplets:
            self._droplets = []
            for d in self.client.get_all_droplets():
                self._droplets.append(d)
        return self._droplets

    def droplets_all_delete(self, ignore=None, interactive=True, project=None):

        if not ignore:
            ignore = []

        def test(ignore, name):
            if name.startswith("TF-"):
                return False
            for item in ignore:
                if name.lower().find(item.lower()) != -1:
                    return False
            return True

        todo = []
        for droplet in self.droplets_list(project):
            if test(ignore, droplet.name):
                todo.append(droplet)
        if todo != []:
            todotxt = ",".join([i.name for i in todo])
            if not interactive or j.tools.console.ask_yes_no("ok to delete:%s" % todotxt):
                for droplet in todo:
                    droplet.destroy()

    def droplets_all_shutdown(self, project=None):
        for droplet in self.droplets_list(project):
            droplet.shutdown()

    def droplets_list(self, project=None):
        """list droplets

        :param project: name of the project to filter on, defaults to None
        :type project: str, optional
        :raises j.exceptions.Input: raise an error if project doesn't exist.
        :return: list of droplets
        :rtype: [Droplet]
        """
        if not project:
            return self.droplets

        project = self._project_get(project)
        if not project:
            raise j.exceptions.Input("could not find project with name:%s" % project)

        return project.list_droplets()

    # def _projects_list(self):
    #     return ProjectManagement.list(self.client)

    # @property
    # def projects(self):
    #     """property to return all the cached projects

    #     :return: list of project
    #     :rtype: [Project]
    #     """
    #     if not self._projects:
    #         for project in self._projects_list():
    #             self._projects.append(project)
    #     return self._projects

    # def _project_get(self, name):
    #     for project in self.projects:
    #         if project.name.lower() == name.lower():
    #             return project
    #     return None

    # def project_create(self, name, purpose, description="", environment="", is_default=False):
    #     """Create a digital ocean project

    #     :param name: name of the project
    #     :type name: str
    #     :param purpose: purpose of the project
    #     :type purpose: str
    #     :param description: description of the project, defaults to ""
    #     :type description: str, optional
    #     :param environment: environment of project's resources, defaults to ""
    #     :type environment: str, optional
    #     :param is_default: make this the default project for your user
    #     :type is_default: bool
    #     :return: project instance
    #     :rtype: Project
    #     """
    #     if self._project_get(name):
    #         raise j.exceptions.Value("A project with the same name already exists")

    #     project = ProjectManagement(
    #         token=self.token_,
    #         name=name,
    #         purpose=purpose,
    #         description=description,
    #         environment=environment,
    #         is_default=is_default,
    #     )
    #     project.create()

    #     if is_default:
    #         project.update(is_default=True)

    #     self._projects.append(project)

    #     return project

    def project_get(self, name):
        """Get an existing project

        :param name: project name
        :type name: str
        :raises j.exceptions.Input: raises an error if there is no project with this name
        :return: Project object
        :rtype: Project
        """
        project = self._project_get(name)
        if not project:
            raise j.exceptions.Input("could not find project with name:%s" % name)
        return project

    def project_delete(self, name):
        """Delete an exisiting project.
        A project can't be deleted unless it has no resources.

        :param name: project name
        :type name: str
        :raises j.exceptions.Input: raises an error if there is no project with this name
        """
        project = self._project_get(name)
        if not project:
            raise j.exceptions.Input("could not find project with name:%s" % name)
        project.delete()

        self._projects.remove(project)

    def __str__(self):
        return "digital ocean client:%s" % self.name

    __repr__ = __str__
