'''
credit_cards.py

Copyright 2008 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import re

import core.data.kb.knowledge_base as kb
import core.data.constants.severity as severity

from core.controllers.plugins.grep_plugin import GrepPlugin
from core.data.kb.vuln import Vuln


def luhnCheck(value):
    '''
    The Luhn check against the value which can be an array of digits,
    numeric string or a positive integer.

    @author Alexander Berezhnoy (alexander.berezhnoy |at| gmail.com)
    '''
    # Prepare the value to be analyzed.
    arr = []
    for c in value:
        if c.isdigit():
            arr.append(int(c))
    arr.reverse()

    # Analyze
    for idx in [i for i in range(len(arr)) if i % 2]:
        d = arr[idx] * 2
        if d > 9:
            d = d / 10 + d % 10
        arr[idx] = d

    sm = sum(arr)
    return not (sm % 10)


class credit_cards(GrepPlugin):
    '''
    This plugin detects the occurrence of credit card numbers in web pages.

    @author Alexander Berezhnoy (alexander.berezhnoy |at| gmail.com)
    '''

    def __init__(self):
        GrepPlugin.__init__(self)

        cc_regex = '((^|\s)\d{4}[- ]?(\d{4}[- ]?\d{4}|\d{6})[- ]?(\d{5}|\d{4})($|\s))'
        #    (^|[^\d])                        Match the start of the string, or something that's NOT a digit
        #    \d{4}[- ]?                       Match four digits, and then (optionally) a "-" or a space
        #    (\d{4}[- ]?\d{4}|\d{6})          Match one of the following:
        #            - Four digits, and then (optionally) a "-" or a space and then four digits again (VISA cards)
        #            - Six digits (AMEX cards)
        #    [- ]?                            Match a "-" or a space (optionally)
        #    (\d{5}|\d{4})                    Match the final digits, five or four digits
        #    ($|[^\d])                        Match the end of the string, or something that's NOT a digit

        self._cc_regex = re.compile(cc_regex, re.M)

    def grep(self, request, response):
        '''
        Plugin entry point, search for the credit cards.
        @param request: The HTTP request object.
        @param response: The HTTP response object
        @return: None
        '''
        if response.is_text_or_html() and response.get_code() == 200 \
                and response.get_clear_text_body() is not None:

            found_cards = self._find_card(response.get_clear_text_body())

            for card in found_cards:
                desc = 'The URL: "%s" discloses the credit card number: "%s"'
                desc = desc % (response.get_url(), card)
                
                v = Vuln('Credit card number disclosure', desc,
                         severity.LOW, response.id, self.get_name())

                v.set_url(response.get_url())
                v.add_to_highlight(card)
                
                self.kb_append_uniq(self, 'credit_cards', v, 'URL')

    def _find_card(self, body):
        '''
        @return: A list of matching credit card numbers
        '''
        res = []

        match_list = self._cc_regex.findall(body)

        for match_set in match_list:
            possible_cc = match_set[0]
            if luhnCheck(possible_cc):
                res.append(possible_cc)

        return res

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugins scans every response page to find the strings that are
        likely to be credit card numbers. It can be tested against the following
        URL:
            - https://www.paypal.com/en_US/vhelp/paypalmanager_help/credit_card_numbers.htm
        '''
