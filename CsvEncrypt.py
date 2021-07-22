#!/usr/local/bin/python3
import os
import hashlib
import sys
import base64
from Crypto.Cipher import AES
import random

"""
AES加密解密工具类
此工具类加密解密结果与 http://tool.chacuo.net/cryptaes 结果一致
数据块128位
key 为16位
iv 为16位，且与key相等
字符集utf-8
输出为base64
AES加密模式 为cbc
填充 pkcs7padding

pip3 install pycrypto
"""

def pkcs7padding(text):
    """
    明文使用PKCS7填充
    最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
    :param text: 待加密内容(明文)
    :return:
    """
    bs = AES.block_size  # 16
    length = len(text)
    bytes_length = len(bytes(text, encoding='utf-8'))
    # tips：utf-8编码时，英文占1个byte，而中文占3个byte
    padding_size = length if(bytes_length == length) else bytes_length
    padding = bs - padding_size % bs
    # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
    padding_text = chr(padding) * padding
    return text + padding_text


def pkcs7unpadding(text):
    """
    处理使用PKCS7填充过的数据
    :param text: 解密后的字符串
    :return:
    """
    length = len(text)
    unpadding = ord(text[length-1])
    return text[0:length-unpadding]


def encrypt(key, content):
    """
    AES加密
    key,iv使用同一个
    模式cbc
    填充pkcs7
    :param key: 密钥
    :param content: 加密内容
    :return:
    """
    key_bytes = bytes(key, encoding='utf-8')
    iv = key_bytes
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    # 处理明文
    content_padding = pkcs7padding(content)
    # 加密
    encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
    # 重新编码
    result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
    return result


def decrypt(key, content):
    """
    AES解密
     key,iv使用同一个
    模式cbc
    去填充pkcs7
    :param key:
    :param content:
    :return:
    """
    key_bytes = bytes(key, encoding='utf-8')
    iv = key_bytes
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    # base64解码
    encrypt_bytes = base64.b64decode(content)
    # 解密
    decrypt_bytes = cipher.decrypt(encrypt_bytes)
    # 重新编码
    result = str(decrypt_bytes, encoding='utf-8')
    # 去除填充内容
    result = pkcs7unpadding(result)
    return result


def get_key(n):
    """
    获取密钥 n 密钥长度
    :return:
    """
    c_length = int(n)
    source = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    length = len(source) - 1
    result = ''
    for i in range(c_length):
        result += source[random.randint(0, length)]
    return result

aes_key = 'NYcZGy55crYEWyyt'


current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

def save_to_file(file_path, contents):
   fh = open(file_path, 'w')
   fh.write(contents)
   fh.close()
   return

def get_encrypt_content(file_path):
    if os.path.isfile(file_path):
        f = open(file_path,'r', newline='')
        original_content = f.read()
        encrypt_content = encrypt(aes_key, original_content)
        f.close()
        return encrypt_content
    return None

def get_decrypt_content(file_path):
    if os.path.isfile(file_path):
        f = open(file_path,'r', newline='')
        original_content = f.read()
        encrypt_content = decrypt(aes_key, original_content)
        f.close()
        return encrypt_content
    return None

def encrypt_and_rewrite_files():
    print('encrypt_and_rewrite_files -- ')
    g = os.walk("./CSV")
    for path, dir_list, file_list in g:
        for file_name in file_list:
            if file_name == '.DS_Store':
                continue

            file_full_path = os.path.join(path, file_name)
            encrypt_content = get_encrypt_content(file_full_path)
            
            md5_obj = hashlib.md5()
            md5_obj.update(bytes(file_name, encoding='utf-8'))
            file_name_md5 = md5_obj.hexdigest() + '.txt'
            # print(f'file:{file_name} -> {file_name_md5}')
            
            save_to_file(os.path.join(path, file_name_md5), encrypt_content)
            os.remove(file_full_path)
         

def decrypt_and_rewrite_files():
    print('decrypt_and_rewrite_files -- ')
    g = os.walk("./CSV")
    for path, dir_list, file_list in g:
        for file_name in file_list:
            if file_name == '.DS_Store':
                continue
            if file_name.endswith('.txt') == False:
                continue
            file_full_path = os.path.join(path, file_name)
            decrypt_content = get_decrypt_content(file_full_path)
            
            file_name_raw = find_file_raw_name(file_name)
            # print(f'file:{file_name} -> {file_name_raw}')
            
            save_to_file(os.path.join(path, file_name_raw), decrypt_content)
            os.remove(file_full_path)

def find_file_raw_name(md5_name):
    # print(md5_name)
    raw_names = ['cms_index.json','cms_banner.csv','cms_category.csv','cms_column_gallery.csv',
                 'cms_dailyrec_local_jp.csv','cms_dailyrec_local.csv','cms_deep_link.csv','cms_language.csv',
                 'cms_picture_order.csv','cms_picture_send.csv','cms_picture_value_test.csv','cms_picture.csv',
                 'cms_premium_pic_send.csv','cms_push_daily_new.csv','cms_push_specific_date.csv','cms_topic.csv',
                 'config_bonus.csv','config_ciy_palette.csv','config_coreplay.csv','config_device_blacklist.csv',
                 'config_device.csv','config_feedback.csv','config_game.csv','config_os_blacklist.csv',
                 'config_paris_ad.csv','config_popup_queue.csv','config_premium.csv','config_quest_present.csv',
                 'config_quest.csv','config_region.csv','config_ui_bundle.csv','config_ui_effect.csv',
                 'config_ui_motion.csv','config_ui_res.csv','config_user_group.csv','config_index.json',
                 'config_achievement.csv','config_achievement.csv','config_action_relation.csv',
                 'config_coreplay_float.csv','config_cost.csv','config_drop.csv','config_item.csv','config_task.csv',
                 'config_action.csv']
       
    for raw_name in raw_names:
        md5_obj = hashlib.md5() 
        md5_obj.update(bytes(raw_name, encoding='utf-8')) 
        file_name_md5 = md5_obj.hexdigest() + '.txt'
        # print(f'raw_name: {raw_name}  file_name_md5: {file_name_md5}')
        if file_name_md5 == md5_name:
            return raw_name
    return f'{md5_name}.csv'

def test():
    mix_16 = 'abx张三丰12sa'
    encrypt_mixed = encrypt(aes_key, mix_16)
    print(encrypt_mixed)
    decrypt_mixed = decrypt(aes_key, encrypt_mixed)
    print(decrypt_mixed)
    print(decrypt_mixed == mix_16)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '2' or sys.argv[1] == 'f' or sys.argv[1] == 'decrypt':
            decrypt_and_rewrite_files()
        else:
            encrypt_and_rewrite_files()
    else:
        encrypt_and_rewrite_files()    
         
        
    

    


