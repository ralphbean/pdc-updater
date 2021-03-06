# -*- coding: utf-8 -*-
# This file is part of pdc-updater.
#
# pdc-updater is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# pdc-updater is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pdc-updater.  If not, see <http://www.gnu.org/licenses/>.
""" Fedmsg consumer that updates PDC.

Authors:    Ralph Bean <rbean@redhat.com>

"""

import fedmsg.consumers

import pdcupdater.handlers

import logging
log = logging.getLogger(__name__)


import pdc_client


class PDCUpdater(fedmsg.consumers.FedmsgConsumer):
    config_key = 'pdcupdater.enabled'

    def __init__(self, hub):
        config = hub.config

        # Ensure this is present, it should be a dict with a url and creds
        self.pdc_config = config['pdcupdater.pdc']

        # Load all our worker bits.
        self.handlers = list(pdcupdater.handlers.load_handlers(config))

        # Tell fedmsg to only notify us about topics that our handlers want.
        self.topic = [
            '.'.join([config['topic_prefix'], config['environment'], topic])
            for handler in self.handlers for topic in handler.topic_suffixes
        ]

        super(PDCUpdater, self).__init__(hub)

    def consume(self, msg):
        msg = msg['body']  # Remove envelope
        idx = msg.get('msg_id', None)
        topic = msg.get('topic', None)
        self.log.debug("Received %r, %r" % (idx, topic))

        pdc = pdc_client.PDCClient(**self.pdc_config)
        pdcupdater.utils.handle_message(pdc, self.handlers, msg)
