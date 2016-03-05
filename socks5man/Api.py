import logging

from flask import Flask
from flask import jsonify

from socks5man.ServerManager import ServerManager

server = Flask(__name__)

@server.route("/server/get")
def get_socks5_server():
    
    server_manager = ServerManager()
    
    json_response = {"servers":[]}
    
    server = server_manager.get_server_json()
    
    if server is not None:
        json_response["servers"].append(server)
        return jsonify(json_response), 200
    
    return jsonify(**json_response), 404

def start_api():
    
    listen_ip   = "0.0.0.0"
    listen_port = 4242
    
    logging.info("Starting socks5man api server on %s:%s", listen_ip,
                                                           listen_port)
    server.run(listen_ip, listen_port)