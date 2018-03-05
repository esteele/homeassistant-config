import datetime
import json
import appdaemon.appapi as appapi


class Locks(appapi.AppDaemon):

    def initialize(self):
        # self.log('getting codes')
        # for slot in range(1,31):
        #     for node_id in [17, 18]:
        #         code = self.call_service('lock/get_usercode', node_id=node_id, code_slot=slot)
        #         self.log("%s %s %s"% (node_id, slot, code))

        # Reset lock codes every morning at 4am
        self.run_daily(self.update_lock_codes, datetime.time(4, 0, 0))


    def update_lock_codes(self, *args):
        self.log("Updating lock coded")
        with open('/share/lock_codes.json', 'r') as f:
            content = f.read()
            self.log(content)
            entries = json.loads(content)
            for slot in range(1,31):
                if str(slot) in entries:
                    name, code = entries[str(slot)]
                    self.set_lock_code(slot, code)
                else:
                    self.clear_lock_code(slot)


    def set_lock_code(self, slot, code):
        for node_id in [17, 18]:
            self('Setting lock code for node %s on slot %s' % (node_id, slot))
 
            self.call_service('lock/set_usercode', node_id=node_id, code_slot=slot, usercode=code)

    def clear_lock_code(self, slot):
        for node_id in [17, 18]:
            self('Clearing lock code for node %s on slot %s' % (node_id, slot))
            self.call_service('lock/clear_usercode', node_id=node_id, code_slot=slot)
