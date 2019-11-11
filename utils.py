import random
import string


'''
生成num位数的随机字符串
'''


def gen_random_str(num):
    salt = ''.join(random.sample(string.ascii_letters + string.digits, num))
    print('随机字符串', salt)
    return salt
