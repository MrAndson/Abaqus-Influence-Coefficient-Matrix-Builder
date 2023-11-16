# -*- coding:utf-8 -*-
# Do not delete the following import lines
import sys                              # 系统控制模组导入，用于控制程序运行状态
from abaqus import *                    # Abaqus 模组导入
from abaqusConstants import *           # Abaqus 常用参数模组导入
from odbAccess import *                 # Odb处理模组导入
from textRepr import *                  # 这个是用于prettyprint的
import time                             # 导入time模组用于计时
import __main__                         # 说实话不知道干啥的，abaqus模组必备？
import section                          # 下面基本上是abaqus内部模组
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
import os                               # 打开程序用
import collections                      # 这东西是有序字典要用
import csv


#############################################################################################################################
# 函数定义区开始


# 函数job_submit,用于提交job
# 输入模型名称（默认为Model-1）、job名称、CPU数量、是否需要输入结束信息
# 无返回值
def job_submit(model_name, job_name, cpu_num, message_note = False):
    mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=cpu_num, 
    numDomains=cpu_num, numGPUs=0)                                      # 上面三行是一整句话，其目的是构建一个job，但不提交
    # mdb.jobs[jobName].writeInput(consistencyChecking=OFF)             # 提交input文件，事实上这句话没用，可以拿来测试功能，但同时需要执行多个job时不推荐
    mdb.jobs[job_name].submit(consistencyChecking=OFF)                   # 作业提交计算
    mdb.jobs[job_name].waitForCompletion()                               # 等待本次作业完成
    if message_note:
        print(job_name + " finished")                                   # 默认不输出提示消息，表明本次完成
    # 函数定义完毕，注释完毕，测试完毕


# 函数node_input_to_node_list，用于将输入的node节点格式转变为list格式，包括去重和格式识别。
# 但格式识别功能较弱，对随意输入内容可能不能判断，需要保证输入格式正确
# 输入节点列表（格式为字符串），格式要求为”1:10:2,4:5,6“类型
# 输出转化格式后的列表（格式为list）
# 有返回值
def node_input_to_node_list(node_input):
    #将输入的节点格式转换为对应的list
    node_list = []                                                      # 定义一个空列表用于存放之后的节点列表
    range_groups = node_input.split(',')                                # 把输入的字符串先用 ，作为分割标志分开，得到节点组合形成的列表
    flag = 1                                                            # 定义一个flag，用于指示是否有格式错误，有格式错误变为0
    for range_group in range_groups:                                    # 对节点组合形成的列表进行遍历，对其中的每一个节点组合均进行如下操作
        range_split = range_group.split(':')                            # 首先将该节点组合按照 ：进行分割，对分割结果进行判断
        if len(range_split) == 3:                                       # 分割结果长为3，则为 起始：终止：间隔 的字段形式，将其每个放到range函数里追加到node_list里
            for node_num in range(int(range_split[0]),int(range_split[1]),int(range_split[2])):
                node_list.append(node_num)
        elif len(range_split) == 2:                                     # 分割结果长为2，则为 起始：终止 的字段形式，类似地将其放入range函数
            for node_num in range(int(range_split[0]),int(range_split[1])):
                node_list.append(node_num)
        elif len(range_split) == 1:                                     # 分割结果长为1，则为 节点编号 的形式，直接将其加入node_list中
            node_list.append(int(range_split[0]))
        else: 
            flag = 0
            break   
    # 简易判断格式是否有误，有误则退出script，
    if flag == 0:
        print("Input format wrong. Script was terminated")              # Respect for Terminator
        print("Please enter the correct format and run script again.")  # 其实只是为了反馈语句比较完整，这句话用处不大
        sys.exit()                                                      # 如果格式不满足要求，则终止程序，要求重新输入后再运行
    else:
        # 将输入的节点list去重，同时不改变顺序                          # 仔细想了想，似乎没有去重这个需求
        node_list_deduplicated = list(set(node_list))                   # 利用set的不重复性去重，但此时会出现顺序紊乱
        node_list_deduplicated.sort(key = node_list.index)              # 利用元素在node_list中出现的顺序排序,实现恢复输入顺序
        # 如果有重复，提示一下，但是不会退出
        if len(node_list_deduplicated) != len(node_list):               # 判断是否有重复的方式是根据去重前后的list长度是否相同
            print("Input format wrong. Duplicated nodes detected and deleted.")   
        else:
            print('Input format right. Nodes Input transformed')
        return node_list_deduplicated                                   # 该函数有返回值用于将处理后的list输出
    # 函数定义完毕，注释完毕，测试完毕


# 函数node_list_to_node_set，用于将输入的node_list转变为Abaqus中的节点集合
# 输入node_list，模型名称，部件名称，集合名称
# 在使用图形化界面时，需要先调用node_input_to_node_list函数将格式化输入文本转换为list
# 无返回值
# 发现有两种不同的建立set的方式，默认为第一种，建立在part上，另外一种建立在instance上，差别不大，但会影响之后的数据提取操作，所以强制要求必须True，冗余只是为了之后可能用到
def node_list_to_node_set(model_name, part_name, node_list, set_name, in_part = True):
    if in_part:
        p = mdb.models[model_name].parts[part_name]                         # 指定建立集合的模型与对应部件
        n = p.nodes                                                         # 指定建立集合类型为节点集
        nodesSeq=n.sequenceFromLabels(node_list)                            # 建立包括node_list中所有标号的节点集合
        p.Set(nodes=nodesSeq, name=set_name)                                # 设定节点集合名称
    else:
        a = mdb.models[model_name].rootAssembly                             # 指定建立集合的模型与对应部件，该方法目前禁止调用，因为没发现区别
        instance_name = part_name + '-1'                                    # 由于建立在instance上，所以指定instance名称
        n = a.instances[instance_name].nodes                                # 指定建立集合类型为节点集
        nodesSeq=n.sequenceFromLabels(node_list)                            # 建立包括node_list中所有标号的节点集合
        a.Set(nodes=nodesSeq, name=set_name)                                # 设定节点集合名称
    # 函数定义完毕，注释完毕，测试完毕


# CPRESS数据提取逻辑说明
# 原本以为实现提取参数很简单，但为了提取CPRESS数据写了三个函数和一个测试用函数，简直了
# 这么做的原因是因为对于常规的U和S，其定义输出场和实际输出场是一个名字
# 但对于CPRESS和其他一些C开头的输出场，上述两个量它名称不一样
# 目前认为不一样的原因是由于有两处接触区域，在abaqus内部认为是两个CPRESS接触场，只不过GUI提取是直接隐藏了这个说法
# 因此用代码实现，就需要将这里面的两个CPRESS场（事实上可能有多个，所以进行遍历），全部提取出来，并将不同场节点数据进行加和
# 加和就是简单的加和，看代码能知道实现方法
# 所以写了三个函数，monitor，detector和kernel
# monitor用于判断是否要提取CPRESS，调用后两个函数
# detector 用于遍历所有场，取出其中的CPRESS场名称（GUI中都叫CPRESS，但底层分了好几个不同名称）
# kernel是提取核心，用于提取并返回值，若仅告诉其提取场为CPRESS，则仅能提取第一个CPRESS场（若有多个接触面则会出现问题，单个接触区域不会）
# 逻辑为：如果monitor判断要提取CPRESS，则调用detector取出所有CPRESS场，再将取出结果传给kernel用于提取参数
# 如果monitor判断不是提取CPRESS，则进入另一分支，但当前该分支pass，为赶进度不写，这个分支是用于提取其他场的。
# 下面为三个函数具体说明


# 函数cpress_detector，专门用于提取CPRESS场名称
# 输入选择帧，输出该帧输出场中，包括CPRESS的所有输出场
# 有返回值
# 该函数可扩展，用于提取其他类似于CPRESS这种名不副实的场，但目前没有需求，不加更改（改的话，控制挑选key的名称就可以）
def cpress_detector(frame_chosen):
    cpress_list = []                                                        # 定义一个空list，用于构建结构，之后添加数据
    for key in frame_chosen.fieldOutputs.keys():                            # 这个frame_chosen.fieldOutputs的类型是个Repository，但似乎继承了字典的结构，所以用字典遍历
        if 'CPRESS' in key:                                                 # 判断这个字典的key中是否包含“CPRESS”字符串
            cpress_list.append(key)                                         # 有则加入list
    return cpress_list                                                      # 最后返回list，detector工作完毕
    # 函数定义完毕，注释完毕，测试完毕
    
    
# 函数data_extract_mointor，数据提取函数的控制端，用于控制三个数据提取函数
# 输入odb名称，分析步及帧数（默认帧数-1），部件名称，节点集名称，和提取数据类型（默认CPRESS，其他数据类型给出分支接口，但暂未实现）
# 调用cpress_detector()和data_extract_kernel()
# 输出节点数值字典，但无序，还需另外一个函数实现数据提取和数据输入顺序相同
# 该函数亦可扩展，用于提取出CPRESS外的其他场，当前特化为CPRESS，为赶进度，暂不完整，略有可惜
def data_extract_mointor(odb_name, step_name, part_name, set_name, frame_serial_number = -1, data_type = 'CPRESS'):
    odb_file = openOdb(path = odb_name)                                     # 打开Odb文件
    frame_chosen = odb_file.steps[step_name].frames[frame_serial_number]    # 定义输出帧
    instance_name = part_name + '-1'                                        # GUI输入为part_name,所以这里需要将part_name转变为instance_name
    output_dict = {}                                                        # 定义空字典，用于构建结构
    # prettyPrint(frame_chosen.fieldOutputs)                                # 调试用，该句用于了解可输出变量
    if data_type == 'CPRESS':                                               # 如果提取场变量名为’CPRESS‘
        cpress_list = cpress_detector(frame_chosen)                         # 则调用detector获取所有CPRESS场
        for cpress_name in cpress_list:                                     # 对上述获取的所有CPRESS场进行遍历，每个场均执行一次data_extract_kernel()
            output_dict = data_extract_kernel(odb_file, frame_chosen, instance_name, set_name, output_dict, data_type = cpress_name)   
    elif data_type == 'U':
        output_dict = data_extract_kernel(odb_file, frame_chosen, instance_name, set_name, output_dict, data_type)
    else:
        pass                                                                # 这个else是用于扩展接口的，以后可以用于提取其他的场数据
    odb_file.close()                                                        # 提取数据后，释放内存
    return output_dict                                                      # 返回该字典，以节点label为key，节点值为键值
    # 函数定义完毕，注释完毕，测试完毕
    

# 函数data_extract_kernel，用于提取数据，需依附于monitor函数
# 输入odb名称，提取帧，instance名称，节点集名称，输出字典，提取数据类型
# 输出节点数据字典，字典以节点label为key，以value为键值
# 有返回值
# 这里面的output_dict是复用的，用于实现多场叠加
# 这种提取吧，它有个问题，就是它自动升序排序，你之前费劲心思保留的顺序没了
# 为了解决这个问题，当前方法是利用字典先存储 节点和查询值的对应数据, 再根据有序列表挨个查询获得有序的查询值
# 但这又是另一个函数了
def data_extract_kernel(odb_file, frame_chosen, instance_name, set_name, output_dict, data_type):   # 发现为啥不能实现有序输出了，因为abaqus中的节点集是无序的
    output_field = frame_chosen.fieldOutputs[data_type]                                             # 定义输出帧中的输出场类型
    output_node_set = odb_file.rootAssembly.instances[instance_name.upper()].nodeSets[set_name.upper()]     # 设定输出节点集，如果建立set在instance上，就把instance那一块删掉就行
    output_data = output_field.getSubset(region = output_node_set)                                  # 获取输出场中的输出点集的所有值
    for value in output_data.values:                                                                # 对所有的节点值遍历
        if value.nodeLabel in output_dict.keys():                                                   # 如果output_dict中有这个key，则将其对应值加和
            output_dict[value.nodeLabel] += value.data                                              # 如果没有这个key，则添加该key和其对应值
        else:
            output_dict[value.nodeLabel] = value.data
    # prettyPrint(output_data.values[1])
    return output_dict                                                                              # 最后返回这个dict
    # 函数定义完毕，注释完毕，测试完毕


# Surface集合构建逻辑说明
# 原本也是以为很简单的，但是发现根本没有根据节点确定surf，surf是根据element确定的
# 然后发现节点确定的element还要确定是哪个face，但face顺序根本没有规律
# 但总之解决该问题了
# 解决问题的整体思路是：
# 利用node_nearby_elements提取给定node附近的element
# 利用nodes_to_element对比不同node附近的element，确定两个node之间的那个element序号
# 利用surface_set将给定节点连线上的element边建立为surf集
# 上述三个函数均以surface_sets_monitor函数调用，即操作者仅用调用该函数
# 为实现该功能一共用了四个函数


# 函数node_nearby_element，用于提取node附近的element
# 输入模型名，实例名和节点集名
# 输出字典，字典以节点label为key，以node附近的element为值
# 感谢CSDN@奶茶也青春提供思路
def node_nearby_elements(model_name, instance_name, set_name):
    node_elements = {}                                                      # 定义空字典，用于构建架构
    for node in mdb.models[model_name].rootAssembly.instances[instance_name].sets[set_name].nodes:  # 遍历节点集合中的所有节点
        temp_seq=[]                                                         # 构建临时序列，用于记录临时element数据
        for element in node.getElements():                                  # 将node附近的所有element均加入temp_seq列表
            temp_seq.append(element.label)
        node_elements[node.label]=temp_seq                                  # 在字典中添加键值对
    return node_elements
    # 函数定义完毕，注释完毕，测试完毕


# 函数nodes_to_element，用于按顺序提取两个node之间对应的element
# 输入node_nearby_element中的提取结果字典，和有序node_list
# 输出字典，以node为key，以当前node和下一个node之间的element编号为键值
# 太惨了，居然有这么一步，做之前根本没想到，以为指定node就可以了
def nodes_to_element(node_elements, node_list):
    nodes_element = collections.OrderedDict()                               # 构建空有序字典
    for node in node_list:                                                  # 对有序node_list中的节点进行遍历
        node_current = node                                                 # 定义当前node
        if node_current == node_list[-1]:                                   # 若当前node为node_list中的最后node，则退出循环
            break   
        node_next = node_list[node_list.index(node) + 1]                    # 若不为，则继续运行，定义下一个index的node为node_next
        for element in node_elements[node_current]:                         # 遍历当前node对应的elements
            if element in node_elements[node_next]:                         # 如果当前node的element也在下一node的element中，则认为该element为重合element，计入有序字典
                nodes_current = (node_current , node_next)                  # 定义当前节点组，注意为元组型，不然无法成为key
                nodes_element[nodes_current] = element
    return nodes_element                                                    # 返回该有序字典
    # 函数定义完毕，注释完毕，测试完毕


# 函数surface_set，用于建立节点对应的表面集
# 输入模型名，实例名，element序号，element对应节点序号，和表面名称
# 无输出（直接建立节点集）
# element序号需要根据nodes_to_element确定
# 啊这，居然abaqus里面的surf是根据对应的element确定的，而不是用node_label确定，555
# 目测是只有外侧的element才有surface这个量，虽然你用代码也能实现内部表面，但那时候就很混乱 
# 我去不是外侧的有surface，而是它恰好几乎所有的都是face2Element都是外侧表面，把它改成face3就是另外的，但问题是不是所有的都恰好，啊
# 上面的这个问题通过循环遍历解决了
# 事实上并非按照1234的表面顺序进入分支，而是按照2413的顺序，这是发现最多的情况是2表面为所需表面，4次之，其他都没有出现过
# 但由于不能判断到底是哪个，所以只能建立后判断，不行再重复
def surface_set(model_name, instance_name, node_nums, element_num, surface_name):
    a = mdb.models[model_name].rootAssembly                                 # 指定model名称
    f1 = a.instances[instance_name].elements                                # 指定实例名称
    face_elements = f1[element_num - 1: element_num]                        # 指定建立surface对应element，发现要前-1，而不是后+1
    trial_time = 1                                                          # 由于不确定哪个面是我构建surf需要的面，所以做试错，初始化试错次数trial_time
    trial_flag = 1                                                          # 初始化试错标志trial_flag，认为只要flag == 1 就继续试错
    while trial_flag:                                                       # 使用while循环，只要flag为真，就一直循环
        if trial_time == 1:                                                 # 每次循环，试错次数trial_time 加一，则每次循环进入不同的分支，构建不同surf
            surf_current = a.Surface(face2Elements=face_elements, name=surface_name)                # 指定表面名称，在表面2建立surf
        elif trial_time == 2:
            surf_current = a.Surface(face4Elements=face_elements, name=surface_name)                # 指定表面名称，在表面4建立surf
        elif trial_time == 3:
            surf_current = a.Surface(face1Elements=face_elements, name=surface_name)                # 指定表面名称，在表面1建立surf
        elif trial_time == 4:
            surf_current = a.Surface(face3Elements=face_elements, name=surface_name)                # 指定表面名称，在表面4建立surf
        else:                                                                                       
            print('Surface Setting wrong. Check it at' + str(node_nums[0]) + 'and' + str(node_nums[1]))
            sys.exit()                                                      # 如果四次循环将四个面都试了一遍都没有满足条件，就直接退出程序
        for node in surf_current.nodes:                                     # 按理来讲不会出现这种情况，因为node和element都是对应的，但是这里要避免死循环
            if node.label in node_nums:                                     
                trial_flag *= 1                                             # 判断之前构建的surf对应的node是否与你希望的node相同
            else:
                trial_flag *= 0                                             # 只要有一个不同，则flag变为0
        trial_flag = 1 - trial_flag                                         # 将flag取非，则变为：只要有一个不同，则flag就是1，则循环会继续进行，除非所有都相同，flag变为0，循环结束
        trial_time += 1                                                     # 每次循环计数器加一，保证每次循环进入不同分支
    # 函数定义完毕，注释完毕，测试完毕


# 函数surface_sets_monitor，用于按照节点顺序构建对应节点边
# 输入模型名，部件名，节点集名称和节点有序list，以及之前提取出的cpressData
# 输出自建有序字典ordered_model_data，将所有node,element,surf，cpress信息有序联系储存
# 有输出
# n个节点对应n-1个边，对每个边分别建立对应的surf集
# 注意这里面的nodes和elements单复数均有含义
# nodes_element表示多个节点确定一个element，node_elements表示一个node对应的多个elements
def surface_sets_monitor(model_name, part_name, set_name, node_list, cpress_data):
    instance_name = part_name + '-1'                                            # 定义实例名称
    node_elements = node_nearby_elements(model_name, instance_name, set_name)   # 根据节点集，确定每个节点对应的elements
    nodes_element = nodes_to_element(node_elements, node_list)                  # 根据节点序列，获得两个连续节点对应的element，为有序字典
    surf_serial = 1                                                             # 定义surf序号
    ordered_model_data = {}                                                     # 想到了新方法搭建有序dict，用于储存所有node，element，cpress，surf数据并建立联系
    for node_nums in nodes_element.keys():                                      # 对有序字典nodesElement进行遍历
        element_num = nodes_element[node_nums]                                  # 确定字典key对应键值
        surface_name = 'AutoSurf-' + str(surf_serial) + ': ' + str(node_nums[0]) + '-' + str(node_nums[1])  # 确定自动构建的surf名称
        surface_set(model_name, instance_name, node_nums, element_num, surface_name)       # 调用函数建立surf
        # 构建surf之后，构建temp_dict用于将cpressData和nodes_element以及surf_name建立完全联系
        # 下面建立的temp_dict作为临时dict，在后面会成为key为顺序数值的键值，即为第key个数据组的键值
        # 其中，'node_first_num'为按顺序第一节点的label，'node_second_num'为按顺序第二节点的label
        # 'element_num' 为上面两个节点对应的element
        # 'node_first_cpress' 为第一个节点上的CPRESS，'node_second_cpress'为第二个节点上的CPRESS
        # 'surface_name'为第key个表面的名称
        # 'average_surf_pressure'为第key个表面上应该有的平均cpress
        temp_dict = {
            'node_first_num' : node_nums[0], 
            'node_second_num' : node_nums[1], 
            'element_num' : element_num,
            'node_first_cpress' : cpress_data[node_nums[0]],
            'node_second_cpress' : cpress_data[node_nums[1]],
            'surface_name' : surface_name, 
            'average_surf_pressure' : (cpress_data[node_nums[0]] + cpress_data[node_nums[1]]) / 2.0
            }
        ordered_model_data[surf_serial] = temp_dict                             # 以序号为key，以上面的联系为value，构建dict，实现储存无序，但调用有序
        surf_serial += 1                                                        # surf序号加1，加入序号目的是为了保证即使节点序号无序，显示的surf阵列也是有序的
    return ordered_model_data               
    # 函数定义完毕，注释完毕，测试完毕
    # 仔细想来，这里面的ordered_model_data应该从最初就开始建立的，每一步增加一点东西，也不用每个函数的调用参数那么多了
    # 仔细想来，那么其他的模型参数也可以这样实现，构建一个大的dict，每一步都增加dict
    # 嗯，这大概意思是在大型脚本里面的信息流和数据流要从最初开始构建
    # 从这一步构建倒没问题，主要是脚本的简洁性就差了很多
 
    
# 函数step_establish，用于建立分析步
# 输入模型名，新建分析步名，前一分析步名，最大增量步数，初始增量步长
# 无输出（直接建立分析步）
def step_establish(model_name, auto_step_name, previous_step_name, max_increasements_num, initial_increment):
    mdb.models[model_name].StaticStep(name=auto_step_name, previous=previous_step_name, maxNumInc=max_increasements_num, initialInc=initial_increment)
    # 建立分析步的函数内容就一句话，所以也没什么需要解释的
    # 函数定义完毕，注释完毕，测试完毕


# 函数node_set_freeze，用于约束给定的节点集的y方向位移，之后可以选择改位移约束条件，不过目前没有这个需求
# 输入模型名，部件名，节点集名，边界条件名和创建该边界条件的分析步名
# 无输出（直接建立边界条件）
# 该代码全部从pythonReader中抄出来，除了变量名基本没有改动，因此不加注释，基本能看懂
# 这个函数经历了修正，解释一下
# 我们需要的是将node约束在当前位置，而不是约束在0（0为初始位置），对比了下，发现这个通过加入fixed=ON那句话就可以实现
def node_set_freeze(model_name, part_name, set_name, boundary_name, create_step_name):
    instance_name = part_name + '-1'
    a = mdb.models[model_name].rootAssembly
    region = a.instances[instance_name].sets[set_name]
    mdb.models[model_name].DisplacementBC(name=boundary_name, createStepName=create_step_name, 
        region=region, u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET, fixed=ON,
        distributionType=UNIFORM, fieldName='', localCsys=None)
    # 函数定义完毕，注释完毕，测试完毕


# 函数surface_pressure_load，用于在单个surface上施加均布载荷
# 输入模型名，表面名，载荷名，建立载荷分析步，均布载荷大小
# 没有输出，直接建立载荷，注意建立载荷是在原有没有的基础上建立
# 主要为abaqus内部代码，基本可理解，不进行过多解释
def surface_pressure_load(model_name, surface_name, load_name, create_step_name, load_magnitude):
    a = mdb.models[model_name].rootAssembly
    region = a.surfaces[surface_name]
    mdb.models[model_name].Pressure(name=load_name, createStepName=create_step_name, 
        region=region, distributionType=UNIFORM, field='', magnitude=load_magnitude, 
        amplitude=UNSET)
    # 函数定义完毕，测试完毕
    

# 函数surface_load_monitor，用于一次性批量施加载荷（就是指等效轴接触压力），如果要对单个表面施加载荷，直接用surface_pressure_load
# 调用surface_pressure_load，实现在node_data_dict中的所有surface上施加对应大小的载荷
# 输入模型名，施加载荷的分析步，全部数据dict：node_data_dict
# 无输出，直接批量建立载荷
def surface_load_monitor(model_name, step_name, node_data_dict):
    for i in range(len(node_data_dict)):                                    # 对node_data_dict里面的内容遍历
        serial_num = i + 1                                                  # 按照key，事实上就是123456的顺序
        surface_name = node_data_dict[serial_num]['surface_name']           # 将node_data_dict中的内容转化出来，下同
        node_first_num = node_data_dict[serial_num]['node_first_num']
        node_second_num = node_data_dict[serial_num]['node_second_num']
        load_magnitude = node_data_dict[serial_num]['average_surf_pressure']
        load_name = 'AutoLoadEquivalent-' + str(serial_num) + ' : ' + str(node_first_num) + '-' + str(node_second_num)    # 定义载荷名称
        surface_pressure_load(model_name, surface_name, load_name, step_name, load_magnitude)   # 循环施加载荷
    # 函数定义完毕，注释完毕，测试完毕


# 函数axis_move，实现改变轴的位置，事实上就是修改一个边界条件
# 输入模型名，边界条件名，修改边界条件发生的分析步，以及默认将位移改到0.0
# 无输出，直接修改边界条件
# 代码简单，基于abaqus内部函数，无注释
def axis_move(model_name, boundary_name, change_step_name, loacation = 0.0):
    mdb.models[model_name].boundaryConditions[boundary_name].setValuesInStep(stepName=change_step_name, u1=loacation)
    # 函数定义完毕，测试完毕


# 函数matrix_dict_initialize，用于初始化影响系数矩阵储存的字典
# 输入模型名，cpu数，提取该初始位置数据的分析步，提取数据的部件名，节点集名，和有序节点列表
# 输出初始化后的矩阵字典，该字典以节点的顺序为key，以内部字典为value
# 内部字典包括：节点编号，节点U值列表，和节点影响系数列表
# 有返回值
# 该函数内部包括了一个作业提交步
def matrix_dict_initialize(model_name, cpu_num, step_name, part_name, set_name, node_list, submit = True):
    job_name = 'AutoJob-0-Initial_Position'                                           # 定义初始位置作业名称
    if submit:
        job_submit(model_name, job_name, cpu_num)                                       # 提交初始位置作业，同样，加一个判断是用于代码调试
    odb_name = job_name + '.odb'
    original_displacement = data_extract_mointor(odb_name, step_name, part_name, set_name, data_type = 'U')     # 从提交的初始位置作业中提取所有node_set中的节点位移数据
    cof_matrix = {}
    for node in node_list:                                                          # 对节点位移数据进行遍历，并按照node_list中的节点顺序进行初始化dict
        serial_num = node_list.index(node) + 1                                      # 获得序号
        u = original_displacement[node]                                             # 提取位移量，但当前位移量包括x和y方向的两个位移
        # 创建内层字典，包括节点序号，节点x方向位移和节点影响系数矩阵
        temp_dict = {
            'nodeLabel' : node,
            'nodeUList' : [u[0]],
            'nodeInfCof' : []
        }
        # 以节点顺序为key，内层字典为value，创建cof_matrix字典，并返回cof_matrix
        cof_matrix[serial_num] = temp_dict
    return cof_matrix
    # 函数定义完毕，注释完毕，测试完毕


# 函数unit_load_creator，用于批量创建单位载荷，但这些单位载荷创建后即被抑制，供之后启用
# 输入模型名，载荷创建分析步，nodeDataDict，和载荷大小
# 函数直接创建并抑制所有单位载荷，输出更新后的nodeDataDict
# 有输出
def unit_load_creator(model_name, create_step_name, node_data_dict, load_magnitude):
    for key in node_data_dict:                                                  # 对每个node_data_dict中的值进行遍历
        database = node_data_dict[key]                                          # 获取当前key中的内层字典当做当前数据库
        surface_name = database['surface_name']                                 # 获取表面名称
        node_first = database['node_first_num']                                 # 获取第一节点label
        node_second = database['node_second_num']                               # 获取第二节点label
        load_name = 'AutoUnitLoad' + str(key) + ' : ' + str(node_first) + '-' + str(node_second)        # 定义单位载荷名称
        surface_pressure_load(model_name, surface_name, load_name, create_step_name, load_magnitude)    # 创建单位载荷
        node_data_dict[key]['UnitLoadName'] = load_name                                                 # 将单位载荷名称加入node_data_dict
        mdb.models[model_name].loads[load_name].suppress()                      # 抑制本次循环中创建的单位载荷
        # 每个表面上的单位载荷都已设定，但同时已抑制
    return node_data_dict                                                       # 返回更新后的node_data_dict
    # 函数定义完毕，注释完毕，测试完毕


# 函数influence_coefficient_matrix_builder，用于在影响系数矩阵初始化建立后，批量提交并提取数据，获得完整影响系数矩阵
# 输入模型名，cpu数，数据提取分析步名，部件名，初始化的影响系数矩阵，节点集名，节点数据库名，载荷大小，默认启动计算
# 输出构建完成的影响系数矩阵，该矩阵中不仅包括影响系数矩阵，还包括对应的节点和位移矩阵
# 有输出
def influence_coefficient_matrix_builder(model_name, cpu_num, extract_data_step_name, part_name, cof_matrix, set_name, node_data_dict, load_magnitude = 0.05, submit = True):
    # 建立单位载荷后，开始遍历所有节点施加载荷，提交作业，并提取结果导入cof_matrix中
    for key in node_data_dict:                                          # 遍历所有的节点数据库（事实上为表面或单元数据库）
        if key == len(node_data_dict):                                  # 如果上面的数据库遍历到了最后一个，就不再进行之后的内容
            break                                                       # 即，有n个节点，加上两侧一共n+2个节点，对应n+1个表面，n+1个表面按顺序两个一组施加载荷，对应n次载荷，n阶矩阵
        database_current = node_data_dict[key]                          # 获取当前数据库
        database_next = node_data_dict[key + 1]                         # 获取下一数据库
        unit_load_current = database_current['UnitLoadName']            # 获取载荷1的载荷名
        unit_load_next = database_next['UnitLoadName']                  # 获取载荷2的载荷名
        mdb.models[model_name].loads[unit_load_current].resume()        # 将之前批量定义的载荷，按顺序找到两个启动一下
        mdb.models[model_name].loads[unit_load_next].resume()
        node_first = database_current['node_first_num']                 # 找到node名称，用于job命名
        node_second = database_current['node_second_num']
        job_name = 'AutoJob-' + str(key) + '-' + 'UnitLoad-OnNode-' + str(node_second) 
        if submit:
            job_submit(model_name, job_name, cpu_num)                   # 提交初始位置作业，同样，加一个判断是用于调试
        odb_name = job_name + '.odb'
        displacement_data = data_extract_mointor(odb_name, extract_data_step_name, part_name, set_name, data_type = 'U')     # 从提交的初始位置作业中提取所有node_set中的节点位移数据
        for key in cof_matrix:                                          # 在本次job提交并结束后，开始批量提取数据，对每个影响系数矩阵中的节点进行遍历
            database_current = cof_matrix[key]                          # 重新定义当前数据库，将当前节点中的二层字典提取出来
            node_label = database_current['nodeLabel']                  # 同样地获取当前节点序号
            u = displacement_data[node_label]
            cof_matrix[key]['nodeUList'].append(u[0])                   # 在影响系数矩阵dict中提取出来的位移量和差值，加入影响系数矩阵中
            node_difference = u[0] - cof_matrix[key]['nodeUList'][0]    
            cof_matrix[key]['nodeInfCof'].append(node_difference)
        mdb.models[model_name].loads[unit_load_current].suppress()      # 提取完数据后，将之前启动的载荷再去掉
        mdb.models[model_name].loads[unit_load_next].suppress()
    return cof_matrix                                                   # 所有更新后，返回更新后的影响系数矩阵
    # 函数定义完毕，注释完毕，测试完毕


# 函数data_output_to_csv，将程序结果写入csv文件
# 输入matrix，默认打开文件
# 输出文件路径，但目前未调用
# 有返回值
# 该输出结果每一行为对应节点在不同载荷下的x位移变化量，每一列为在对应节点施加载荷不同节点的位移变化量
def data_output_to_csv(matrix_dict, file_open = True):
    first_row = ['UnitLoad On']                             # 初始化第一行内容
    file_name = 'dataOutput.csv'                            # 定义文件名
    f = open(file_name, 'wb+')                              # 打开文件，‘wb’为无间隔行类型二进制文件
    csv_writer = csv.writer(f)
    for key in matrix_dict:                                 # 首先遍历一遍将第一行内容完善，最后写入第一行
        if key == 1 or key == len(matrix_dict):             # 遍历中第一个和最后一个node跳过，因为事实上只需要中间的，两边端点的仅用于计算
            continue
        first_row.append(matrix_dict[key]['nodeLabel'])
    csv_writer.writerow(first_row)   
    csv_writer.writerow(['NodeLabel'])                      # 第二行内容表明下面都是nodelabel
    for key in matrix_dict:                                 # 再遍历一遍，写入内容
        if key == 1 or key == len(matrix_dict):
            continue
        database_current = matrix_dict[key]
        node_label = database_current['nodeLabel']
        node_inf_cof = database_current['nodeInfCof']
        node_inf_cof.insert(0, node_label)
        csv_writer.writerow(node_inf_cof)
    f.close()
    current_dir = os.getcwd()
    file_path = current_dir + '\\' + file_name
    if file_open:                                           # 默认打开文件
        os.startfile(file_path)
    return file_path
    # 函数定义完毕，注释完毕，测试完毕


# 函数定义区结束
#############################################################################################################################
#############################################################################################################################
# 程序控制区开始


# 主程序
def main_f(modelName, modelName2, modelName3, nodeInput, partName, cpuNum, currentStepName, boundaryName, loadMagnitude, submit = False):
    nodeList = node_input_to_node_list(nodeInput)                       # 文本格式化节点序列转化为list格式，命名为nodeList
    setName = 'Node_Total'                                              # 定义节点集合名称
    node_list_to_node_set(modelName, partName, nodeList, setName)       # 构建abaqus中的节点集，但构建节点集结果会丧失顺序性
    # 节点集构建完毕
    # 这个节点集在Part模块可见
    
    # 初始提交一次作业，用于提取初始CPRESS
    jobName = 'AutoJob-0-Original'                                      # 初始提交作业名称
    if submit:
        job_submit(modelName, jobName, cpuNum)                          # 提交初始作业,加一个判断是调试代码用，调试代码时提交作业耗时较大，因此不会每次都提交作业
    # 初始作业步完成

    # 提取初始作业步的CPRESS
    odbName = jobName + '.odb'                                          # 定义初始作业odb库名称
    dataType = 'CPRESS'                                                 # 设定提取类型
    cpressData = data_extract_mointor(odbName, currentStepName, partName, setName, frame_serial_number = -1, data_type = dataType)     # 提取CPRESS
    # 初始作业步CPRESS提取完毕
    
    # n个节点对应n-1个边，对每个边分别建立对应的surf集
    nodeDataDict = surface_sets_monitor(modelName, partName, setName, nodeList, cpressData)        # 调用monitor函数建立surf集，返回当前的所有数据dict
    # surf集建立完毕
    # 这个surf集在Step模块之后均可见
    
    # 构建脚本分析步1，该分析步用于约束所有节点在当前Y坐标（其他自由度不约束）
    # 建立脚本分析步1
    autoStepFirstName = 'AutoStep-First : Node Constraints'                                # 定义脚本分析步一名称
    previousStepName = currentStepName                                  # 定义建立脚本分析步一的前一分析步，目前认为该前一分析步就是当前分析步（推荐为最后分析步）
    maxIncNum = 10000                                                   # 定义脚本分析步最大分析步数
    initInc = 0.01                                                      # 定义脚本分析步初始分析步长，这两个就固定这么大了，反正大了只会影响时间，小了则可能不收敛
    step_establish(modelName, autoStepFirstName, previousStepName, maxIncNum, initInc)   # 建立该脚本分析步一
    # 脚本分析步1建立完毕
    # 约束边界node的Y方向位移，保证其y方向一直为当前
    BoundaryName = 'BC-Node_Total_Freeze'                                          # 定义该约束名称
    node_set_freeze(modelName, partName, setName, BoundaryName, autoStepFirstName) # 在脚本分析步1中，实现位移约束
    # 位移约束给定
    # 脚本分析步1内容完成
    
    # 建立脚本分析步2，该分析步用于施加等效载荷
    # 建立脚本分析步2
    autoStepSecondName = 'AutoStep-Second : Equivalent Load'                                                  # 定义脚本分析步2名称
    step_establish(modelName, autoStepSecondName, autoStepFirstName, maxIncNum, initInc)    # 在脚本分析步1后，建立脚本分析步2
    # 脚本分析步2建立完毕
    # 施加等效接触载荷
    surface_load_monitor(modelName, autoStepSecondName, nodeDataDict)
    # 等效接触载荷批量建立完毕
    # 脚本分析步2内容完成

    # 建立脚本分析步3，该分析步用于实现移轴操作
    # 建立脚本分析步3
    autoStepThirdName = 'AutoStep-Third : Axis Move'                                                    # 定义脚本分析步3名称
    step_establish(modelName, autoStepThirdName, autoStepSecondName, maxIncNum, initInc)    # 在脚本分析步2后，建立脚本分析步3
    # 脚本分析步3建立完毕
    # 修改约束内容以实现移轴
    axis_move(modelName, boundaryName, autoStepThirdName)              # 设定修改发生在脚本分析步3，默认直接将对应约束的x位移改为0，只用告知其他参数即可
    # 移轴操作完毕
    # 脚本分析步3内容完成
    
    # 脚本分析步3完成后，初始化影响系数矩阵，其中包括一个作业提交，用于获取initial position，作业提交包括在了初始化程序中
    matrixDict = matrix_dict_initialize(modelName, cpuNum, autoStepThirdName, partName, setName, nodeList, submit = submit)    # 调用函数初始化matrix_dict
    # 影响系数矩阵初始化完毕
    
    # 构建脚本分析步4，该分析步中，批量施加单位载荷并构建完整的影响系数矩阵
    autoStepFourthName = 'AutoStep-Fourth : Unit Load'                                      # 定义脚本分析步4名称
    step_establish(modelName, autoStepFourthName, autoStepThirdName, maxIncNum, initInc)    # 在脚本分析步3后，建立脚本分析步4
    # 脚本分析步4建立完毕
    # 构建单位载荷，构建过程中，对每个单位载荷都抑制一下
    createStepName = autoStepFourthName                                                     # 定义构建单位载荷的分析步为脚本分析步4
    nodeDataDict = unit_load_creator(modelName, createStepName, nodeDataDict, load_magnitude = loadMagnitude)   # 调用函数将单位载荷构建出来，并更新nodeDataDict
    # 单位载荷构建完毕，尚未启用
    # 利用初始化完毕的影响系数矩阵，批量处理，实现构建完整的影响系数矩阵
    matrixDict = influence_coefficient_matrix_builder(modelName, cpuNum, autoStepFourthName, partName, matrixDict, setName, nodeDataDict, loadMagnitude, submit = submit)
    # 影响系数矩阵构建完毕   
    
    # 调用函数，将影响系数矩阵写入文件，默认打开文件
    data_output_to_csv(matrixDict, file_open = True)
    
    print('Script finished\n\n')                                      # 输出脚本完成，并加入几行空行用于和之后内容区分


# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

# modelName = 'Model-1'                                               # 输入模型名，一般默认就是这个
# nodeInput = "35,6,7,36,8,37,10,38"                                  # 输入所需节点序列（文本格式），可以为开始:结束:间隔 或是 开始:结束 或是 节点 三种格式，以英文逗号和冒号分隔，不然报错
# partName = 'O'                                                      # 输入研究part名称，注意不是实例instance
# cpuNum = 8                                                          # 输入提交作业CPU数
# currentStepName = 'Step-PP'                                         # 输入没有影响系数矩阵时的最后一个step名称，应该是最后一个分析步名称
# boundaryName = 'BC-1'                                               # 指定需要修改的边界条件名称，指你之前移轴操作中定义的那个边界条件的名字，注意以文本格式输入
# loadMagnitude = 0.05                                                # 输入单位载荷大小，当前为0.05（均布载荷0.05MPa）


# modelName2 = modelName
# modelName3 = modelName
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA


# main_f(modelName, modelName2, modelName3, nodeInput, partName, cpuNum, currentStepName, boundaryName, loadMagnitude, submit = True)

# execfile('F:/Desktop/Influence_Coffience_Matrix/Displacement_Matrix_Builder_kernelV4.py',__main__.__dict__)
# todo 加入功能，识别是否有AutoJob-Original，不然可能直接执行会费很久有问题无法修正，可以加入一个选项用于check但不执行
# todo 加入功能，自动识别接触区域
# todo 说不定可以写一个时间计算，不过用处不大

# "37,6,38,7,39,8,40,9"
# 程序控制区结束
#############################################################################################################################
