# Asset-List-Generator

Asset List Generator is a lightweight utility that provides a convenient interface for generating Blender Remote Asset Library asset listings. It replaces the manual command-line workflow by allowing users to configure the Blender executable and asset library paths, then execute the `asset_listing generate` command with a single click.

Without this tool, setting up a Remote Asset Library can be complex and confusing, especially for users who are unfamiliar with command-line operations.

This utility was developed with AI assistance. It has been tested on Windows, but contributions are welcome to improve its functionality, code quality, and cross-platform support.

# Tutorial

The downloaded ZIP file contains `Asset List Generator.exe`. You can extract it anywhere, although it is recommended to place it in its own folder.

Running the executable should display the following interface.

* **Blender Executable**: The location of your `blender.exe`. The path must include blender.exe. at the end.
* **Asset Library Folder**: The root "folder" of your asset library. Within the folder, it may contain `.blend` files directly, or it may contain subfolders that contain asset libraries.

<img width="757" height="255" alt="image" src="https://github.com/user-attachments/assets/1ab4eb0a-99d2-49a8-8b69-f2f62d8ca3a0" />

Once both paths are configured correctly, click **Generate Asset List**.

Internally, this utility simply automates the procedure described in the official Blender documentation:

https://docs.blender.org/manual/en/dev/files/asset_libraries/remote_asset_libraries.html#creating-a-remote-asset-library

It launches Blender in the background, executes the `asset_listing generate` command, and generates the files required for a Remote Asset Library.
The white space displays the output from Blender's console. The process should finish with a message such as "Finished Successfully" as shown.

<img width="546" height="54" alt="image" src="https://github.com/user-attachments/assets/752c425d-5314-44e8-934a-ff7cf2bf2eb8" />

When the process completes successfully, the asset library folder should contain a `_v1` directory and an `_asset-library-meta.json` file. These files are required before uploading the asset library for online remote access.
The other two folders under mosaic contain my asset .blend files.
<img width="206" height="101" alt="image" src="https://github.com/user-attachments/assets/5a304801-b459-4617-b99c-bccfb93b169a" />
