from core.models.change_logging import ObjectChange
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from netbox.plugins import get_plugin_config
from packaging import version
import json
import logging

logger = logging.getLogger('netbox_change2log')

# Starting with NetBox v4.4, the ObjectChange object has a `message` field, where a user can specify a comment on the change.
netbox_supports_change_comment = version.parse(settings.VERSION.split('-')[0]) >= version.parse("4.4.0")

@receiver(post_save, sender=ObjectChange)
def handle_objectchange_save(sender, instance, **kwargs):
    change_user = instance.user_name
    object_name = instance.object_repr
    request_id  = instance.request_id
    diff        = instance.diff()

    # The diff() object contains a nice list of pre and post values of changes attributes.
    changes = []
    for attribute in diff['pre']:
        # Remove linebreaks, so log messages won't break.
        changes.append(f'{attribute}: "{str(diff['pre'][attribute]).replace('\r\n', '\\n')}" -> "{str(diff['post'][attribute]).replace('\r\n', '\\n')}"')
        
    output_format = get_plugin_config('netbox_change2log', 'output_format')
    if output_format == 'json':
        if get_plugin_config('netbox_change2log', 'consolidate_multiple_changes'):
            change_obj = {
                'change_user': change_user,
                'object_name': object_name,
                'request_id': str(request_id),
                'changes': {
                    'pre': { attr: str(val).replace('\r\n', '\\n') for attr, val in diff['pre'].items() },
                    'post': { attr: str(val).replace('\r\n', '\\n') for attr, val in diff['post'].items() }
                }
            }
            if netbox_supports_change_comment:
                change_obj['comment'] = instance.message
        else:
            for attribute in diff['pre']:
                change_obj = {
                    'change_user': change_user,
                    'object_name': object_name,
                    'request_id': str(request_id),
                    'changes': {
                        'pre': { attribute: str(diff['pre'][attribute]).replace('\r\n', '\\n') },
                        'post': { attribute: str(diff['post'][attribute]).replace('\r\n', '\\n') }
                    }
                }
                if netbox_supports_change_comment:
                    change_obj['comment'] = instance.message

        logger.info(json.dumps(change_obj))
    else: # 'text' or any invalid
        comment = ''
        if netbox_supports_change_comment:
            comment = f'. Comment: "{instance.message}"'

        if get_plugin_config('netbox_change2log', 'consolidate_multiple_changes'):
            logger.info(f'{change_user} {instance.get_action_display().lower()} {object_name}. Change: {", ".join(changes)}{comment} [Request: {request_id}]')
        else:
            for change in changes:
                logger.info(f'{change_user} {instance.get_action_display().lower()} {object_name}. Change: {change}{comment} [Request: {request_id}]')