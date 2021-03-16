
Capsule is a plugin for Blender that makes the process of exporting quick and seamless, leveraging Blender's inbuilt export formats to let you export hundreds of assets into multiple formats with a single click.


## Features

* **Batch Exports** - Mark hundreds of objects and groups in a scene for export and export them all with one click. If you've made changes to assets in the scene and need to re-export them, it's as simple as one more click.

* **Export Lists** - Get an overview of all objects prepared for export and quickly change their settings from the list menus.

* **Export Presets** - Create detailed sets of export settings, supporting Alembic, Collada, FBX, GLTF, OBJ, STL and USD export formats.

* **Origin Point Export** - You can decide where the origin point is in your exports, no need to manually move around your objects before exporting.

* **Automated Folder Structures** - Capsule lets you automatically generate folders for your exports to help keep complex export setups organised.



## Installation

- Download the latest release from the releases page, unzip the download and then ZIP the "Capsule" folder.

- Under Blender’s User Preferences Menu, in the Add-ons section, click, “Install From File”, and select the ZIP file.

- The add-on will appear in the list, simply click the checkbox next to it’s title to activate it.


## FAQ
**How do I use this plugin?**

Check out the Github Wiki for quick instructions on getting started - https://github.com/Takanu/Capsule/wiki.


**What version of Blender does the plugin work with?**

The current version supports Blender 2.92.


**Are there things that Capsule can't currently export?**

Theres a few use cases where Capsule may have trouble exporting assets from your scene:

* Animations that aren't attached to Armature Bones - If you try to do this when the asset is using an Object Origin Point for export it will likely fail, keep these to using Scene origin points.

* Bone Constraints - The "Preserve Armature Constraints" button under the Armature tab in the Export Presets menu can help if you need to export an armature with bone constraints, as it is unlikely to export properly when left. This however is currently an experimental feature, so results may vary.


**What if i have a problem or bug with the add-on?**

* You can post an issue on the GitHub page (https://github.com/Takanu/Capsule/issues), this is the best place to post an issue as I can categorize and keep track of them in one place.



**Do you have any other cool add-ons?**

Yep, and they're all completely free - check out my GitHub account for other Blender goodies (https://github.com/Takanu).




---

If you like this plugin and want to support future development, [consider buying me a coffee](https://paypal.me/takanukyriako) ☕️.
