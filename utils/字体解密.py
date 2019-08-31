import base64
import re
import requests
from io import BytesIO
from fontTools.ttLib import TTFont


# 字体解密
def font_secret():
    base64_str = ('AAEAAAALAIAAAwAwR1NVQiCLJXoAAAE4AAAAVE9TLzL4XQjtAAABjAAAAFZjbWFwq8N/'
                  'ZAAAAhAAAAIuZ2x5ZuWIN0cAAARYAAADdGhlYWQVzdUvAAAA4AAAADZoaGVhCtADIwAAA'
                  'LwAAAAkaG10eC7qAAAAAAHkAAAALGxvY2ED7gSyAAAEQAAAABhtYXhwARgANgAAARgAAAA'
                  'gbmFtZTd6VP8AAAfMAAACanBvc3QFRAYqAAAKOAAAAEUAAQAABmb+ZgAABLEAAAAABGgAA'
                  'QAAAAAAAAAAAAAAAAAAAAsAAQAAAAEAAOdD7y5fDzz1AAsIAAAAAADZI0UPAAAAANkjRQ8AAP/'
                  'mBGgGLgAAAAgAAgAAAAAAAAABAAAACwAqAAMAAAAAAAIAAAAKAAoAAAD/AAAAAAAAAAEAAAAKA'
                  'DAAPgACREZMVAAObGF0bgAaAAQAAAAAAAAAAQAAAAQAAAAAAAAAAQAAAAFsaWdhAAgAAAABAAAAA'
                  'QAEAAQAAAABAAgAAQAGAAAAAQAAAAEERAGQAAUAAAUTBZkAAAEeBRMFmQAAA9cAZAIQAAACAAUD'
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAFBmRWQAQJR2n6UGZv5mALgGZgGaAAAAAQAAAAAAAAAAAAA'
                  'EsQAABLEAAASxAAAEsQAABLEAAASxAAAEsQAABLEAAASxAAAEsQAAAAAABQAAAAMAAAAsAAAAB'
                  'AAAAaYAAQAAAAAAoAADAAEAAAAsAAMACgAAAaYABAB0AAAAFAAQAAMABJR2lY+ZPJpLnjqeo59'
                  'kn5Kfpf//AACUdpWPmTyaS546nqOfZJ+Sn6T//wAAAAAAAAAAAAAAAAAAAAAAAAABABQAFAAUA'
                  'BQAFAAUABQAFAAUAAAACAAGAAUABAAKAAIABwADAAEACQAAAQYAAAAAAAAAAAAAAAAAAAAAAAA'
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                  'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                  'AAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAiAAAAAAAAAAKAACUdgAAlHYAAAAIAACVjwAAlY8AA'
                  'AAGAACZPAAAmTwAAAAFAACaSwAAmksAAAAEAACeOgAAnjoAAAAKAACeowAAnqMAAAACAACfZAA'
                  'An2QAAAAHAACfkgAAn5IAAAADAACfpAAAn6QAAAABAACfpQAAn6UAAAAJAAAAAAAAACgAPgBmA'
                  'JoAvgDoASQBOAF+AboAAgAA/+YEWQYnAAoAEgAAExAAISAREAAjIgATECEgERAhIFsBEAECAez+6/'
                  'rs/v3IATkBNP7S/sEC6AGaAaX85v54/mEBigGB/ZcCcwKJAAABAAAAAAQ1Bi4ACQAAKQE1IREFN'
                  'SURIQQ1/IgBW/6cAicBWqkEmGe0oPp7AAEAAAAABCYGJwAXAAApATUBPgE1NCYjIgc1NjMyFhUU'
                  'AgcBFSEEGPxSAcK6fpSMz7y389Hym9j+nwLGqgHButl0hI2wx43iv5D+69b+pwQAAQAA/+YEGQYn'
                  'ACEAABMWMzI2NRAhIzUzIBE0ISIHNTYzMhYVEAUVHgEVFAAjIiePn8igu/5bgXsBdf7jo5CYy8bw/'
                  'sqow/7T+tyHAQN7nYQBJqIBFP9uuVjPpf7QVwQSyZbR/wBSAAACAAAAAARoBg0ACgASAAABIxEj'
                  'ESE1ATMRMyERNDcjBgcBBGjGvv0uAq3jxv58BAQOLf4zAZL+bgGSfwP8/CACiUVaJlH9TwABAAD/'
                  '5gQhBg0AGAAANxYzMjYQJiMiBxEhFSERNjMyBBUUACEiJ7GcqaDEx71bmgL6/bxXLPUBEv7a/v3Z'
                  'bu5mswEppA4DE63+SgX42uH+6kAAAAACAAD/5gRbBicAFgAiAAABJiMiAgMzNjMyEhUUACMiABEQ'
                  'ACEyFwEUFjMyNjU0JiMiBgP6eYTJ9AIFbvHJ8P7r1+z+8wFhASClXv1Qo4eAoJeLhKQFRj7+ov7'
                  'R1f762eP+3AFxAVMBmgHjLfwBmdq8lKCytAAAAAABAAAAAARNBg0ABgAACQEjASE1IQRN/aLLAk'
                  'D8+gPvBcn6NwVgrQAAAwAA/+YESgYnABUAHwApAAABJDU0JDMyFhUQBRUEERQEIyIkNRAlATQmIy'
                  'IGFRQXNgEEFRQWMzI2NTQBtv7rAQTKufD+3wFT/un6zf7+AUwBnIJvaJLz+P78/uGoh4OkAy+B9'
                  'avXyqD+/osEev7aweXitAEohwF7aHh9YcJlZ/7qdNhwkI9r4QAAAAACAAD/5gRGBicAFwAjAAA3'
                  'FjMyEhEGJwYjIgA1NAAzMgAREAAhIicTFBYzMjY1NCYjIga5gJTQ5QICZvHD/wABGN/nAQT+sP7'
                  'Xo3FxoI16pqWHfaTSSgFIAS4CAsIBDNbkASX+lf6l/lP+MjUEHJy3p3en274AAAAAABAAxgABAA'
                  'AAAAABAA8AAAABAAAAAAACAAcADwABAAAAAAADAA8AFgABAAAAAAAEAA8AJQABAAAAAAAFAAsAN'
                  'AABAAAAAAAGAA8APwABAAAAAAAKACsATgABAAAAAAALABMAeQADAAEECQABAB4AjAADAAEECQAC'
                  'AA4AqgADAAEECQADAB4AuAADAAEECQAEAB4A1gADAAEECQAFABYA9AADAAEECQAGAB4BCgADAA'
                  'EECQAKAFYBKAADAAEECQALACYBfmZhbmdjaGFuLXNlY3JldFJlZ3VsYXJmYW5nY2hhbi1zZWNy'
                  'ZXRmYW5nY2hhbi1zZWNyZXRWZXJzaW9uIDEuMGZhbmdjaGFuLXNlY3JldEdlbmVyYXRlZCBieS'
                  'BzdmcydHRmIGZyb20gRm9udGVsbG8gcHJvamVjdC5odHRwOi8vZm9udGVsbG8uY29tAGYAYQBu'
                  'AGcAYwBoAGEAbgAtAHMAZQBjAHIAZQB0AFIAZQBnAHUAbABhAHIAZgBhAG4AZwBjAGgAYQBuAC0A'
                  'cwBlAGMAcgBlAHQAZgBhAG4AZwBjAGgAYQBuAC0AcwBlAGMAcgBlAHQAVgBlAHIAcwBpAG8AbgAg'
                  'ADEALgAwAGYAYQBuAGcAYwBoAGEAbgAtAHMAZQBjAHIAZQB0AEcAZQBuAGUAcgBhAHQAZQBkACAA'
                  'YgB5ACAAcwB2AGcAMgB0AHQAZgAgAGYAcgBvAG0AIABGAG8AbgB0AGUAbABsAG8AIABwAHIAbwBq'
                  'AGUAYwB0AC4AaAB0AHQAcAA6AC8ALwBmAG8AbgB0AGUAbABsAG8ALgBjAG8AbQAAAAIAAAAAAAAA'
                  'FAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwECAQMBBAEFAQYBBwEIAQkBCgELAQwAAAAAAAAAAAAAAAAAAAAA')
    # url = 'https://bj.58.com/hezu/38239655311781x.shtml?shangquan=wanshouluhd'
    # res = requests.get(url)
    # base64_str = re.findall("charset=utf-8;base64,(.*?)'\)", res.text)[0]
    bin_data = base64.decodebytes(base64_str.encode())
    # 写入otf字体文件
    # font_file = 'D:/data/font.otf'
    # with open(font_file, 'wb') as f:
    #     f.write(bin_data)
    # 解析字体库
    # font = TTFont(font_file)
    # BytesIO() 把二进制数据bin_data当作文件来操作,TTFont接收一个文件类型
    font = TTFont(BytesIO(bin_data))
    # font.saveXML("text.xml")
    # uni_list = font['cmap'].tables[0].ttFont.getGlyphOrder()
    # c = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap
    c = font.getBestCmap()
    res_list = []
    text = '龒鸺龤龤'
    for i in text:
        if ord(i) in c:
            t = int(c[ord(i)][-2:])-1
        else:
            t = i
        res_list.append(t)
    crack_text = ''.join([str(i) for i in res_list])
    print(crack_text)


font_secret()


# 天眼查字体解密
# font = TTFont('D:/data/tyc-num.woff')
# font.saveXML('D:/data/tyc-num.xml')
with open('D:/data/tyc-num.xml') as f:
    xml = f.read()
GlyphID = re.findall(r'<GlyphID id="(.*?)" name="(\d+)"/>', xml)  # 获得对应关系
GlyphIDNameList = list(set([int(name) for gid, name in GlyphID]))  # 对应关系数量转换
DigitalDict = {str(i): str(GlyphIDNameList[i-2]) for i in range(2, len(GlyphIDNameList)+2)}  # 数字对应关系的字典推导式
GlyphIDDict = {str(name): DigitalDict[gid] for gid, name in GlyphID}  # 通过数字对应关系生成源代码跟页面显示的字典推导式
text = '8223458.540'
# true_text = list(map(lambda x: GlyphIDDict[x] if (x in GlyphIDDict) else x, text))
true_text = [GlyphIDDict[x] if (x in GlyphIDDict) else x for x in text]
true_text = ''.join(true_text)
print(true_text)
