from netbox.plugins import PluginConfig

class Change2LogConfig(PluginConfig):
    name = 'netbox_change2log'
    verbose_name = 'NetBox Change2Log'
    description = 'Sends the changelog to a logger'
    version = '0.1.0'
    author = 'TMT GmbH & Co. KG'
    min_version = '4.0.0'

    default_settings = {
        'consolidate_multiple_changes': False,
        'output_format': 'text',
    }
    
    def ready(self):
        from . import signals

config = Change2LogConfig