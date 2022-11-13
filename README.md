# QuickSync
 A python script which is easy to use for you to sync your files with a webdav server.

## Preliminaries

Please ensure you have installed `Python >= 3.5`.

The script use WebDav3Client for transmitting data.So you need use

`$ pip install webdavclient3` 

to ensure it can be used in your environment.

## Quick Start

First,download the codes:

```
git clone https://github.com/WendaoLee/QuickSync.git target_folder
```

Then,you should finish configuration of your webdav-server:

```bash
python target_folder/QuickSync.py config --server 'protocol://yourserver address' --account 'acconut' --password 'password'
```

Now,you can choose a folder to sync. Out of version control consideration(Not the truly version control),we use a json file named `pack_QUICKSYNC.json` for the script to sync your files. So before your first sync,please enter this:

```bash
python target_folder/QuickSync.py update folder_path
```

This will create a file named `pack_QUICKSYNC.json` in the `folder_path`.All its key-values inherited from the configuration in your `config` command. If you don't want this,you can use extra parameter to make special configuration:

```bash
python target_folder/QuickSync.py update folder_path --server server_address --account account_id --password password
```

 Then,just sync your files with:

```bash
python target_folder/QuickSync.py -f folder_path
```

**Notice**,if you use relative path,make sure you use`./path`,not the `/path`,especially in Linux.

## Usage

```
usage: QuickSync [-h] [-f F] {sync,config,update,get} ...

This is a quick sync program for webdav. You can use this script to sync your file from a webdav server.

positional arguments:
  {sync,config,update,get}
    sync                Use this to sync your files.
    config              The sub-command is used to make global config for your sync script.
    update              This command like 'git commit',without commit you cannot push your change.You must use this
                        command to make a folder be available for our sync.

options:
  -h, --help            show this help message and exit
  -f F                  -f is the abbreviation of 'folder_path'.You enter the local folder's path here. For
                        instance,'-f ./SyncFolder' with relative path or '/home/usr/SyncFolder' in Linux and
                        'C:\Windows\SyncFolder' in Windows with absolute path. And this is a convenient usage of 'sync
                        -f'.With it you start you sync process with your server. If you have finished config and use
                        'update' command for your folder,you can just enter the folder's path then start sync your
                        file easily. If not,it will throw message info to push you enter the config.
```



```bash
usage: QuickSync sync [-h] [-f F]

options:
  -h, --help  show this help message and exit
  -f F        -f is the abbreviation of 'folder_path'.You enter the local folder's path here. For instance,'-f
              ./SyncFolder' with relative path or '/home/usr/SyncFolder' in Linux and 'C:\Windows\SyncFolder' in
              Windows with absolute path. If you have finished config and use 'update' command for your folder,you can
              just enter the folder's path then start sync your file easily. If not,it will throw message info to push
              you enter the config.
```



```bash
usage: QuickSync get [-h] [-t T] [-f F]

options:
  -h, --help  show this help message and exit
  -t T        The folder's name in remote server.Just a name without sep.For instance,'-f folder_name'
  -f F        The local saved folder's path.
```



```bash
usage: QuickSync update [-h] [--server SERVER] [--account ACCOUNT] [--password PASSWORD] [--folder_name FOLDER_NAME]
                        folder_path

positional arguments:
  folder_path           The folder's path of which you want to sync.Must be entered.

options:
  -h, --help            show this help message and exit
  --server SERVER
  --account ACCOUNT
  --password PASSWORD
  --folder_name FOLDER_NAME
                        If this parameter entered,it will be the folder's name you see in your webdav server
```

