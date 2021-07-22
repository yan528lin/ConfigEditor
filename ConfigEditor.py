#!/usr/local/bin/python3

import os
import sys
import csv
import json
import hashlib
import subprocess

COMMAND_FORMAT = """
    配置文件必须放在./CSV/config 或者 ./CSV/cms下
    如果要修改国内版的配置，必须同目录下存在 CsvEncrypt.py 文件
    脚本命令格式：
    1.终端命令单条配置修改
    ./ConfigEditor.py  filename  config_name  alter_position  alter_list
    alter_position 与 alter_list 要修改多个值时，值之间用逗号隔开，修改内容要数量一致
    alter_position 的序号从1开始
    例如：./ConfigEditor.py  config_game.csv  data_es_switch  3,4  F,es的开关
    国内项目需要在命令末尾添加d，注意一定要在配置文件加密的情况下使用
    例如：./ConfigEditor.py  config_game.csv  data_es_switch  3,4  F,es的开关 d
    2.通过文件进行1条以上的配置修改及添加
    ./ConfigEditor.py  filename  filename2
    例如：./ConfigEditor.py  config_game.csv  tmp.csv
    国内项目同样需要末尾添加d
    3.仅修改md5值
    ./ConfigEditor.py config_index.json
    or ./ConfigEditor.py cms_index.json
    暂不支持加密的配置文件
    """


class ConfigEditor(object):
    __config_dir_name = "./CSV/config/"
    __config_file_name = "config_game.csv"
    __config_item_name = ""
    __config_alter_position_list = []
    __alter_content_list = []
    __index_name = "config_index.json"

    def set_config_dir_name(self, new_config_dir_name):
        self.__config_dir_name = new_config_dir_name

    def set_config_file_name(self, new_config_file_name):
        self.__config_file_name = new_config_file_name

    def set_config_item_name(self, new_config_item_name):
        self.__config_item_name = new_config_item_name

    def set_config_alter_position(self, new_config_alter_position_list):
        self.__config_alter_position_list = new_config_alter_position_list

    def set_alter_content(self, new_alter_content_list):
        self.__alter_content_list = new_alter_content_list

    def set_index_name(self, new_index_name):
        self.__index_name = new_index_name

    def get_config_file_md5(self):
        with open(self.__config_dir_name + self.__config_file_name, "rb") as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
        return md5obj.hexdigest()

    def auto_add_index_num(self) -> bool:
        """
        尝试自动更新md5值与配置版本号
        :return:True修改成功，False修改失败
        """
        try:
            with open(self.__config_dir_name + self.__index_name, "r", encoding="utf-8") as f:
                index_data = json.load(f)
                try:
                    # 修改配置文件的md5值
                    index_data["Resource"][self.__config_file_name]["md5"] = self.get_config_file_md5()
                    print("成功修改版本号与md5值")
                    index_data["Data"]["version"] += 1
                    index_num = index_data["Data"]["version"]
                    print("版本号为：" + str(index_num))
                except KeyError:
                    print("修改版本号与md5值失败，请手动设置")
                    return False

            with open(self.__config_dir_name + self.__index_name, "w", encoding="utf-8") as f:
                json.dump(index_data, f, indent=4, separators=(',', ':'))
                return True
        except FileNotFoundError:
            print("版本文件没有找到，请添加版本文件！")
            return False

    def alter_config_file_md5(self):
        """
        只更新md5值
        :return:True修改成功，False修改失败
        """
        try:
            with open(self.__config_dir_name + self.__index_name, "r", encoding="utf-8") as f:
                index_data = json.load(f)
                for root, dirs, files in os.walk(self.__config_dir_name, topdown=False):
                    for name in files:
                        # index文件跳过
                        if "index.json" in name:
                            continue

                        try:
                            with open(os.path.join(root, name), "rb") as rfp:
                                file_md5 = hashlib.md5(rfp.read()).hexdigest()
                            index_data["Resource"][name]["md5"] = file_md5

                        except KeyError:
                            print(f"{name}没有在{self.__index_name}中找到！")

            with open(self.__config_dir_name + self.__index_name, "w", encoding="utf-8") as f:
                json.dump(index_data, f, indent=4, separators=(',', ':'))

            print(f"已更新{self.__config_dir_name}目录下所有配置文件的md5值！")
            return True

        except FileNotFoundError:
            print(f"没有找到{self.__index_name}，请查看配置目录！")
            return False

    # test parameter：config_game.csv data_es_switch 3,4 T,es
    def alter_config_content_by_command(self) -> bool:
        """
        通过类中已经设定好的元素完成配置项的修改
        :return:True修改成功，False修改失败
        """
        if len(self.__alter_content_list) != len(self.__config_alter_position_list):
            print("修改配置项数量与位置数量不等，请重试！")
            return False

        is_changed = False
        try:
            with open(self.__config_dir_name + self.__config_file_name, "r", encoding="utf-8") as rfp:
                with open("tmp_config", "w", encoding="utf-8") as wfp:
                    csv_reader = csv.DictReader(rfp)
                    key_list = csv_reader.fieldnames

                    csv_writer = csv.DictWriter(wfp, fieldnames=key_list)
                    csv_writer.writeheader()

                    for line in csv_reader:
                        if line[key_list[0]] == self.__config_item_name:
                            i = 0
                            for pos in self.__config_alter_position_list:
                                if pos > len(key_list) or pos <= 0:  # 修改配置项位置出错
                                    print("修改配置项的位置出错，请重试！")
                                    subprocess.run(["rm", "tmp_config"])
                                    return False

                                line[key_list[pos - 1]] = self.__alter_content_list[i]  # 更改配置新值
                                i += 1
                                is_changed = True
                                # print("已修改配置项：" + line[key_list[0]])

                        csv_writer.writerow(line)

            if is_changed:
                subprocess.run("mv tmp_config " + self.__config_dir_name + self.__config_file_name, shell=True)
                print("已修改配置如下：")
                subprocess.run("cat " + self.__config_dir_name + self.__config_file_name + " |grep " +
                               self.__config_item_name, shell=True)
                return True

            print("没有找到" + self.__config_item_name + "，请查看拼写，或者使用文件修改功能来增加此配置项")

        except FileNotFoundError:
            print("没有找到" + self.__config_file_name + "，请查看拼写")

        return False

    # test parameter：config_test.csv test_config2.csv
    def alter_config_content_by_file(self, my_file) -> bool:
        """
        通过文件来修改配置文件中的项目，可以一次性修改多条配置，可以新增加配置项
        :param my_file: 用于修改配置的临时文件名，string
        :return:True修改成功，False修改失败
        """
        try:
            with open(my_file, "r", encoding="utf-8") as my_fp:
                csv_my_reader = csv.DictReader(my_fp)
                key_my_list = csv_my_reader.fieldnames

                # 比较修改文件的每一行，找到该项则替换，没找到则增加一行
                for my_line in csv_my_reader:
                    try:
                        with open(self.__config_dir_name + self.__config_file_name, "r", encoding="utf-8") as rfp:
                            csv_reader = csv.DictReader(rfp)
                            key_list = csv_reader.fieldnames

                            if key_list != key_my_list:
                                print("两个文件的标题行不同，请检查文件")
                                return False

                            with open("tmp_config", "w", encoding="utf-8") as wfp:
                                csv_writer = csv.DictWriter(wfp, fieldnames=key_list)
                                csv_writer.writeheader()

                                is_found = False
                                for line in csv_reader:
                                    if line[key_list[0]] == my_line[key_list[0]]:
                                        is_found = True
                                        csv_writer.writerow(my_line)
                                        print("已修改配置项：" + my_line[key_list[0]])
                                        continue

                                    csv_writer.writerow(line)

                                # 原文件没有找到配置项，则新添加一行
                                if not is_found:
                                    csv_writer.writerow(my_line)
                                    print("已添加配置项：" + my_line[key_list[0]])

                        subprocess.run("mv tmp_config " + self.__config_dir_name + self.__config_file_name, shell=True)

                    except FileNotFoundError:
                        print("没有找到" + self.__config_file_name + "，请查看拼写")
            return True
        except FileNotFoundError:
            print("没有找到" + my_file + "，请查看拼写")
        return False

    def find_config_by_name(self):
        """
        通过配置项的全名找到配置文件中的那一行
        :return: 成功返回这条配置项的一整行，失败返回空
        """
        try:
            with open(self.__config_dir_name + self.__config_file_name, "r", encoding="utf-8") as rfp:
                csv_reader = csv.DictReader(rfp)
                key_list = csv_reader.fieldnames

                for line in csv_reader:
                    if line[key_list[0]] == self.__config_item_name:
                        return str(line)
        except FileNotFoundError:
            print("文件没有找到！")
            return []
        print("配置项没有找到！")
        return []


def parse_command_parameter() -> bool:
    """
    解析命令，调用参数修改配置的方法
    :return:True修改成功，False修改失败
    """
    ce = ConfigEditor()
    ce.set_config_file_name(sys.argv[1])
    file_first_name = sys.argv[1].split("_")[0]
    if file_first_name != "config":
        if file_first_name == "cms":
            ce.set_index_name("cms_index.json")
            ce.set_config_dir_name("./CSV/cms/")
        else:
            print("修改文件的格式有误，请查看！")
            return False

    config_name = sys.argv[2]
    str_pos = sys.argv[3]
    str_alter = sys.argv[4]

    ce.set_config_item_name(config_name)

    try:
        ce.set_config_alter_position(list(map(int, str_pos.split(","))))
    except ValueError:
        print("请输入正确的config_alter_position_list！")
        return False
    ce.set_alter_content(str_alter.split(","))

    if ce.alter_config_content_by_command():    # 修改配置成功，尝试自动增加版本号
        ce.auto_add_index_num()
    return True


def parse_file_parameter() -> bool:
    """
    解析命令，调用文件修改配置的方法
    :return:True修改成功，False修改失败
    """
    ce = ConfigEditor()
    ce.set_config_file_name(sys.argv[1])
    file_first_name = sys.argv[1].split("_")[0]
    if file_first_name != "config":
        if file_first_name == "cms":
            ce.set_index_name("cms_index.json")
            ce.set_config_dir_name("./CSV/cms/")
        else:
            print("修改文件的名字有误，请查看！")
            return False

    if ce.alter_config_content_by_file(sys.argv[2]):
        ce.auto_add_index_num()
    return True


def parse_command_parameter_domestic():
    if sys.argv[5] == "d":
        subprocess.run("python3 ./CsvEncrypt.py decrypt", shell=True)
        parse_command_parameter()
        subprocess.run("python3 ./CsvEncrypt.py", shell=True)
    else:
        default_print()


def parse_file_parameter_domestic():
    if sys.argv[3] == "d":
        subprocess.run("python3 ./CsvEncrypt.py decrypt", shell=True)
        parse_file_parameter()
        subprocess.run("python3 ./CsvEncrypt.py", shell=True)
    else:
        default_print()


def parse_alter_md5_parameter():
    ce = ConfigEditor()
    if sys.argv[1] != "config_index.json":
        if sys.argv[1] == "cms_index.json":
            ce.set_index_name("cms_index.json")
            ce.set_config_dir_name("./CSV/cms/")
        else:
            print("修改文件的名字有误，请查看！")
            return False
    ce.alter_config_file_md5()


def default_print():
    print(COMMAND_FORMAT)


if __name__ == "__main__":
    len_sys = len(sys.argv)
    dic_actions = {2: parse_alter_md5_parameter,
                   3: parse_file_parameter,
                   4: parse_file_parameter_domestic,
                   5: parse_command_parameter,
                   6: parse_command_parameter_domestic}

    dic_actions.get(len_sys, default_print)()