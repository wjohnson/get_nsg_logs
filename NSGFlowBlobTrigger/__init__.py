import os, json, socket
import logging

from .fqdn import FQDNS, get_current_ip_for_fqdns
from .flowlog import filter_parsed_flowlog, parse_flowlog

import azure.functions as func


def main(nsgblob: func.InputStream, outputblob: func.Out[str]) -> None:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {nsgblob.name}\n"
                 f"Blob Size: {nsgblob.length} bytes")
    
    try:
        current_nsg = nsgblob.name.split('/')[8]
    except IndexError:
        logging.info("Blob found that doesn't have 8 splits.  Exiting.")
        return None
    # Load in the triggered blob's data
    data = json.loads(nsgblob.read().decode('utf-8'))
    # Parse the file to be a list of dictionaries
    parsed_results = parse_flowlog(data, current_nsg)
    logging.info(f"There were {len(parsed_results)} flow log entries found.")
    # Early stopping if there are no logs found
    if len(parsed_results) == 0:
        return None
    logging.info(f"Sample result: {json.dumps(parsed_results[0])}")
    
    # Filter based on fqdns, rule name, and direction
    allowed_fqdn_ips = get_current_ip_for_fqdns(FQDNS)
    filtered_results = filter_parsed_flowlog(
        parsed_log = parsed_results,
        dstIpAddressDstPortNotIn = allowed_fqdn_ips,
        ruleIs = "UserRule_Port_other",
        directionIs = "O"
        )
    logging.info(f"There were {len(filtered_results)} flow log entries that matched the criteria.")

    outputblob.set(json.dumps({"value":filtered_results}))
    logging.info("Completed write to blob")
    
