# Reading NSG logs from Blob Storage with an Azure Function

**Please see the [original script](https://github.com/erjosito/get_nsg_logs/blob/master/get_nsg_logs.py) from Jose Moreno for more insight into how the parsing / `get_nsg_logs.py` script works.***
You might have set your Azure Vnet, with some NSGs. You start rolling apps, to the point where you have many VMs, and many NSGs. Somebody makes an application upgrade, or installs a new application, but traffic is not flowing through. Which NSG is dropping traffic? Which TCP ports should be opened?

One possibility is using Traffic Analytics. Traffic Analytics is a two-step process:
1. NSG logs are stored in a storage account
2. NSG logs from the storage account are processed (consolidated and enriched with additional information) and made queriable

One of the nicest features of Traffic Analytics is being able to query logs with the KQL (Kusto Query Language). For example, you can use this query to find out the dropped flows in the last 3 hours for IP address 1.2.3.4:

```
AzureNetworkAnalytics_CL
| where TimeGenerated >= ago(1h)
| where SubType_s == "FlowLog"
| where DeniedInFlows_d > 0 or DeniedOutFlows_d > 0
| where SrcIP_s == "1.2.3.4"
| project NSGName=split(NSGList_s, "/")[2],NSGRules_s,DeniedInFlows_d,DeniedOutFlows_d,SrcIP_s,DestIP_s,DestPort_d,L7Protocol_s
```

However, you will notice that there is a time lag, and you will not find the very latest logs in Log Analytics. The original NSG Flow logs are stored in storage account, in JSON format, so you could get those logs using the Azure Storage SDK.

You can deploy this Azure Function to parse and identify outbound traffic against an nsg rule of Port_other with an nsg named hdi_nsg.