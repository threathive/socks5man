import logging

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from socks5man.ServerManager import ServerManager

server = Flask(__name__)

@server.route("/")
def list_socks5_servers():
    message = None
    server_manager = ServerManager()

    if "del" in request.args.keys():
        id = request.args.get("del")
        message = server_manager.delete_server(id)

    if "checkstatus" in request.args.keys():
        if not server_manager.update_server_status(request.args.get("checkstatus")):
            message = "Server does not exist"

    servers = server_manager.get_all_servers()

    return render_template("listservers.html", servers=servers,
                           message=message)

@server.route("/server/get")
def get_socks5_server():
    server_manager = ServerManager()

    json_response = {"servers": []}

    server = server_manager.get_server_json()

    if server is not None:
        json_response["servers"].append(server)
        return jsonify(json_response), 200

    return jsonify(json_response), 404


@server.route("/server/add", methods=["POST", "GET"])
def add_socks5_server():
    message = None
    if request.method == "POST":
        message = ServerManager().add_server(request)

    return render_template("add_server.html", message=message)


def start_api():
    listen_ip = "0.0.0.0"
    listen_port = 4242

    logging.info("Starting socks5man api server on %s:%s",
                 listen_ip, listen_port)

    server.run(listen_ip, listen_port, debug=True)
