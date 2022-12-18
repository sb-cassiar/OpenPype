import os
import copy

from maya import cmds
import pymel.core as pc
import xgenm

from openpype.pipeline import publish
from openpype.hosts.maya.api.lib import maintained_selection, attribute_values
from openpype.lib import StringTemplate


class ExtractXgenCache(publish.Extractor):
    """Extract Xgen"""

    label = "Extract Xgen"
    hosts = ["maya"]
    families = ["xgen"]
    scene_type = "ma"

    def process(self, instance):
        if "representations" not in instance.data:
            instance.data["representations"] = []

        staging_dir = self.staging_dir(instance)
        maya_filename = "{}.{}".format(instance.data["name"], self.scene_type)
        maya_filepath = os.path.join(staging_dir, maya_filename)

        # Get published xgen file name.
        template_data = copy.deepcopy(instance.data["anatomyData"])
        template_data.update({"ext": "xgen"})
        templates = instance.context.data["anatomy"].templates["publish"]
        xgen_filename = StringTemplate(templates["file"]).format(template_data)
        name = instance.data["xgenPalette"].replace(":", "__").replace("|", "")
        value = xgen_filename.replace(".xgen", "__" + name + ".xgen")
        attribute_data = {
            "{}.xgFileName".format(instance.data["xgenPalette"]): xgen_filename
        }

        # Export xgen palette files.
        xgen_path = os.path.join(staging_dir, value).replace("\\", "/")
        xgenm.exportPalette(
            instance.data["xgenPalette"].replace("|", ""), xgen_path
        )
        self.log.info("Extracted to {}".format(xgen_path))

        representation = {
            "name": name,
            "ext": "xgen",
            "files": value,
            "stagingDir": staging_dir,
        }
        instance.data["representations"].append(representation)

        # Collect nodes to export.
        duplicate_nodes = []
        for node, connections in instance.data["xgenConnections"].items():
            transform_name = connections["transform"].split(".")[0]

            # Duplicate_transform subd patch geometry.
            duplicate_transform = pc.duplicate(transform_name)[0]
            pc.parent(duplicate_transform, world=True)
            duplicate_transform.name(stripNamespace=True)
            duplicate_shape = pc.listRelatives(
                duplicate_transform, shapes=True
            )[0]

            pc.connectAttr(
                "{}.matrix".format(duplicate_transform),
                "{}.transform".format(node),
                force=True
            )
            pc.connectAttr(
                "{}.worldMesh".format(duplicate_shape),
                "{}.geometry".format(node),
                force=True
            )

            duplicate_nodes.append(duplicate_transform)

        # Import xgen onto the duplicate.
        with maintained_selection():
            cmds.select(duplicate_nodes)
            collection = xgenm.importPalette(xgen_path, [])

        # Export Maya file.
        type = "mayaAscii" if self.scene_type == "ma" else "mayaBinary"
        with attribute_values(attribute_data):
            with maintained_selection():
                cmds.select(duplicate_nodes + [collection])
                cmds.file(
                    maya_filepath,
                    force=True,
                    type=type,
                    exportSelected=True,
                    preserveReferences=True,
                    constructionHistory=True,
                    shader=True,
                    constraints=True,
                    expressions=True
                )

        self.log.info("Extracted to {}".format(maya_filepath))

        representation = {
            "name": self.scene_type,
            "ext": self.scene_type,
            "files": maya_filename,
            "stagingDir": staging_dir,
            "data": {"xgenName": collection}
        }
        instance.data["representations"].append(representation)

        # Revert to original xgen connections.
        for node, connections in instance.data["xgenConnections"].items():
            for attr, src in connections.items():
                cmds.connectAttr(
                    src, "{}.{}".format(node, attr), force=True
                )

        cmds.delete(duplicate_nodes + [collection])

        # Setup transfers.
        #needs to reduce resources to only what is used for the collections in
        #the objectset
        xgen_dir = os.path.join(
            os.path.dirname(instance.context.data["currentFile"]), "xgen"
        )
        transfers = []
        for root, dirs, files in os.walk(xgen_dir):
            for file in files:
                source = os.path.join(root, file)
                destination = source.replace(
                    xgen_dir, instance.data["resourcesDir"]
                )
                transfers.append((source, destination))

        instance.data["transfers"] = transfers
