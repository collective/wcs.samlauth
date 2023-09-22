from plone import api
from wcs.samlauth.plugin import SamlAuthPlugin
import logging
import io


LOGGER = logging.getLogger(__name__)
PLUGIN_ID = 'saml'


def install_plugin():
    """Post install script"""
    # Setup our request oidc plugin.
    pas = api.portal.get_tool('acl_users')

    # Create plugin if it does not exist.
    if PLUGIN_ID not in pas.objectIds():
        plugin = SamlAuthPlugin(
            title="SAML",
        )
        plugin.id = PLUGIN_ID
        pas._setObject(PLUGIN_ID, plugin)
        LOGGER.info("Created %s in acl_users.", PLUGIN_ID)
    plugin = getattr(pas, PLUGIN_ID)

    # Activate all supported interfaces for this plugin.
    activate = []
    plugins = pas.plugins
    for info in plugins.listPluginTypeInfo():
        interface = info["interface"]
        interface_name = info["id"]
        if plugin.testImplements(interface):
            activate.append(interface_name)
            LOGGER.info(
                "Activating interface %s for plugin %s", interface_name, PLUGIN_ID
            )

    plugin.manage_activateInterfaces(activate)
    LOGGER.info("Plugins activated.")

    # Order some plugins to make sure our plugin is at the top.
    # This is not needed for all plugin interfaces.
    for info in plugins.listPluginTypeInfo():
        interface_name = info["id"]
        # If we support IPropertiesPlugin, it should be added here.
        if interface_name in ("IChallengePlugin",):
            iface = plugins._getInterfaceFromName(interface_name)
            plugins.movePluginsTop(iface, [PLUGIN_ID])
            LOGGER.info("Moved %s to top of %s.", PLUGIN_ID, interface_name)

    return plugin


def clean_for_json(data):

    cleaned_json = ''
    file_ = io.StringIO()
    file_.write(data)
    file_.seek(0)
    for line_raw in file_.readlines():
        line = line_raw.strip()
        if line.startswith('//'):
            continue
        elif line.startswith('/*'):
            continue
        elif line.startswith('*'):
            continue
        else:
            cleaned_json += line
    return cleaned_json