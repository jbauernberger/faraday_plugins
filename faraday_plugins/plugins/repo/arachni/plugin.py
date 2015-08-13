#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information
'''

from __future__ import with_statement
from plugins import core
from model import api
import socket
import re
import os
import pprint
import sys

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

"""Arachni plugin XML Parser.

Description.

"""

current_path = os.path.abspath(os.getcwd())

__author__     = "Matías Ariel Ré Medina"
__copyright__  = "Copyright 2011, Faraday Project"
__credits__    = ["Matías Ariel Ré Medina"]
__license__    = ""
__version__    = "1.0.0"
__maintainer__ = "Matías Ariel Ré Medina"
__email__      = "mre@infobytesec.com"
__status__     = "Development"

class ArachniXmlParser(object):
    """Plugin that parses Arachni's XML report files.
    
    :param arachni_xml_filepath: Xml report generated by Arachni.
    
    :class:`.ArachniXmlParser`
    """
    def __init__(self, xml_output):
        tree = self.parse_xml(xml_output)
        
        if tree:
            self.issues = self.getIssues(tree)
            self.system = self.getSystem(tree)
        else:
            self.issues = []
            self.system = []

    def parse_xml(self, xml_output):
        """Opens and parses an arachni xml report file.
        
        :param filepath:

        :rtype xml_tree: An xml tree instance. None if error.
        """
        try:
            tree = ET.fromstring(xml_output)
        except SyntaxError, err:
            print "SyntaxError: %s. %s" % (err, xml_output)
            return None

        return tree

    def getIssues(self, tree):
        """
        :param tree:
        """
        for issues in tree.findall('issues'):
            for self.issue_node in issues.findall('issue'):
                yield Issue(self.issue_node)

    def getSystem(self, tree):
        """
        :param tree:
        """
        for self.system_node in tree.findall('system'):
            yield System(self.system_node)
    
    def getPlugins(self, tree):
        """
        :param tree:
        """
        for self.plugin_node in tree.findall('plugins'):
            yield Plugins(self.plugin_node)
        


               
      
               

class Issue(object):
    def __init__(self, issue_node):
        """
        :param issue_node:
        """
        self.node = issue_node
        self.name = self.getDesc(issue_node, 'name')
        self.var = self.getDesc(issue_node, 'var')
        self.severity = self.getDesc(issue_node, 'severity')
        self.url = self.getDesc(issue_node, 'url').lower()
        self.element = self.getDesc(issue_node, 'element')
        self.cwe = self.getDesc(issue_node, 'cwe')
        self.method = self.getDesc(issue_node, 'method')
        self.tags = self.getTags(issue_node, 'tags', 'tag')
        self.variable = self.getDesc(issue_node, 'variable')
        self.remedy_guidance = self.getDesc(issue_node, 'remedy_guidance')
        self.description = self.getDesc(issue_node, 'description')
        self.manual_verification = self.getDesc(issue_node, 'manual_verification')
        self.references = self.getReferences(issue_node)
        self.variations = self.getVariations(issue_node)

    def getDesc(self, issue_node, tag):
        """
        :param issue_node:
        :param tag:
        :rtype text: Returns current issue description
        """
        desc = issue_node.findall(tag)
        if desc:
            return desc[0].text
        else:
            return 'None'

    def getTags(self, issue_node, main_tag, child_tag):
        """
        :param issue_node:
        :param main_tag:
        :param child_tag:
        :rtype string: Returns current issue tag description
        """
        for tags in issue_node.findall(main_tag):
            for tag in tags.findall(child_tag):
                tagDesc = tag.attrib['name']
                if tagDesc:
                    return tagDesc
                else:
                    return 'None'

    def getReferences(self, issue_node):
        """Returns current issue references on this format {'url': 'http://www.site.com', 'name': 'WebSite'}.
        
        :param issue_node: Issue instance.
        :param main_tag: Container's tag.
        :param child_tag: Child's tag.

        :rtype dict: Reference
        """
        for tags in issue_node.findall('references'):
            for tag in tags.findall('reference'):
                reference = tag.attrib
                if reference:
                    return reference
                else:
                    return "None"

    def getVariations(self, issue_node):
        """Returns variations in dict format.

        :param issue_node: Issue instance.

        :rtype dict: Variations, keys : {'url', 'headers' , 'html'}

        """
        requests = []
        responses = []
        html = []
        url = []
        headers = [requests, responses]
        for variations in issue_node.findall('variations'):
            for variation in variations.findall('variation'):
                for urltmp in variation.findall('url'):
                    url.append(urltmp.text.lower())
                for heads in variation.findall('headers'):
                    for request in heads.findall('request'):
                        for field in request.findall('field'):
                            requests.append(field.attrib)
                    for response in heads.findall('response'):
                        for field in response.findall('field'):
                            responses.append(field.attrib)
                for htmltmp in variation.findall('html'):
                     html.append(htmltmp.text)
                     
        finalVariation = {'url' : url, 'headers' : headers, 'html' : html}
        return
    
    
               
       
               

class System(object):
    def __init__(self, system_node):
        self.system_node = system_node
        self.version = self.getDesc('version')
        self.revision = self.getDesc('revision')
        self.star_ttime = self.getDesc( 'start_datetime')
        self.finish_time = self.getDesc('finish_datetime')
        self.delta_time = self.getDesc('delta_time')
        self.url = self.getDesc('url')
        self.user_agent = self.getDesc('user_agent')
        self.audited_elements = self.getChildDesc('audited_elements', 'element')
        self.modules = self.getChildDesc('modules', 'module')
        self.filters = self.getFilters()
        self.cookies = self.getChildDesc('cookies', 'cookie')

    def getDesc(self, tag):
        """
        :param tag:
        :rtype text: Returns current issue description
        """
        desc = self.system_node.findall(tag)
        if desc:
            return desc[0].text
        else:
            return 'None'
            
    def getChildDesc(self, father_tag, child_tag):
        """Returns modules in dict format.

        :param father_tag: Container's tag.
        :param child_tag: Child's tag.
        :rtype child: (string/dict)

        """
        for tags in self.system_node.findall(father_tag):
            for child in tags.findall(child_tag):
                if child.tag == 'cookie':
                    return child.attrib
                elif child.tag == 'element':
                    return child.text
                else:
                    return child.attrib['name']
                    
    def getFilters(self):
        """Returns filters in list format.

        :rtype filters:
            filters[i], i:
                    0 for exclude,
                    1 for include,
                    2 for redundant.

        """
        exclude = []
        include = []
        redundant = []
        for tags in self.system_node.findall('filters'):
            for child in tags:
                if child.tag == 'exclude':
                    for regexp in child:
                        exclude.append(regexp.text)
                elif child.tag == 'include':
                    for regexp in child:
                        include.append(regexp.text)
                else:
                    for regexp in child:
                        redundant.append(regexp.text)
        filters = [('exclude', exclude), ('include', include), ('redundant', redundant)]
        return filters


               
        
               

class Plugins():
    def __init__(self, plugin_node):
        self.plugin_node = plugin_node
        self.healthmap = self.getHealthmap(self.plugin_node)
        self.content_types = self.getContentTypes(self.plugin_node)
    pass
    
class ArachniPlugin(core.PluginBase):
    """
    Plugin that parses Arachni's XML report files.
    """
    def __init__(self):
        core.PluginBase.__init__(self)
        self.id              = "Arachni"
        self.name            = "Arachni XML Output Plugin"
        self.plugin_version         = "0.0.2"
        self.version   = "0.4.5.2"
        self.framework_version  = "1.0.0"
        self.options         = None
        self._current_output = None
        self.macaddress = None
        self.hostname = None
        self.address = None
        self.port = "80"

                                          
        self._command_regex  = re.compile(r'^(sudo arachni |arachni |\.\/arachni |ruby \.\/arachni |ruby arachni ).*?')
                                                   
        self._report_regex = re.compile(r"^.*(--report=xml\s*[^\s]+).*$")
        
        global current_path
        self._output_file_path = os.path.join(self.data_path, "arachni_report-%s.xml" % self._rid)
                                                                                                 
        self._completition = {
            "":"arachni [options] url",
            "-h":"Help",
            "--help":"Help",
            "-v":"Be verbose.",
            "--version":"Show version information and exit.",
            "--debug":"Show what is happening internally. (You should give it a shot sometime ;) )",
            "--only-positives":"Echo positive results *only*.",
            "--http-username":"&lt;string&gt;    Username for HTTP authentication.",
            "--http-password":"&lt;string&gt;    Password for HTTP authentication.",            
            "--http-req-limit":"--http-req-limit=&lt;integer&gt;  Concurrent HTTP requests limit. (Default: 20) (Be careful not to kill your server.) (*NOTE*: If your scan seems unresponsive try lowering the limit.)",
            "--http-timeout":"--http-timeout=&lt;integer&gt;    HTTP request timeout in milliseconds.",
            "--cookie-jar":"--cookie-jar=&lt;filepath&gt;     Netscape HTTP cookie file, use curl to create it.",
            "--cookie-string":"--cookie-string='&lt;name&gt;=&lt;value&gt;; &lt;name2&gt;=&lt;value2&gt;' Cookies, as a string, to be sent to the web application.",
            "--user-agent":"--user-agent=&lt;string&gt;       Specify user agent.",
            "--custom-header":"--custom-header='&lt;name&gt;=&lt;value&gt;' Specify custom headers to be included in the HTTP requests. (Can be used multiple times.)",
            "--authed-by":"--authed-by=&lt;string&gt;        Who authorized the scan, include name and e-mail address. (It'll make it easier on the sys-admins during log reviews.) (Will be appended to the user-agent string.)",
            "--login-check-url":"--login-check-url=&lt;url&gt;     A URL used to verify that the scanner is still logged in to the web application. (Requires 'login-check-pattern'.)",
            "--login-check-pattern":"--login-check-pattern=&lt;regexp&gt; A pattern used against the body of the 'login-check-url' to verify that the scanner is still logged in to the web application. (Requires 'login-check-url'.)",
            "--save-profile":"--save-profile=&lt;filepath&gt;   Save the current run profile/options to &lt;filepath&gt;.",
            "--load-profile":"--load-profile=&lt;filepath&gt;   Load a run profile from &lt;filepath&gt;. (Can be used multiple times.) (You can complement it with more options, except for:\n* --modules\n* --redundant)",
            "--show-profile":"Will output the running profile as CLI arguments.",
            "-e":"-e &lt;regexp&gt; Exclude urls matching &lt;regexp&gt;. (Can be used multiple times.)",
            "--exclude":"    --exclude=&lt;regexp&gt          Exclude urls matching &lt;regexp&gt;.",
            "--exclude-page":"    --exclude-page=&lt;regexp&gt     Exclude pages whose content matches &lt;regexp&gt;.",
            "-i":"-i &lt;regexp&gt; Include *only* urls matching &lt;regex&gt;. (Can be used multiple times.)",
            "--include":"&lt;regexp&gt;          Include *only* urls matching &lt;regex&gt;.",
            "--redundant":"--redundant=&lt;regexp&gt;:&lt;limit&gt; Limit crawl on redundant pages like galleries or catalogs. (URLs matching &lt;regexp&gt; will be crawled &lt;limit&gt; amount of times.) (Can be used multiple times.)",
            "--auto-redundant":"--auto-redundant=&lt;limit&gt;    Only follow &lt;limit&gt; amount of URLs with identical query parameter names. (Default: inf) (Will default to 10 if no value has been specified.)",
            "-f":"Follow links to subdomains. (Default: off)",
            "--depth":"--depth=&lt;integer&gt; Directory depth limit. (Default: inf) (How deep Arachni should go into the site structure.)",
            "--follow-subdomains":"Follow links to subdomains.",
            "--link-count":"--link-count=&lt;integer&gt;      How many links to follow. (Default: inf)",
            "--redirect-limit":"--redirect-limit=&lt;integer&gt;  How many redirects to follow. (Default: 20)",
            "--extend-paths":"--extend-paths=&lt;filepath&gt;   Add the paths in &lt;file&gt; to the ones discovered by the crawler. (Can be used multiple times.)",
            "--restrict-paths":"--restrict-paths=&lt;filepath&gt; Use the paths in &lt;file&gt; instead of crawling. (Can be used multiple times.)",
            "--https-only":"Forces the system to only follow HTTPS URLs.",
            "-g":"Audit links.",
            "-p":"Audit forms.",
            "-c":"Audit cookies.",
            "--audit-cookies":"Audit cookies.",
            "--exclude-cookie":"--exclude-cookie=&lt;name&gt; Cookie to exclude from the audit by name. (Can be used multiple times.)",
            "--exclude-vector":"--exclude-vector=&lt;name&gt; Input vector (parameter) not to audit by name. (Can be used multiple times.)",
            "--audit-headers":"Audit HTTP headers. (*NOTE*: Header audits use brute force. Almost all valid HTTP request headers will be audited even if there's no indication that the web app uses them.) (*WARNING*: Enabling this option will result in increased requests, maybe by an order of magnitude.)",
            "--audit-cookies-extensively":"Submit all links and forms of the page along with the cookie permutations. (*WARNING*: This will severely increase the scan-time.)",
            "--fuzz-methods":"Audit links, forms and cookies using both GET and POST requests. (*WARNING*: This will severely increase the scan-time.)",
            "--exclude-binaries":"Exclude non text-based pages from the audit. (Binary content can confuse recon modules that perform pattern matching.)",
            "--lsmod":"--lsmod=&lt;regexp&gt; List available modules based on the provided regular expression. (If no regexp is provided all modules will be listed.) (Can be used multiple times.)",
            "-m":"-m &lt;modname,modname..&gt; Comma separated list of modules to load. (Modules are referenced by their filename without the '.rb' extension, use '--lsmod' to list all.\nUse '*' as a module name to deploy all modules or as a wildcard, like so:\nxss*   to load all xss modules\nsqli*  to load all sql injection modules etc.\nYou can exclude modules by prefixing their name with a minus sign:\n--modules=*,-backup_files,-xss\nThe above will load all modules except for the 'backup_files' and 'xss' modules.\nOr mix and match:\n-xss*   to unload all xss modules.)",
            "--lsrep":"--lsrep=&lt;regexp&gt; List available reports based on the provided regular expression. (If no regexp is provided all reports will be listed.) (Can be used multiple times.)",
            "--repload":"--repload=&lt;filepath&gt; Load audit results from an '.afr' report file. (Allows you to create new reports from finished scans.)",
            "--report":"--report='&lt;report&gt;:&lt;optname&gt;=&lt;val&gt;,&lt;optname2&gt;=&lt;val2&gt;,...'\n&lt;report&gt;: the name of the report as displayed by '--lsrep'\n(Reports are referenced by their filename without the '.rb' extension, use '--lsrep' to list all.)\n(Default: stdout) (Can be used multiple times.)",
            "--lsplug":"--lsplug=&lt;regexp&gt; List available plugins based on the provided regular expression.",
            "--plugin":"--plugin='&lt;plugin&gt;:&lt;optname&gt;=&lt;val&gt;,&lt;optname2&gt;=&lt;val2&gt;,...",
            '--lsplat':"List available platforms.",
            "--no-fingerprinting":"Disable platform fingerprinting.",
            "--proxy":"--proxy=&lt;server:port&gt; Proxy address to use.",
            "--proxy-auth":"--proxy-auth=&lt;user:passwd&gt;  Proxy authentication credentials.",
            "--proxy-type":"--proxy-type=&lt;type&gt; Proxy type; can be http, http_1_0, socks4, socks5, socks4a (Default: http)",
            }

    def parseOutputString(self, output, debug = False):
        """
        This method will discard the output the shell sends, it will read it from
        the xml where it expects it to be present.

        NOTE: if 'debug' is true then it is being run from a test case and the
        output being sent is valid.
        """
        parser = ArachniXmlParser(output)
        for system in parser.system:
            self.hostname = self.getHostname(system.url)
            self.address = self.getAddress(self.hostname)
            
            h_id = self.createAndAddHost(self.address)

                               
            i_id = self.createAndAddInterface(h_id, self.address, ipv4_address=self.address,hostname_resolution=self.hostname )
                        
            s_id = self.createAndAddServiceToInterface(h_id, i_id,
                                                self.protocol, 
                                                "tcp",
                                                ports=[self.port],
                                                status="open",
                                                version="",
                                                description="")

            n_id = self.createAndAddNoteToService(h_id,s_id,"website","")
            n2_id = self.createAndAddNoteToNote(h_id,s_id,n_id,self.hostname,"")

            
            for issue in parser.issues:
                
                desc=issue.description
                desc+="\nSolution: " + issue.remedy_guidance if issue.remedy_guidance !="None" else ""
                ref=[issue.references] if issue.references else []
                if issue.cwe != "None":
                    ref.append('CWE-'+issue.cwe)
                v_id = self.createAndAddVulnWebToService(h_id, s_id,
                                         website=self.hostname,    
                                         name=issue.name,
                                         desc=desc,    
                                         ref=ref,    
                                         pname=issue.var,
                                         severity=issue.severity,
                                         method=issue.method,
                                         path=issue.url)    
        
                    
                                         
        
        return True
    
    def processCommandString(self, username, current_path, command_string):
        """
        Adds the "--report=xml:outfile=" parameter to set an xml output for
        the command string that the user has set.
        If the user has already set a xml report his report will be replaced with faraday's one.
        """
    
        arg_match = self._report_regex.match(command_string)

        if arg_match is None:
            return re.sub(r"(^.*?arachni)", r"\1 --report=xml:outfile=%s" % self._output_file_path, command_string)
        else:
            return re.sub(arg_match.group(1),r"--report=xml:outfile=%s" % self._output_file_path, command_string)
            
    def getHostname(self, url):
        """
        Strips protocol and gets hostname from URL.
        """       
        reg = re.search("(http|https|ftp)\://([a-zA-Z0-9\.\-]+(\:[a-zA-Z0-9\.&amp;%\$\-]+)*@)*((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|localhost|([a-zA-Z0-9\-]+\.)*[a-zA-Z0-9\-]+\.(com|edu|gov|int|mil|net|org|biz|arpa|info|name|pro|aero|coop|museum|[a-zA-Z]{2}))[\:]*([0-9]+)*([/]*($|[a-zA-Z0-9\.\,\?\'\\\+&amp;%\$#\=~_\-]+)).*?$", url)
        self.protocol = reg.group(1)
        self.hostname = reg.group(4)

        if self.protocol == 'https':
            self.port=443
        if reg.group(11) is not None:
            self.port = reg.group(11)
            
        return self.hostname

    
    def getAddress(self, hostname):
        """
        Returns remote IP address from hostname.
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.error, msg:
                                                        
            return self.hostname


def createPlugin():
    return ArachniPlugin()
