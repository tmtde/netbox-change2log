# NetBox Change2Log
The goal of this plugin is to be able to log changes from NetBox's change log to another place (or multiple places).
Since logging needs can be very custom, the plugin provides a named logger the user can configure to their specific needs.

## Compatibililty
| NetBox Version | Plugin Version |
|----------------|----------------|
| 4.0+*          | 0.1            |

*) The `message` field for change log comments [added with NetBox 4.4.0](https://github.com/netbox-community/netbox/pull/20226) is included for installations using 4.4.0+ and omitted in prior versions.

Note: Due to the low amount of changes to the changelog codebase, the plugin may work with way older versions of NetBox, but aren't explicitly tested. If needed, make changes to the `min_version` accordingly.

## Installation
Build package and install:
```bash
cd /path/to/repo/
python3 -m build
pip install ./dist/netbox_change2log-<ver>.tar.gz
```
Or install via git:
```bash
pip install git+https://github.com/tmtde/netbox-change2log.git
```

## Configuration
Configuration is split into two places, one for the plugins configuration and one for the logger itself.

### Plugin
To your `configuration.py` (or `plugins.py` for Docker installations) add the following:

```python
PLUGINS.append('netbox_change2log')
PLUGINS_CONFIG['netbox_change2log'] = {}
```

For the `PLUGIN_CONFIG` the following settings can be changed
- `consolidate_multiple_changes` (Boolean, default `False`): If false, each changed attribute is output as a separate log line, otherwise all changes will appear in the same line.
- `output_format`: Possible values:
	- `text` (default): Outputs a log format `{change_user} {<changed>/<created>/<deleted>} {object_name}. Change: {oldvalue} -> {newvalue} [Request: {request_id}]`
	- `json`: Outputs the change as a json blob


### Logger
Logger configuration is handled in the `configuration.py` configuration file from NetBox (or `logging.py` for a Docker installation).
Add the logger `netbox_change2log` from this plugin to the `LOGGING` variable and configure to your needs.

On how to configure loggers, please see the [Python Documentation on logging](https://docs.python.org/3/library/logging.html) and the [Django Logging Documentation](https://docs.djangoproject.com/en/5.2/topics/logging/) for Django specifics. The plugins logger outputs to the `INFO` level.

An example configuration to log to a file:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'change2log': {
             'formatter': 'simple',
             'class': 'logging.FileHandler',
             'filename': '/var/log/netbox_objectchange.log',
         }
    },
    'loggers': {
        'netbox_change2log': {
            'level': 'INFO',
            'handlers': ['change2log'],
        }
    }
}
```