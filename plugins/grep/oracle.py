'''
oracle.py

Copyright 2006 Andres Riancho

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
import core.data.kb.knowledge_base as kb

from core.controllers.plugins.grep_plugin import GrepPlugin
from core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from core.data.kb.info import Info


class oracle(GrepPlugin):
    '''
    Find Oracle applications.

    @author: Andres Riancho (andres.riancho@gmail.com)
    '''

    OAS_TAGS = ['<!-- Created by Oracle ',]

    def __init__(self):
        GrepPlugin.__init__(self)
        self._already_analyzed = ScalableBloomFilter()

    def grep(self, request, response):
        '''
        Plugin entry point. Grep for oracle applications.

        @param request: The HTTP request object.
        @param response: The HTTP response object
        @return: None
        '''
        url = response.get_url()
        if response.is_text_or_html() and url not in self._already_analyzed:
            self._already_analyzed.add(url)

            for msg in self.OAS_TAGS:
                if msg in response:
                    desc = 'The URL: "%s" was created using Oracle Application'\
                           ' Server.'
                    desc = desc % response.get_url()
                    i = Info('Oracle application server', desc, response.id,
                             self.get_name())
                    i.set_url(url)
                    i.add_to_highlight(msg)
                    
                    self.kb_append(self, 'oracle', i)

    def get_long_desc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin greps every page for oracle messages, versions, etc.
        '''
