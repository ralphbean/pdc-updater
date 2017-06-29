from pdcupdater.tests.handler_tests import BaseHandlerTest, mock_pdc
import pdcupdater.services


class TestRetiredComponents(BaseHandlerTest):
    handler_path = 'pdcupdater.handlers.retirement:RetireComponentHandler'

    def test_can_handle_retire_msg(self):
        idx = '2017-b1adac6d-64e9-406f-a1f4-4d3e57105649'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertTrue(result)

    def test_cannot_handle_unretire_msg(self):
        idx = '2017-d20c1ee0-9c00-4ab8-9364-0fdf120e822c'
        msg = pdcupdater.utils.get_fedmsg(idx)
        result = self.handler.can_handle(None, msg)
        self.assertFalse(result)

    @mock_pdc
    def test_can_process_retire_msg(self, pdc):
        pdc.add_endpoint('component-branches', 'GET', [
            {
                "id": 89151,
                "global_component": "iwhd",
                "name": "f26",
                "slas": [
                    {
                        "id": 178020,
                        "sla": "bug_fixes",
                        "eol": "2222-07-01"
                    },
                    {
                        "id": 178028,
                        "sla": "security_fixes",
                        "eol": "2222-07-01"
                    }
                ],
                "type": "rpm",
                "active": True,
                "critical_path": False
            }
        ])
        pdc.add_endpoint('component-branch-slas', 'GET', [
            {
                "id": 178020,
                "sla": "bug_fixes",
                "branch": {
                    "id": 89151,
                    "name": "f26",
                    "global_component": "iwhd",
                    "type": "rpm",
                    "critical_path": False,
                    "active": True
                },
                "eol": "2222-07-01"
            },
            {
                "id": 178028,
                "sla": "security_fixes",
                "branch": {
                    "id": 89151,
                    "name": "f26",
                    "global_component": "iwhd",
                    "type": "rpm",
                    "critical_path": False,
                    "active": True
                },
                "eol": "2222-07-01"
            }
        ])
        pdc.add_endpoint('component-branch-slas/178020', 'PATCH', 'ok')
        pdc.add_endpoint('component-branch-slas/178028', 'PATCH', 'ok')

        idx = '2017-b1adac6d-64e9-406f-a1f4-4d3e57105649'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        expected_keys = [
            'component-branches',
            'component-branch-slas/178020',
            'component-branch-slas/178028'
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)

    @mock_pdc
    def test_can_process_retire_msg_already_retired(self, pdc):
        pdc.add_endpoint('component-branches', 'GET', [
            {
                "id": 155867,
                "global_component": "obexftp",
                "name": "f26",
                "slas": [
                    {
                        "id": 310591,
                        "sla": "bug_fixes",
                        "eol": "2017-06-28"
                    },
                    {
                        "id": 310602,
                        "sla": "security_fixes",
                        "eol": "2017-06-28"
                    }
                ],
                "type": "rpm",
                "active": False,
                "critical_path": False
            }
        ])

        idx = '2017-3f490f4d-7612-4881-80cb-e1a941d6d700'
        msg = pdcupdater.utils.get_fedmsg(idx)
        self.handler.handle(pdc, msg)
        expected_keys = [
            'component-branches'
        ]
        self.assertEquals(pdc.calls.keys(), expected_keys)
