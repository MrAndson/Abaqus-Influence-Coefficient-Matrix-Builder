# Abaqus-Influence-Coefficient-Matrix-Builder
A plug-in of FEM Software Abaqus to get influence coefficient matrix.

How to install it:

1 Download all files 下载所有文件

2 Put these files in a folder 将所有文件放到一个文件夹

3 Rename the folder as "Abaqus_plugins" 将文件夹重命名为"Abaqus_plugins"

4 Put the folder "Abaqus_plugins" in your abaqus current working directory 把这个文件夹放到abaqus工作目录内

5 Restart Abaqus 重启abaqus

6 Find a new botton “Infulence Coefficient Builder V5.0” in "Plug-ins" button. The "Plug-ins" button is in abaqus manu bar. 在abaqus菜单栏中的“Plug-ins”找到一个新按钮"Infulence Coefficient Builder V5.0"

7 Click the botton to start it. 点击并打开它

How to use it:

1 Choose the stage where you want to get the influence mataix. Make sure no "initial" in the GUI.

2 Input your node labels, in format "start : end : intervel,start : end,pointLabel"

3 Example:"1:6:2,7:9,10" means node label:"1,3,5,7,8,10"

4 Make you node label in right sequence of the mesh, not right, then cant calculate rightly.

5 The label "Start Calculating" is for testing, if dont know, keep it.

6 Press "OK" or "Apply" to start calculating.

7 When finished, a reminding sentence can bo found in abaqus message area. you wont miss it

8 Find the Influence Coefficient Matrix in you working directory.

9 Done

Note:

1 First use GitHub, anything wrong, please contact me

2 this plug-in is being used, if no more needs, no upgrade will be made.

3 Thanks

