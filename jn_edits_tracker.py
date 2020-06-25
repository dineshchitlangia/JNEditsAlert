#Custom Script for tracking Journal node edits
#This script uses simplejson as it is much faster than Python 2.6 json module and has the same functions set
#Following variables define the alert thresholds:
#OK_CEIL = 9
#WARN_FLOOR = 10
#WARN_CEIL = 19
#CRITICAL_FLOOR = 20
#To modify the thresholds, you may edit the above variables and redeploy the alerts

#!/usr/bin/env python


import collections
import os, fnmatch, datetime
import platform
import sys
from resource_management.core.logger import Logger
from resource_management.core.providers import mount
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from ambari_commons import OSConst

import urllib2
import ambari_simplejson as json
import logging
import traceback

from resource_management.libraries.functions.curl_krb_request import curl_krb_request
from resource_management.libraries.functions.curl_krb_request import DEFAULT_KERBEROS_KINIT_TIMER_MS
from resource_management.libraries.functions.curl_krb_request import KERBEROS_KINIT_TIMER_PARAMETER
from resource_management.libraries.functions.curl_krb_request import CONNECTION_TIMEOUT_DEFAULT
from resource_management.core.environment import Environment
from resource_management.libraries.functions.namenode_ha_utils import get_all_namenode_addresses


HDFS_SITE_KEY = '{{hdfs-site}}'
NN_NAMESERVICE = '{{hdfs-site/dfs.nameservices}}'
JN_EDITS_DIR = '{{hdfs-site/dfs.journalnode.edits.dir}}'


OK_CEIL = 9
WARN_FLOOR = 10
WARN_CEIL = 19
CRITICAL_FLOOR = 20

def get_tokens():
  """
  Returns a tuple of tokens in the format {{site/property}} that will be used
  to build the dictionary passed into execute

  :rtype tuple
  """
  return (HDFS_SITE_KEY, NN_NAMESERVICE, JN_EDITS_DIR)



def execute(configurations={}, parameters={}, host_name=None):
  if not HDFS_SITE_KEY in configurations:
    return 'SKIPPED', ['{0} is a required parameter for the script'.format(HDFS_SITE_KEY)]


  hdfs_nameservice = None
  if NN_NAMESERVICE in configurations:
  	hdfs_nameservice = configurations[NN_NAMESERVICE]

  edits_dir = None
  if JN_EDITS_DIR in configurations:
  	edits_dir = configurations[JN_EDITS_DIR]

  pathis = edits_dir + "/" + hdfs_nameservice

  result = find('*_inprogress_*', pathis)

  for i in result:
    stat = os.stat(i)
    motime = stat.st_mtime
    modtimestamp = datetime.datetime.fromtimestamp(motime)
    nowtime = datetime.datetime.now()
    difftime = nowtime - modtimestamp
    days, seconds = difftime.days, difftime.seconds
    hours = days * 24 + seconds // 3600
    secs = days * 24 * 3600 + seconds
    result = getstatus(secs)
    return result    

#### find method takes 2 arguments, "pattern" which checks for the presence of edits_inprogress_#### 
#### and the "path" which is the JN Edits folder, from above configs we would have to pass "edits_dir"
#### 

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result



def getstatus(secs):
    if secs > WARN_FLOOR and secs < WARN_CEIL:
        result_code = 'WARNING'
        label = "JN edits are not happening for over ",WARN_FLOOR," seconds"
    if secs < OK_CEIL:
        result_code = 'OK'
        label = "JN edits are happening well"
    if secs > CRITICAL_FLOOR:
        result_code = 'CRITICAL'
        label = "JN edits are not happening for over ",CRITICAL_FLOOR," seconds"
    return ((result_code, [label]))
