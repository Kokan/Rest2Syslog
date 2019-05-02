from syslogng import LogSource
import time
from r2s_paginator import Paginator
from r2s_parser import Parser
from r2s_state import State
from r2s_utils import _print

class REST2SyslogSource(LogSource):
    
    def init(self, options): # optional
        _print("REST2Syslog Source init")
        try:
            self.interval = int(options['interval'])
            self.paginator = Paginator(options)
            self.parser = Parser(options)
            self.exit = False
            self.state = State()
            return True
        except:
            _print('configuration of REST2Syslog Source (R2S) is incomplete or malformed. Please reffer to the R2S Wiki for more details.')
            return False

    def request_exit(self): # mandatory
        _print("R2S Source exit")
        self.exit = True

    def run(self): # mandatory
        while not self.exit:
            try:
                time.sleep(5)
                self.fetchPages()
            except Exception as e:
                _print('Error while trying to fetch alerts.')
                _print(e)

    def sendItems(self,items):
        for item in items:
            if item['id'] != self.state.last_record_id:
                msg = self.parser.buildMessage(item)
                self.post_message(msg)
                self.state.last_record_id = item['id']
            else:
                return True
        return False

    def fetchPages(self):
        while not self.exit:
            page_items = self.paginator.fetchPage()
            if page_items is not None and len(page_items) != 0:
                is_last_page = self.sendItems(page_items)
                if is_last_page: break    
                self.paginator.next()
            else:
                _print('No more pages to fetch')
                break
        self.state.persist()
        self.paginator.reset()
