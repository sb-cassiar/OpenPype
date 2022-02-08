"""Addon definition is located here.

Import of python packages that may not be available should not be imported
in global space here until are required or used.
- Qt related imports
- imports of Python 3 packages
    - we still support Python 2 hosts where addon definition should available
"""
import os
import click

from avalon.api import AvalonMongoDB
import gazu
from openpype.lib import create_project
from openpype.lib.anatomy import Anatomy
from openpype.modules import JsonFilesSettingsDef, OpenPypeModule, ModulesManager

# Import interface defined by this addon to be able find other addons using it
from openpype_interfaces import IPluginPaths, ITrayAction


# Settings definition of this addon using `JsonFilesSettingsDef`
# - JsonFilesSettingsDef is prepared settings definition using json files
#   to define settings and store default values
class AddonSettingsDef(JsonFilesSettingsDef):
    # This will add prefixes to every schema and template from `schemas`
    #   subfolder.
    # - it is not required to fill the prefix but it is highly
    #   recommended as schemas and templates may have name clashes across
    #   multiple addons
    # - it is also recommended that prefix has addon name in it
    schema_prefix = "kitsu"

    def get_settings_root_path(self):
        """Implemented abstract class of JsonFilesSettingsDef.

        Return directory path where json files defying addon settings are
        located.
        """
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings")


class KitsuModule(OpenPypeModule, IPluginPaths, ITrayAction):
    """This Addon has defined it's settings and interface.

    This example has system settings with an enabled option. And use
    few other interfaces:
    - `IPluginPaths` to define custom plugin paths
    - `ITrayAction` to be shown in tray tool
    """

    label = "Kitsu"
    name = "kitsu"

    def initialize(self, settings):
        """Initialization of addon."""
        module_settings = settings[self.name]

        # Enabled by settings
        self.enabled = module_settings.get("enabled", False)

        # Add API URL schema
        kitsu_url = module_settings["server"].strip()
        if kitsu_url:
            # Ensure web url
            if not kitsu_url.startswith("http"):
                kitsu_url = "https://" + kitsu_url

            # Check for "/api" url validity
            if not kitsu_url.endswith("api"):
                kitsu_url = f"{kitsu_url}{'' if kitsu_url.endswith('/') else '/'}api"

        self.server_url = kitsu_url

        # Set credentials
        self.script_login = module_settings["script_login"]
        self.script_pwd = module_settings["script_pwd"]

        # Prepare variables that can be used or set afterwards
        self._connected_modules = None
        # UI which must not be created at this time
        self._dialog = None

    def tray_init(self):
        """Implementation of abstract method for `ITrayAction`.

        We're definitely  in tray tool so we can pre create dialog.
        """

        self._create_dialog()

    def get_global_environments(self):
        """Kitsu's global environments."""
        return {
            "KITSU_SERVER": self.server_url,
            "KITSU_LOGIN": self.script_login,
            "KITSU_PWD": self.script_pwd,
        }

    def _create_dialog(self):
        # Don't recreate dialog if already exists
        if self._dialog is not None:
            return

        from .widgets import MyExampleDialog

        self._dialog = MyExampleDialog()

    def show_dialog(self):
        """Show dialog with connected modules.

        This can be called from anywhere but can also crash in headless mode.
        There is no way to prevent addon to do invalid operations if he's
        not handling them.
        """
        # Make sure dialog is created
        self._create_dialog()
        # Show dialog
        self._dialog.open()

    def get_connected_modules(self):
        """Custom implementation of addon."""
        names = set()
        if self._connected_modules is not None:
            for module in self._connected_modules:
                names.add(module.name)
        return names

    def on_action_trigger(self):
        """Implementation of abstract method for `ITrayAction`."""
        self.show_dialog()

    def get_plugin_paths(self):
        """Implementation of abstract method for `IPluginPaths`."""
        current_dir = os.path.dirname(os.path.abspath(__file__))

        return {"publish": [os.path.join(current_dir, "plugins", "publish")]}

    def cli(self, click_group):
        click_group.add_command(cli_main)


@click.group(KitsuModule.name, help="Kitsu dynamic cli commands.")
def cli_main():
    pass


@cli_main.command()
def sync_local():
    """Synchronize local database from Zou sever database."""

    # Connect to server
    gazu.client.set_host(os.environ["KITSU_SERVER"])

    # Authenticate
    gazu.log_in(os.environ["KITSU_LOGIN"], os.environ["KITSU_PWD"])

    # Iterate projects
    dbcon = AvalonMongoDB()
    dbcon.install()
    all_projects = gazu.project.all_projects()
    for project in all_projects:
        # Create project locally
        # Try to find project document
        project_name = project["name"]
        project_code = project_name
        dbcon.Session["AVALON_PROJECT"] = project_name
        project_doc = dbcon.find_one({"type": "project"})

        # Get all assets from zou
        all_assets = gazu.asset.all_assets_for_project(project)

        # Query all assets of the local project
        project_col = dbcon.database[project_code]
        asset_docs_zou_ids = {
            asset_doc["data"]["zou_id"]
            for asset_doc in project_col.find({"type": "asset"})
        }

        # Create project if is not available
        # - creation is required to be able set project anatomy and attributes
        if not project_doc:
            print(f"Creating project '{project_name}'")
            project_doc = create_project(project_name, project_code, dbcon=dbcon)

        # Create project item
        insert_list = []

        bulk_writes = []
        for asset in all_assets:
            asset_data = {"zou_id": asset["id"]}

            # Set tasks
            asset_tasks = gazu.task.all_tasks_for_asset(asset)
            asset_data["tasks"] = {
                t["task_type_name"]: {"type": t["task_type_name"]} for t in asset_tasks
            }

            # Create Asset
            asset_doc = {
                "name": asset["name"],
                "type": "asset",
                "schema": "openpype:asset-3.0",
                "data": asset_data,
                "parent": project_doc["_id"],
            }

            if asset["id"] not in asset_docs_zou_ids:  # Item is new
                insert_list.append(asset_doc)
            else:
                asset_doc = project_col.find_one({"data": {"zou_id": asset["id"]}})

                # TODO update
            # for task in asset_tasks:
            #     # print(task)
            #     task_data = {"zou_id": task["id"]}

            #     # Create Task
            #     task_doc = {
            #         "name": task["name"],
            #         "type": "task",
            #         "schema": "openpype:asset-3.0",
            #         "data": task_data,
            #         "parent": asset_doc["_id"],
            #     }
            #     insert_list.append(task_doc)

            # elif item.data(REMOVED_ROLE): # TODO removal
            #     if item.data(HIERARCHY_CHANGE_ABLE_ROLE):
            #         bulk_writes.append(DeleteOne(
            #             {"_id": item.asset_id}
            #         ))
            #     else:
            #         bulk_writes.append(UpdateOne(
            #             {"_id": item.asset_id},
            #             {"$set": {"type": "archived_asset"}}
            #         ))

            # else: TODO update data
            #     update_data = new_item.update_data()
            #     if update_data:
            #         bulk_writes.append(UpdateOne(
            #             {"_id": new_item.asset_id},
            #             update_data
            #         ))

        # Insert new docs if created
        if insert_list:
            project_col.insert_many(insert_list)

        # Write into DB TODO
        # if bulk_writes:
        #     project_col.bulk_write(bulk_writes)

    dbcon.uninstall()


@cli_main.command()
def show_dialog():
    """Show ExampleAddon dialog.

    We don't have access to addon directly through cli so we have to create
    it again.
    """
    from openpype.tools.utils.lib import qt_app_context

    manager = ModulesManager()
    example_addon = manager.modules_by_name[KitsuModule.name]
    with qt_app_context():
        example_addon.show_dialog()
