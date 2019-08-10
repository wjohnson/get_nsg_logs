from datetime import datetime, timedelta

def parse_flowlog(data, current_nsg):
    """
    :param data dict(str, str): Contents of a flowlog file in dictionary form.
    :param current_nsg str: Name of current NSG being processed.
    :rtype list(dict(str, str)): The contents of the flowlog file transformed into a list of dictionaries. 
    """
    output = []
    for record in data['records']:
        for rule in record['properties']['flows']:
            for flow in rule['flows']:
                for flowtuple in flow['flowTuples']:
                    tupleValues = flowtuple.split(',')
                    output.append(
                        {
                        "eventTime":record["time"],
                        "rule": rule["rule"],
                        "nsgName":current_nsg,
                        "srcIp":tupleValues[1],
                        "dstIp":tupleValues[2],
                        "srcPort":tupleValues[3],
                        "dstPort":tupleValues[4],
                        "direction":tupleValues[6],
                        "action":tupleValues[7]
                        }
                    )
    return output


def filter_parsed_flowlog(parsed_log, **kwargs):
    """
    :param parsed_log list(dict(str,str)): List of flowlogs in the dictionary format.
    :rtype list: List of flowlogs as dictionaries filtered by kwarg criteria.

    Optional kwargs
    :param dstIpAddressNotIn list: List of IP Addresses to exclude based on destination IP.
    :param dstIpAddressDstPortNotIn list(tuple(str,str)): List of IP addresses and ports to excluded
        based on destination IP and port.
    :param isInLastNMinutes int: 
    :param ruleIs str: Rule field must match ruleIs (a valid NSG rule).
    :param directionIs str: Direction field must match directionIs (O or I).
    """
    filtered_log = []
    for flowlog in parsed_log:
        safe_to_append = 0
        if "isInLastNMinutes" in kwargs:
            log_date = datetime.strptime(flowlog["eventTime"][0:19], "%Y-%m-%dT%H:%M:%S")
            safe_to_append += int(
                ((datetime.utcnow() - log_date).seconds / 60) <= kwargs["isInLastNMinutes"]
            )

        if "dstIpAddressNotIn" in kwargs:
            safe_to_append += int(flowlog["dstIp"] not in kwargs["dstIpAddressNotIn"])
        if "dstIpAddressDstPortNotIn" in kwargs:
            safe_to_append += int(not any(
                [flowlog["dstIp"] == filter_ip\
                    and flowlog["dstPort"] == filter_port\
                    for filter_ip, filter_port\
                    in kwargs["dstIpAddressDstPortNotIn"]
                ]))
        if "ruleIs" in kwargs:
            safe_to_append += int(flowlog["rule"] == kwargs["ruleIs"])
        if "directionIs" in kwargs:
            safe_to_append += int(flowlog["direction"] == kwargs["directionIs"])
        if safe_to_append == len(kwargs):
            filtered_log.append(flowlog)

    return filtered_log