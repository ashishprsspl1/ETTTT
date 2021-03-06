# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.integrations.campfire import CampfireIntegration
from webhelpers2.text import truncate

log = logging.getLogger(__name__)


class CampfireAlertChannel(AlertChannel):
    __mapper_args__ = {
        'polymorphic_identity': 'campfire'
    }

    @property
    def client(self):
        client = CampfireIntegration.create_client(
            self.integration.config['api_token'],
            self.integration.config['account'])
        return client

    def notify_reports(self, **kwargs):
        """
        Notify user of individual reports

        kwargs:
            application: application that the event applies for,
            user: user that should be notified
            request: request object
            since_when: reports are newer than this time value,
            reports: list of reports to render

        """
        template_vars = self.report_alert_notification_vars(kwargs)

        app_url = kwargs['request'].registry.settings['_mail_url']
        destination_url = kwargs['request'].route_url('/',
                                                      app_url=app_url)
        f_args = ('report',
                  template_vars['resource'].resource_id,
                  template_vars['url_start_date'].strftime('%Y-%m-%dT%H:%M'),
                  template_vars['url_end_date'].strftime('%Y-%m-%dT%H:%M'))
        destination_url += 'ui/{}?resource={}&start_date={}&end_date={}'.format(
            *f_args)

        if template_vars['confirmed_total'] > 1:
            template_vars["title"] = "%s - %s reports" % (
                template_vars['resource_name'],
                template_vars['confirmed_total'],
            )
        else:
            error_title = truncate(template_vars['reports'][0][1].error or
                                   'slow report', 90)
            template_vars["title"] = "%s - '%s' report" % (
                template_vars['resource_name'],
                error_title)

        template_vars["title"] += ' ' + destination_url

        log_msg = 'NOTIFY  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)

        for room in self.integration.config['rooms'].split(','):
            self.client.speak_to_room(room.strip(), template_vars["title"])

    def notify_report_alert(self, **kwargs):
        """
        Build and send report alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.report_alert_notification_vars(kwargs)

        if kwargs['event'].unified_alert_action() == 'OPEN':
            title = 'ALERT %s: %s - %s %s %s' % (
                template_vars['alert_action'],
                template_vars['resource_name'],
                kwargs['event'].values['reports'],
                template_vars['report_type'],
                template_vars['destination_url']
            )

        else:
            title = 'ALERT %s: %s type: %s' % (
                template_vars['alert_action'],
                template_vars['resource_name'],
                template_vars['alert_type'].replace('_', ' '),
            )
        for room in self.integration.config['rooms'].split(','):
            self.client.speak_to_room(room.strip(), title, sound='VUVUZELA')

    def notify_uptime_alert(self, **kwargs):
        """
        Build and send uptime alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.uptime_alert_notification_vars(kwargs)

        message = 'ALERT %s: %s has uptime issues %s\n\n' % (
            template_vars['alert_action'],
            template_vars['resource_name'],
            template_vars['destination_url']
        )
        message += template_vars['reason']

        for room in self.integration.config['rooms'].split(','):
            self.client.speak_to_room(room.strip(), message, sound='VUVUZELA')

    def send_digest(self, **kwargs):
        """
        Build and send daily digest notification

        kwargs:
            application: application that the event applies for,
            user: user that should be notified
            request: request object
            since_when: reports are newer than this time value,
            reports: list of reports to render

        """
        template_vars = self.report_alert_notification_vars(kwargs)
        f_args = (template_vars['resource_name'],
                  template_vars['confirmed_total'],)
        message = "Daily report digest: %s - %s reports" % f_args
        message += '{}\n'.format(template_vars['destination_url'])
        for room in self.integration.config['rooms'].split(','):
            self.client.speak_to_room(room.strip(), message)

        log_msg = 'DIGEST  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)

    def notify_chart_alert(self, **kwargs):
        """
        Build and send chart alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.chart_alert_notification_vars(kwargs)
        message = 'ALERT {}: value in "{}" chart: ' \
                  'met alert "{}" criteria {} \n'.format(
            template_vars['alert_action'],
            template_vars['chart_name'],
            template_vars['action_name'],
            template_vars['destination_url']
        )

        for item in template_vars['readable_values']:
            message += '{}: {}\n'.format(item['label'], item['value'])

        for room in self.integration.config['rooms'].split(','):
            self.client.speak_to_room(room.strip(), message, sound='VUVUZELA')
