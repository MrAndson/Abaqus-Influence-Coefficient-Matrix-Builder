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

20251203134454 upgrade

关于如何点选：

打开插件后，一共包括9行文本（包括标题行和按钮行）：

第一行 标题；

第二行 选择你需要计算影响系数矩阵的分析步（不同分析步的边界条件可能不同，因此需要指定，所有的操作都会在指定分析步之后开始，包括施加单位载荷，提取数据等，如果计算成功，可以发现新的分析步，一般以“AutoStep”开头）；

第三行 指定你需要计算影响系数矩阵的部件（part），对密封接触力学分析而言，一般是研究的密封件；

第四行 选择你想要计算影响系数矩阵对应的接触边界条件，对密封接触力学分析而言，一般是密封界面对应的接触条件（该插件仅适用于单个密封界面，如有多个密封界面，可交流研究如何修正）；

第五行 计算机CPU数和施加单位载荷大小，一般单位载荷给1；

第六行 需要计算影响系数矩阵的节点编号，对密封接触力学分析而言，是密封件（对应第三行）在密封接触边界（对应第四行）上的所有节点，有顺序要求，请参考GitHub文档；

第七行 测试用按钮，可以无视，其功能是在已有多个影响系数计算结果odb文件的基础上，直接提取影响系数矩阵；如果之前未运行，请不要点击；

第八行 文件标签；

第九行 操作按钮，点击“OK”，在当前输入的内容下，关闭gui，开始计算；点击“Apply”，保持当前gui不关闭，开始计算；

