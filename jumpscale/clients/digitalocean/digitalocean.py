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


class ProjectFactory(StoredFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def get_project_exist_remote(self, name):
        for project in self.list_remote():
            if project.name == name:
                return project
        raise j.exceptions.Input("could not find project with name:%s on you Digital Ocean account" % name)


class Project(Client):
    do_name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_digital_ocean_name(self, name):
        self.do_name = name

    def deploy(self, purpose, description="", environment="", is_default=False):
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

        if self.parent.projects.check_project_exist_remote(self.do_name):
            raise j.exceptions.Value("A project with the same name already exists")

        project = ProjectManagement(
            token=self.parent.projects.parent_instance.token_,
            name=self.do_name,
            purpose=purpose,
            description=description,
            environment=environment,
            is_default=is_default,
        )
        project.create()

        if is_default:
            project.update(is_default=True)

        return project

    def delete_remote(self):
        """Delete an exisiting project.
        A project can't be deleted unless it has no resources.

        :param name: project name
        :type name: str
        :raises j.exceptions.Input: raises an error if there is no project with this name
        """
        project = self.parent.projects.get_project_exist_remote(self.do_name)
        project.delete()


class DropletFactory(StoredFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_remote(self, project_name=None):
        # List remote dorplet for a project if it is specified
        if project_name:
            project = self.parent_instance.projects.get_project_exist_remote(project_name)
            return project.list_droplets()

        return self.parent_instance.client.get_all_droplets()

    def check_droplet_exist_remote(self, name):
        for droplet in self.list_remote():
            if droplet.name.lower() == name.lower():
                return True
        return False

    def get_droplet_exist_remote(self, name):
        for droplet in self.list_remote():
            if droplet.name.lower() == name.lower():
                return droplet
        raise j.exceptions.Input("could not find project with name:%s on you Digital Ocean account" % name)

    def shutdown_all(self, project_name=None):
        for droplet in self.list_remote(project_name):
            droplet.shutdown()

    def delete_all(self, ignore=None, interactive=True, project_name=None):

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
        for droplet in self.list_remote(project_name):
            if test(ignore, droplet.name):
                todo.append(droplet)
        if todo != []:
            todotxt = ",".join([i.name for i in todo])
            if not interactive or j.tools.console.ask_yes_no("ok to delete:%s" % todotxt):
                for droplet in todo:
                    droplet.destroy()


class Droplet(Client):
    do_name = fields.String()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_digital_ocean_name(self, name):
        self.do_name = name

    def deploy(
        self,
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
            project = self.parent.projects.get_project_exist_remote(self.do_name)
            if not project:
                raise j.exceptions.Input("could not find project with name:%s" % project_name)

        # Get ssh
        if not sshkey:
            sshkey_do = self.parent.get_default_sshkey()

            if not sshkey_do:
                # means we did not find the sshkey on digital ocean yet, need to create
                # TODO need to make sure that that sshkey is loaded and valid
                sshkey = self.parent.sshkey
                key = digitalocean.SSHKey(
                    token=self.parent.projects.parent_instance.token_, name=sshkey.name, public_key=sshkey.public_key
                )
                key.create()
            sshkey_do = self.parent.get_default_sshkey()
            assert sshkey_do
            sshkey = sshkey_do.name

        if self.parent.droplets.check_droplet_exist_remote(self.do_name):
            dr0 = self.parent.droplets.get_droplet_exist_remote(self.do_name)
            if delete:
                dr0.destroy()
            else:
                sshcl = j.clients.sshclient.get(name="do_%s" % self.do_name, host=dr0.ip_address, sshkey=sshkey)
                return dr0, sshcl

        sshkey = self.parent.droplets.parent_instance.get_sshkey(sshkey)
        region = self.parent.droplets.parent_instance.get_region(region)
        imagedo = self.parent.droplets.parent_instance.get_image(image)

        img_slug_or_id = imagedo.slug if imagedo.slug else imagedo.id

        droplet = digitalocean.Droplet(
            token=self.parent.droplets.parent_instance.token_,
            name=self.do_name,
            region=region.slug,
            image=img_slug_or_id,
            size_slug=size_slug,
            ssh_keys=[sshkey],
            backups=False,
        )
        droplet.create()

        if project:
            project.assign_resources(["do:droplet:%s" % droplet.id])

    def delete_remote(self):
        droplet = self.parent.droplets.get_droplet_exist_remote(self.do_name)
        droplet.destroy()


class DigitalOcean(Client):
    name = fields.String()
    token_ = fields.String()
    projects = fields.Factory(Project, factory_type=ProjectFactory)
    droplets = fields.Factory(Droplet, factory_type=DropletFactory)

    def __init__(self):
        super().__init__()
        self._client = None

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

    # Images
    @property
    def digitalocean_images(self):
        return self.client.get_distro_images()

    @property
    def digitalocean_myimages(self):
        return self.client.get_images(private=True)

    @property
    def digitalocean_account_images(self):
        return self.digitalocean_images + self.digitalocean_myimages

    @property
    def digitalocean_sizes(self):
        return self.client.get_all_sizes()

    def get_image(self, name):
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

    def get_image_names(self, name=""):
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

    # Regions

    @property
    def digitalocean_regions(self):
        return self.client.get_all_regions()

    @property
    def digitalocean_region_names(self):
        return [i.slug for i in self.digitalocean_regions]

    def get_region(self, name):
        for item in self.digitalocean_regions:
            if name == item.slug:
                return item
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find region:%s" % name)

    # SSHkeys
    @property
    def sshkeys(self):
        return self.client.get_all_sshkeys()

    def get_default_sshkey(self):
        pubkeyonly = self.sshkey.public_key
        for item in self.sshkeys:
            if item.public_key.find(pubkeyonly) != -1:
                return item
        return None

    def det_default_sshkey(self, default_sshkey):
        self.sshkey = default_sshkey

    def get_sshkey(self, name):
        for item in self.sshkeys:
            if name == item.name:
                return item
        raise j.exceptions.Base("did not find key:%s" % name)

    def __str__(self):
        return "digital ocean client:%s" % self.name

    __repr__ = __str__
