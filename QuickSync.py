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

    # This struct is used to ensure the entered folder_path will become absolute path.
    # In linux,is the path is '/folder',it still be recognized as absolute path,
    # so here we need elif to ensure the final folder_path is a absolute path,as we need it to let things be done.

    # Here if it is running in windows,pass './folder' or '/folder',it will go in
    if not os.path.isabs(args.folder_path):

        if args.folder_path[0] == '.':
            # getcwd() gets the target running terminal's path,so if it is not absolute path,it must be a relative path.
            # So we use this to get the whole path.
            args.folder_path = os.getcwd() + args.folder_path.split('.')[1]
        else:
            args.folder_path = os.getcwd() + args.folder_path

    # to ensure in linux,relative path can convert to absolute path.
    elif args.folder_path[0] == '.' and os.name == 'posix':
        args.folder_path = os.getcwd() + args.folder_path.split('.')[1]

    # This struct is to check if pack_QUICKSYNC.json exist
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
            if args.globals:
                with open(file=os.path.dirname(os.path.realpath(__file__)) + os.sep + 'config.json',
                  mode="r+", encoding="utf-8") as g:

                  theLocalConfig = json.load(g)
                  thePackConfig['server'] = theLocalConfig['server']
                  thePackConfig['account'] = theLocalConfig['account']
                  thePackConfig['password'] = theLocalConfig['password']
            f.seek(0)
            f.truncate()
            f.write(json.dumps(thePackConfig))
        TerminalLogger.LOGGER.INFO('Finish update!')
        return
    else:
        # default folder name for saving in the server is the folder's local name.

        # Consider the situation:
        # In linux,for instance,the absolute path is '/home/usr/folderName'
        # But in windows,with process above,if user enter './FolderName',it will be 'C:\Users\Administrator\Documents/FolderName',
        # these two situations can get same result with split("/")
        # BUT,when user copy path from explore or cmd,it could be "C:\Users\Administrator\Document\FolderName".
        # So here we need a if structure to deal with these condition.
        if os.name == "nt" and len(args.folder_path.split("/")) == 1:
            folder_name = args.folder_path.split("\\")[
                len(args.folder_path.split("\\")) - 1
            ]
        else:
            folder_name = args.folder_path.split("/")[
                len(args.folder_path.split("/")) - 1
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

    # This struct used for ensuring the final path is the absolute path.See comments above in funcation update_folder_json
    if not os.path.isabs(args.f):
        if args.f[0] == '.':
            # getcwd() gets the target running terminal's path,so if it is not absolute path,it must be a relative path.
            # So we use this to get the whole path.
            args.f = os.getcwd() + args.f.split('.')[1]
        else:
            args.f = os.getcwd() + args.f

    # to ensure in linux,relative path can convert to absolute path.
    elif args.f[0] == '.' and os.name == 'posix':
        args.f = os.getcwd() + args.f.split('.')[1]

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
        TerminalLogger.LOGGER.ERROR("Are you trying to first download files which haven't processed with QuickSync before from server?"
                                    "If so,please use command 'get',not the command 'sync'")
        return

    # Check the remote version
    webdav.download("/" + theLocalPackConfig["FolderName"] + "/pack_QUICKSYNC.json", os.getcwd() + os.sep + "tmp.json")
    with open(file=os.getcwd() + os.sep + "tmp.json", mode='r+', encoding="utf-8") as f:
        version = int(json.load(f)['Version'])
    if int(theLocalPackConfig['Version']) > version:
        TerminalLogger.LOGGER.INFO("Local is the newer version,starting update....")
        webdav.upload("/" + theLocalPackConfig["FolderName"],
                    args.f)
        TerminalLogger.LOGGER.INFO("Upload success!")
    elif int(theLocalPackConfig['Version'] == version):
        TerminalLogger.LOGGER.WARNING("Local is not the newer version.So stop the uploading.\n"
                                      "If you want to upload your file as you have changed your file.Make sure you have use UPDATE command")
    else:
        TerminalLogger.LOGGER.DEBUG("Local is older,so begin downloading to sync file......")
        webdav.download(remote_path=theLocalPackConfig["FolderName"],
                        local_path=args.f)
        return


def get_files(args):
    if not args.f or not args.t:
        raise ValueError("Missing arguments.Both -f and -t should enter with GET command")

    # This struct used for ensuring the final path is the absolute path.See comments above in funcation update_folder_json
    if not os.path.isabs(args.f):
        if args.f[0] == '.':
            # getcwd() gets the target running terminal's path,so if it is not absolute path,it must be a relative path.
            # So we use this to get the whole path.
            args.f = os.getcwd() + args.f.split('.')[1]
        else:
            args.f = os.getcwd() + args.f

    # to ensure in linux,relative path can convert to absolute path.
    elif args.f[0] == '.' and os.name == 'posix':
        args.f = os.getcwd() + args.f.split('.')[1]

    # check local path's existence
    if not os.path.exists(args.f):
        TerminalLogger.LOGGER.ERROR('The local path is invalid!')
        raise NotADirectoryError("The local path is invalid.The path is {path}".format(path=args.f))

    with open(file=os.path.dirname(os.path.realpath(__file__)) + '/config.json', mode="r+", encoding="utf-8") as f:
        theLocalConfig = json.load(f)
    options = {
        'webdav_hostname': theLocalConfig['server'],
        'webdav_login': theLocalConfig['account'],
        'webdav_password': theLocalConfig['password'],
        'webdav_timeout': 30
    }
    webdav = Client(options)

    # If remote doesn't have such a folder
    if not webdav.check("/" + args.t):
        TerminalLogger.LOGGER.ERROR('The target source you request is not Found!')
        TerminalLogger.LOGGER.ERROR(
            "Are you sure you enter a right name?The -t shouldn't include '/' or '\\' such as '/folder_name'.")
        raise FileNotFoundError()

    # If remote's target folder doesn't have pack json
    if not webdav.check("/" + args.t + "/pack_QUICKSYNC.json"):
        TerminalLogger.LOGGER.WARNING("PLEASE NOTICE:")
        TerminalLogger.LOGGER.WARNING("Remote folder doesn't have pack-json.\n\n"
                                      "But you are using command GET,so we will try to download the file and pack it with pack_QUICKSYNC.json."
                                      "Then try to push pack_QUICKSYNC.json as for next time's usage.Nor we cannot sync it because of our default safety strategy in sync.\n"
                                      "but here may have unexpected error if the network connect not so wonderful.\n"
                                      "Please ensure your network is Okay\n"
                                      "If you ensure you're ready want to GET file.Enter 'y' to continue,'n' to exit.")
        isWait = True
        while isWait:
            choice = input("Enter your choice:")
            if choice == "n":
                return
            elif choice == "y":
                isWait = False
            else:
                TerminalLogger.LOGGER.WARNING("Please enter correct character")

        TerminalLogger.LOGGER.DEBUG("Start downloading.....")
        webdav.download(remote_path="/" + args.t,
                        local_path=args.f)
        TerminalLogger.LOGGER.DEBUG("Update pack_QUICKSYNC.json....")

        class ToObject(dict):
            def __getattr__(self, key):
                return self.get(key)

            def __setattr__(self, key, value):
                self[key] = value

        update_folder_json(ToObject({
            "folder_path": args.f,
            "server": None,
            "account": None,
            "password": None,
            "folder_name": args.t
        }))
        TerminalLogger.LOGGER.DEBUG("Now pushing file.....")
        webdav.push(remote_directory="/" + args.t,
                    local_directory=args.f)
        TerminalLogger.LOGGER.DEBUG("Success Get!")
        return

    TerminalLogger.LOGGER.INFO("The remote folder has pack_QUICKSYNC.json,start downloading......")
    webdav.download(remote_path="/" + args.t, local_path=args.f)


parser = argparse.ArgumentParser(prog='QuickSync',
                                 description="This is a quick sync program for webdav.\n You can use this script to sync your file from a webdav server.")
parser.add_argument('-f',
                    help="-f is the abbreviation of 'folder_path'.You enter the local folder's path here.And it is a convenient usage of 'sync -f'.With it you start you sync process with your server."
                         "\n For instance,'-f ./SyncFolder' with relative path or '/home/usr/SyncFolder' in Linux and 'C:\\Windows\\SyncFolder' in Windows with absolute path."
                         "\nIf you have finished config and use 'update' command for your folder,you can just enter the folder's path then start sync your file easily."
                         "\nIf not,it will throw message info to push you enter the config.")
subparser = parser.add_subparsers()
parser.set_defaults(func=sync_files)

# QuickSync sync
sync_parser = subparser.add_parser('sync',help="Use this to sync your files.")
sync_parser.add_argument('-f',
                         help="-f is the abbreviation of 'folder_path'.You enter the local folder's path here."
                         "\n For instance,'-f ./SyncFolder' with relative path or '/home/usr/SyncFolder' in Linux and 'C:\\Windows\\SyncFolder' in Windows with absolute path."
                         "\nIf you have finished config and use 'update' command for your folder,you can just enter the folder's path then start sync your file easily."
                         "\nIf not,it will throw message info to push you enter the config.")
sync_parser.set_defaults(func=sync_files)

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
update_parser.add_argument('--globals',
                           type=str,
                           help="If you want to update with the global config,use it with any para pass.")
update_parser.set_defaults(func=update_folder_json)

# QuickSync get
get_help_string = """
'get' is a subcommand for you to download files from a webdav server if you are in a new machine.
If you don't use this script to sync your files before,it will ask you to confirm your downloading.
"""
get_parser = subparser.add_parser('get')
get_parser.add_argument('-t',
                        type=str,
                        help="This is the abbreviation of '-target'.You should enter the folder's name in remote server here.Just a name without any sep.For instance,'-f folder_name'")
get_parser.add_argument('-f',
                        type=str,
                        help="The local saved folder's path.")
get_parser.set_defaults(func=get_files)

args = parser.parse_args()

args.func(args)
