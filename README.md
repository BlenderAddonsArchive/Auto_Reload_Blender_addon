# Auto Reload - Blender (2.9x) addon

[Auto Reload Releases](https://github.com/samytichadou/Auto_Reload_Blender_addon/releases)  

Auto Reload is a Blender addon design to automatically refresh external files when modified (*images, movie clips, libraries, sound and cache files*).

Here is a showcase video of the addon 
https://www.youtube.com/watch?v=EwUSCX48Lkw

If you like this addon, you can help me [here](https://ko-fi.com/tonton_blender) through Donation, to buy me a coffee and allow me to continue to develop free tools.
___

## **UI**

*Auto Reload* interface :  

### - ***Popover***

![Popover](https://raw.githubusercontent.com/samytichadou/Auto_Reload_Blender_addon/master/help_images/top_bar_menu_open.png)

Handy accessible menu located in the right part of the topbar to quickly activate/deactivate *Timer* through the *stopwatch button*, and select what to reload from the popover.

### - ***Preferences***

![Addon Preferences](https://raw.githubusercontent.com/samytichadou/Auto_Reload_Blender_addon/master/help_images/addon_preferences.png)

- **Image Timer Frequency :** 
set here the time interval for automatic Check/Reload for external files
- **On Startup section :** Setup general behavior of the addon on Blender startup

___

## **Known Issues**

- Cache files (*alembic and usd*) can be *sequential* (one file per frame for animation). This is not supported for now. 
If any user has some sample sequential cache files to test the addon, it could be implemented quickly.
