# QuickSync
 A python script which is easy to used for you to sync your files with a webdav server.

## Preliminaries

The script use WebDav3Client for transmitting data.So you need use

`$ pip install webdavclient3` 

to ensure it can be used in your env.

## Usage

You should git clone this project into your local env:

```git
git clone https://github.com/WendaoLee/QuickSync.git target_folder
```

Then,you can easily use it with command.

For instance,if you want to sync your files,you should first use this:

```bash
python target_folder/QuickSync.py update folder_path --server server_address --account account_id --password password
```

This will create a file named `pack_QUICKSYNC.json` in the `folder_path`.This file record your configuration for this folder to be synced. And this script use this file to avoid version-conflict during the sync across the platform.

As for convenience,you can make a global configuration with  `QuickSync config`:

```bash
python target_folder/QuickSync.py config --server server_address --account account_id --password password
```

  If so,you can just use

```bash
python target_folder/QuickSync.py update folder_path
```

To create and update the  `pack_QUICKSYNC.json` .

With `pack_QUICKSYNC.json` settled down,you can easily use 

```
python target_folder/QuickSync.py -f folder_path
```

 to sync your file.

