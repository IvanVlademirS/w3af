'''
symfony.py

Copyright 2011 Andres Riancho and Carlos Pantelides

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

from core.data.kb.info import Info
from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList
from core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from core.controllers.plugins.grep_plugin import GrepPlugin


class symfony(GrepPlugin):
    '''
    Grep every page for traces of the Symfony framework.

    @author: Carlos Pantelides (carlos.pantelides@yahoo.com ) based upon
    work by Andres Riancho (andres.riancho@gmail.com) and help from
    Pablo Mouzo (pablomouzo@gmail.com)
    '''

    def __init__(self):
        GrepPlugin.__init__(self)

        # Internal variables
        self._already_inspected = ScalableBloomFilter()
        self._override = False

    def grep(self, request, response):
        '''
        Plugin entry point.

        @param request: The HTTP request object.
        @param response: The HTTP response object
        @return: None, all results are saved in the kb.
        '''
        url = response.get_url()
        if response.is_text_or_html() and url not in self._already_inspected:

            # Don't repeat URLs
            self._already_inspected.add(url)

            if self.symfony_detected(response):
                dom = response.get_dom()
                if dom is not None and not self.csrf_detected(dom):
                    desc = 'The URL: "%s" seems to be generated by the'\
                           ' Symfony framework and contains a form that'\
                           ' perhaps has CSRF protection disabled.'
                    desc = desc % url
                    i = Info('Symfony Framework with CSRF protection disabled',
                             desc, response.id, self.get_name())
                    i.set_url(url)
                    self.kb_append_uniq(self, 'symfony', i, 'URL')

    def symfony_detected(self, response):
        if self._override:
            return True
        for header_name in response.get_headers().keys():
            if header_name.lower() == 'set-cookie' or header_name.lower() == 'cookie':
                if re.match('^symfony=', response.get_headers()[header_name]):
                    return True
        return False

    def csrf_detected(self, dom):
        forms = dom.xpath('//form')
        if forms:
            csrf_protection_regex_string = '.*csrf_token'
            csrf_protection_regex_re = re.compile(
                csrf_protection_regex_string, re.IGNORECASE)
            for form in forms:
                inputs = form.xpath('//input[@id]')
                if inputs:
                    for _input in inputs:
                        if csrf_protection_regex_re.search(_input.attrib["id"]):
                            return True
        return False

    def set_options(self, options_list):
        self._override = options_list['override'].get_value()

    def get_options(self):
        '''
        @return: A list of option objects for this plugin.
        '''
        ol = OptionList()

        d = 'Skip symfony detection and search for the csrf (mis)protection.'
        o = opt_factory('override', self._override, d, 'boolean')
        ol.add(o)

        return ol

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin greps every page for traces of the Symfony framework and the
        lack of CSRF protection.
        '''
