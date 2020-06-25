# JNEditsAlert
Ambari Alert for HDFS Journal Node Edits health

## Motivation

* With the default monitoring, Ambari does not trigger alerts when there is a failure of edits in one of the Journal Nodes in JN Quorum. 
* In typical HDFS HA environment, there are at least three Journal node daemons deployed. 
* If any one of the daemons fails to maintain the edits, then we are at risk of JN Quorum failure if another journal node hits similar issue as other journal node.
* Without the JN Quorum, the Namenodes will crash leading to a system wide outage.



## Reasons why Journal Nodes may not get updated

* Disk space getting exhausted
* Corrupt permissions
* Exhausted HDFS Handlers in Journal Node hosts
* Disk I/O issues on Journal Node hosts
* CPU contention issues on Journal Node hosts


## Custom Alert

The custom alert should get triggered if the edits_inprogress files does not get updated in the defined time intervals.

edits_inprogress files are located on Journal Node edits directory specified by `dfs.journalnode.edits.dir` in hdfs-site configurations.

* Copy jn_edits_tracker.py and alerts-test.json to `/var/lib/ambari-server/resources/host_scripts`

* Restart the Ambari-Server

* Execute the following command to list all the existing alerts:
`curl -u ambariUser:ambariPassword -i -H 'X-Requested-By:ambari' -X GET http://ambariHost:ambariPort/api/v1/clusters/ClusterName/alert_definitions`

* Install the custom alert using Curl command as following:
`cd /var/lib/ambari-server/resources/host_scripts`
`curl -u ambariUser:ambariPassword -i -H 'X-Requested-By:ambari' -X POST -d @alerts-test.json http://node1.example.com:8080/api/v1/clusters/ClusterDemo/alert_definitions`
