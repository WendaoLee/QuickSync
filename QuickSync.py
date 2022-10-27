import argparse, os, json, time
import TerminalLogger
from webdav3.client import Client


def set_global_config(args):
    script_path = os.path.dirname(os.path.realpath(__file__))
    with open(file=script_path + '/config.json', mode="r+", encoding="utf-8") as f:
        theLocalConfig = json.load(f)
        if args.server:
            theLocalConfig['server'] = args.server
        if args.account:
            theLocalConfig['account'] = args.account
        if args.password:
            theLocalConfig['password'] = args.password
        f.seek(0)
        f.truncate()
        f.write(json.dumps(theLocalConfig))
        TerminalLogger.LOGGER.DEBUG(
            "Have changed your config file,the updated-content is{content}".format(content=str(theLocalConfig)))
        TerminalLogger.LOGGER.INFO('Finish config')


def update_folder_json(args):
    if not args.folder_path:
        raise ValueError("Cannot get the folder_path enter")
    if not os.path.isabs(args.folder_path):
        # getcwd() gets the target commandline excute path,so if it is not abpath,it must be a relative path.
        # So we use this to get the whole path.
        args.folder_path = os.getcwd() + args.folder_path

    if os.path.exists(args.folder_path + "/pack_QUICKSYNC.json"):
        with open(file=args.folder_path + "/pack_QUICKSYNC.json",
                  mode="r+", encoding="utf-8") as f:
            thePackConfig = json.load(f)
            thePackConfig['Version'] = time.time_ns()
            if args.server:
                thePackConfig['server'] = args.server
            if args.account:
                thePackConfig['account'] = args.account
            if args.password:
                thePackConfig['password'] = args.password
            if args.folder_name:
                thePackConfig['FolderName'] = args.folder_name
            f.seek(0)
            f.truncate()
            f.write(json.dumps(thePackConfig))
        TerminalLogger.LOGGER.INFO('Finish update!')
        return
    else:
        # default folder name for saving in the server is the folder's local name.
        folder_name = args.folder_path.split(os.sep)[
            len(args.folder_path.split(os.sep)) - 1
            ]
        # Get global config from the script's folder config file.
        with open(file=os.path.dirname(os.path.realpath(__file__)) + os.sep + 'config.json',
                  mode="r+", encoding="utf-8") as f:
            theLocalConfig = json.load(f)

        # If you target the special folder name for saving in server,then it has priority to write into the pack file
        if args.folder_name:
            folder_name = args.folder_name

        with open(file=args.folder_path + "/pack_QUICKSYNC.json",
                  mode='w+', encoding="utf-8") as f:
            pack_dict = {
                "FolderName": folder_name,
                "Version": time.time_ns(),
                "server": theLocalConfig['server'],
                "account": theLocalConfig['account'],
                "password": theLocalConfig['password']
            }
            f.write(json.dumps(pack_dict))

        TerminalLogger.LOGGER.INFO('Finish Update with creating pack file')
        return


def sync_files(args):
    if not args.f:
        TerminalLogger.LOGGER.ERROR('-f missing')
        assert ValueError("-f shouldn't be None")

    if not os.path.isabs(args.f):
        args.f = os.getcwd() + args.f

    if not os.path.exists(args.f + os.sep + "pack_QUICKSYNC.json"):
        TerminalLogger.LOGGER.ERROR("pack json file missing!Have you used the command 'update' before?")
        assert FileNotFoundError("pack json missing!")

    with open(file=args.f + os.sep + "pack_QUICKSYNC.json", mode="r", encoding="utf-8") as f:
        theLocalPackConfig = json.load(f)
    options = {
        'webdav_hostname': theLocalPackConfig['server'],
        'webdav_login': theLocalPackConfig['account'],
        'webdav_password': theLocalPackConfig['password'],
        'webdav_timeout': 30
    }
    webdav = Client(options)
    # If remote doesn't have such a folder
    if not webdav.check("/" + theLocalPackConfig["FolderName"]):
        TerminalLogger.LOGGER.WARNING('Because remote server does not have such folder,we now uploading....')
        webdav.upload("/" + theLocalPackConfig["FolderName"],
                      local_path=args.f)
        TerminalLogger.LOGGER.INFO("Upload success!")
        return

    # If remote's target folder doesn't have pack json
    if not webdav.check("/" + theLocalPackConfig["FolderName"] + "/pack_QUICKSYNC.json"):
        TerminalLogger.LOGGER.ERROR("Remote file doesn't have pack json.Cannot sync out of the Safety Consideration.")
        return

    # Check the remote version
    webdav.download("/" + theLocalPackConfig["FolderName"] + "/pack_QUICKSYNC.json", os.getcwd() + os.sep + "tmp.json")
    with open(file=os.getcwd() + os.sep + "tmp.json", mode='r+', encoding="utf-8") as f:
        version = int(json.load(f)['Version'])
    if int(theLocalPackConfig['Version']) > version:
        TerminalLogger.LOGGER.INFO("Local is the newer version,starting update....")
        webdav.upload("/" + theLocalPackConfig["FolderName"],
                      local_path=os.getcwd() + args.f)
        TerminalLogger.LOGGER.INFO("Upload success!")
    else:
        TerminalLogger.LOGGER.WARNING("Local is not the newer version.So stop the uploading.\n"
                                      "If you want to upload your file as you have changed your file.Make sure you have use UPDATE command")
        return


parser = argparse.ArgumentParser(prog='QuickSync',
                                 description="This is a quick sync program for webdav.\n You can use this script to sync your file from a webdav server.")
parser.add_argument('-f',
                    help="-f is the abbreviation of 'folder_path'.With it you start you sync process with your server."
                         "\nIf you have finished config and use 'update' command for your folder,you can just enter the folder's path then start sync your file easily."
                         "\nIf not,it will throw message info to push you enter the config")
subparser = parser.add_subparsers()
parser.set_defaults(func=sync_files)

# QuickSync config
config_help_string = """
The sub-command is used to make global config for your sync script. 
"""
config_parser = subparser.add_parser('config', help=config_help_string)
config_parser.add_argument('--server',
                           type=str,
                           help="The server's address,including protocol and the port.\n"
                                "For instance:\n 'http://localhost:8080'")
config_parser.add_argument('--account',
                           type=str,
                           help="If your webdav server isn't anonymous,you should config your login account and its password")
config_parser.add_argument('--password',
                           type=str,
                           help="If your webdav server isn't anonymous,you should config your login account and its password")
config_parser.set_defaults(func=set_global_config)

# QuickSync update
update_help_string = """
This command like 'git commit',without commit you cannot push your change.You must use this command to make a folder be available for our sync.
"""
update_parser = subparser.add_parser('update',
                                     help=update_help_string)
update_parser.add_argument('folder_path',
                           type=str,
                           help="The folder's path of which you want to sync.Must be entered.")
update_parser.add_argument('--server',
                           type=str)
update_parser.add_argument('--account',
                           type=str)
update_parser.add_argument('--password',
                           type=str)
update_parser.add_argument('--folder_name',
                           type=str,
                           help="If this parameter entered,it will be the folder's name you see in your webdav server")
update_parser.set_defaults(func=update_folder_json)

# config_server_parser = config_subparser.add_parser('--server')
# config_server_parser.add_argument('server',help="The server's address,including protocol and the port.\n"
#                                                 "For instance:\n 'http://localhost:8080'")

args = parser.parse_args()

args.func(args)
