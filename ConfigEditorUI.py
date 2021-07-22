import tkinter
import os
import ast
import csv
import ConfigEditor
from ConfigEditor import ConfigEditor
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

select_project = []
select_version = []
select_file = []
select_config = []

class ProjectChooser(object):
    def __init__(self):
        self.root = Tk()
        # 500后面的是小写X
        self.root.geometry("600x250+200+200")
        self.root.title("配置编辑器")
        self.set_main_window()

        self.root.mainloop()

    def set_main_window(self):
        top_frame = Frame(self.root)
        bottom_frame = Frame(self.root)
        top_frame.pack(side=TOP, ipady=30)
        bottom_frame.pack()

        # 选择项目的label
        tips_label = Label(top_frame, text="请选择项目：")
        tips_label.pack(side=LEFT)

        # 选择项目的下拉框
        project_list = tkinter.StringVar()
        project_window_combobox = ttk.Combobox(top_frame, textvariable=project_list)
        project_window_combobox.pack(side=RIGHT)
        project_window_combobox["value"] = ("chopin01", "chopin02", "chopin03", "DianDian01")
        project_window_combobox["state"] = "readonly"

        # 确认按钮
        choose_button = Button(bottom_frame, command=self.go_version_choose)
        choose_button["text"] = "确定"
        choose_button.pack(pady=40)

    def go_version_choose(self):
        self.root.destroy()
        VersionChooser()


class VersionChooser(object):
    def __init__(self):
        self.root = Tk()
        self.root.geometry("600x250+200+200")
        self.root.title("配置编辑器")
        self.set_version_window()

        self.root.mainloop()

    def set_version_window(self):
        top_frame = Frame(self.root)
        middle_frame = Frame(self.root)
        bottom_frame = Frame(self.root)
        top_frame.pack(side=TOP, ipady=30)
        bottom_frame.pack(side=BOTTOM, ipady=30)
        middle_frame.pack(ipady=30)

        tips_label = Label(top_frame, text="请选择对应版本：")
        tips_label.pack(side=LEFT)

        # 选择版本下拉框
        version_list = tkinter.StringVar()
        version_window_combobox = ttk.Combobox(top_frame, textvariable=version_list)
        version_window_combobox.pack(side=RIGHT)
        version_window_combobox["value"] = ("a-v2.2.0", "a-v2.3.0")

        choose_button = Button(bottom_frame, command=self.go_file_choose)
        choose_button["text"] = "确定"
        choose_button.pack(side=LEFT, padx=30)

        return_button = Button(bottom_frame, command=self.go_project_choose)
        return_button["text"] = "返回"
        return_button.pack(side=RIGHT,padx=30)

    def go_file_choose(self):
        self.root.destroy()
        FileChooser()

    def go_project_choose(self):
        self.root.destroy()
        ProjectChooser()


class FileChooser(object):
    def __init__(self):
        self.__files = []
        self.__root = ""
        self.__dirs = ()

        self.root = Tk()
        self.root.geometry("600x250+200+200")
        self.root.title("配置编辑器")
        self.set_file_window()

        self.root.mainloop()

    def reset(self):
        self.__files.clear()

    def set_file_window(self):
        self.top_frame = Frame(self.root)
        self.middle_frame = Frame(self.root)
        self.bottom_frame = Frame(self.root)
        self.top_frame.pack(side=TOP, ipady=30)
        self.bottom_frame.pack(side=BOTTOM, ipady=30)
        self.middle_frame.pack(ipady=30)

        self.tips_label = Label(self.top_frame, text="请选择要修改的配置文件：")
        self.tips_label.pack(side=LEFT)

        # 首次读取列表时更新
        if not self.__files:
            self.find_files_names()
        self.file_window_combobox = ttk.Combobox(self.top_frame, values=self.__files)
        self.file_window_combobox["state"] = "readonly"
        self.file_window_combobox.pack(side=RIGHT)
        self.file_window_combobox.current(0)

        self.choose_button = Button(self.bottom_frame, command=self.go_config_window)
        self.choose_button["text"] = "确定"
        self.choose_button.pack(side=LEFT, padx=30)

        self.return_button = Button(self.bottom_frame, command=self.go_version_choose)
        self.return_button["text"] = "返回"
        # self.return_button.pack(side=RIGHT, padx=30)

    def go_config_window(self):
        global select_file
        select_file = self.file_window_combobox.get()
        # if not select_file:
        #     messagebox.showinfo(message="没有挑选一个配置文件！")
        self.reset()
        self.root.destroy()
        ConfigChooser()

    def go_version_choose(self):
        self.reset()
        self.root.destroy()
        VersionChooser()

    def find_files_names(self):
        for root, dirs, files in os.walk("./CSV", topdown=False):
            for file in files:
                if file.endswith(".csv"):
                    self.__files.append(file)
                    # 将config_game.csv置顶
                    if "config_game.csv" in self.__files:
                        game_pos = self.__files.index("config_game.csv")
                        self.__files.remove("config_game.csv")
                        self.__files.insert(0, "config_game.csv")
            self.__root = root
            self.__dirs = list(dirs)

        #     # for name in files:
        #     #     print(os.path.join(root, name))

class ConfigChooser(object):
    def __init__(self):
        global select_file
        self.ce = ConfigEditor()
        self.root = Tk()
        self.root.geometry("600x250+200+200")
        self.root.title(select_file)
        self.set_config_window()

        self.root.mainloop()

    def set_config_window(self):
        self.top_frame = Frame(self.root)
        self.middle_frame = Frame(self.root)
        self.bottom_frame = Frame(self.root)

        self.top_frame.pack(side=TOP, ipady=30)
        self.top_left_frame = Frame(self.top_frame)
        self.top_left_frame.pack(side=LEFT)
        self.top_right_frame = Frame(self.top_frame)
        self.top_right_frame.pack(side=RIGHT, ipadx=20)

        self.bottom_frame.pack(side=BOTTOM, pady=20)
        self.middle_frame.pack()

        # 窗口顶部选择配置项
        self.tips_label = Label(self.top_left_frame, text="选择修改的配置项：")
        self.tips_label.pack(side=LEFT)

        self.config_name= Entry(self.top_left_frame, bg="grey")
        self.config_name.pack()

        self.choose_button = Button(self.top_right_frame, command=self.choose_config_name)
        self.choose_button["text"] = "确定"
        self.choose_button.pack(side=RIGHT)

        # 窗口中部读取配置项内容以及修改配置
        self.config_text = Text(self.middle_frame, bg="grey")
        self.config_text.pack(expand=YES)

        # 窗口底部按钮
        self.alter_button = Button(self.bottom_frame, command=self.alter_config)
        self.alter_button["text"] = "修改"
        self.alter_button.pack(side=LEFT, padx=20)
        self.alter_button.pack_forget()

        self.re_button = Button(self.bottom_frame, command=self.go_file_choose)
        self.re_button["text"] = "返回"
        self.re_button.pack(side=RIGHT, padx=20)

        pass

    def choose_config_name(self):
        global select_config
        global select_file

        select_config = self.config_name.get()

        file_first_name = select_file.split("_")[0]
        if file_first_name != "config":
            if file_first_name == "cms":
                ce.set_index_name("cms_index.json")
                ce.set_config_dir_name("./CSV/cms/")

        self.ce.set_config_file_name(select_file)
        self.ce.set_config_item_name(select_config)
        self.config_full_line = self.ce.find_config_by_name()
        self.config_text.delete(1.0, END)   #先清空
        self.config_text.insert(1.0, self.config_full_line)


        config_text = self.config_text.get(1.0, END)
        # 0是为空，1是文件末尾的换行符，所以大于1才出现修改的按钮
        if len(config_text) > 1:
            self.alter_button.pack()
        else:
            self.alter_button.pack_forget()

    def alter_config(self):
        """
        改变配置
        :return:
        """
        config_text = self.config_text.get(1.0, END)
        config_dic = ast.literal_eval(config_text)  # 将修改后的config改为字典格式
        key_list = config_dic.keys()

        with open("UI_tmp_config", "w", encoding="utf-8") as wfp:
            csv_writer = csv.DictWriter(wfp, fieldnames=key_list)
            csv_writer.writeheader()
            csv_writer.writerow(config_dic)

        if self.ce.alter_config_content_by_file("UI_tmp_config"):
            self.ce.auto_add_index_num()
            messagebox.showinfo(message="修改成功")

    def go_file_choose(self):
        self.root.destroy()
        FileChooser()


if __name__ == "__main__":
    # ProjectChooser()
    # VersionChooser()
    FileChooser()
    #ConfigChooser()
