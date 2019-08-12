import os, json, socket
import logging
import uuid

from .fqdn import FQDNS, get_current_ip_for_fqdns
from .flowlog import filter_parsed_flowlog, parse_flowlog
from azure.storage.blob import BlockBlobService

import azure.functions as func




def main(msg: func.QueueMessage, outputblob: func.Out[str]) -> None:
    block_blob_service = BlockBlobService(connection_string = os.environ.get("input_STORAGE"))
    msg_body = json.loads(msg.get_body().decode('utf-8'))
    try:
        blob_path = msg_body["data"]["url"]
    except:
        logging.info("Failed to open url for {}".format(msg.id))
    
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {msg.id}")
    
    try:
        blob_container_name = blob_path.split('/')[3]
        current_nsg = blob_path.split('/')[8]
        blob_name = '/'.join(blob_path.split('/')[4:])
    except IndexError:
        logging.info("Blob found that doesn't have 9 splits.  Exiting.")
        return None
    # Load in the triggered blob's data
    localFilename = str(uuid.uuid4())+".json"
    if os.path.exists(localFilename):
        os.remove(localFilename)
    block_blob_service.get_blob_to_path(blob_container_name, blob_name, localFilename)
    with open(localFilename, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    # Parse the file to be a list of dictionaries
    parsed_results = parse_flowlog(data, current_nsg)
    logging.info(f"There were {len(parsed_results)} flow log entries found.")
    # Early stopping if there are no logs found
    if len(parsed_results) == 0:
        logging.info(f"Exiting due to no entries found.")
        return None
    logging.info(f"Sample result: {json.dumps(parsed_results[0])}")
    
    # Filter based on fqdns, rule name, and direction
    allowed_fqdn_ips = get_current_ip_for_fqdns(FQDNS)
    filtered_results = filter_parsed_flowlog(
        parsed_log = parsed_results,
        isInLastNMinutes = 2,
        dstIpAddressNotIn = ["40.79.44.59"], # TODO: Figure out what this belongs to!
        dstIpAddressDstPortNotIn = allowed_fqdn_ips,
        ruleIs = "UserRule_Port_other",
        directionIs = "O"
        )
    logging.info(f"There were {len(filtered_results)} flow log entries that matched the criteria.")
    if len(filtered_results) == 0:
        logging.info(f"Exiting due to no filtered results remaining.")
        return None
    outputblob.set(json.dumps({"value":filtered_results}))
    logging.info("Completed write to blob")
    
