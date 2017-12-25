import os
import requests
from bs4 import BeautifulSoup
import threading
from bj.models import Video

# globals(repo_dir = './../tmp')
repo_dir = './../tmp/video'

# 定义请求数据的返回结果的函数
def get_response(url):
    # 为了防止被网站禁止访问，携带浏览器参数，假装浏览器请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # 取出返回的数据
    response =requests.get(url=url,headers=headers).content
    return response


# 解析网页数据获取视频描述和视频下载ｕｒｌ
def get_content_video(html):
# 通过ｂｓ４解析，用内置的解析器html.parser
    soup=BeautifulSoup(html,'html.parser')
    # 获取每个视频模块的信息
    cont=soup.select('.j-r-list-c')
    # 定义一个数组存放视频ｄｅｓｃ＋ｕｒｌ
    urlList=[]
    for item in cont:
        # 查找第一个a标签的内容，作为我们后面保存MP4的文件名
        name=item.find('a').text
        # 查找视频ｕｒｌ
        pmUrl=item.select('.j-video')[0].get('data-mp4')

        # 提取视频ｉｄ用于后期生成文件名
        video_id=item.select('.j-video')[0].get('data-id')
        #以元组的形式添加到数组
        urlList.append((name,pmUrl,video_id))
    return urlList

# 使用ｔｈｒｅａｄｉｎｇ异步下载视频
def download(urlList,page):
    #判断'./../tmp/vodeo'文件夹是否存在
    f_path=os.path.join(repo_dir,page)
    if not os._exists(f_path):
        print('路径不存在，马上创建!')
        os.makedirs(f_path)
    for item in urlList:
        #判断当前视频是否有ｕｒｌ
        if item[1] is None:
            continue
        # 创建视频的路径-->［－３：］截取文件名后缀
        f_path_video=os.path.join(f_path,'%s.%s'%(item[2],item[1][-3:]))

        #通过多线程的方式下载文件，增加下载速度
        thread=threading.Thread(target=save_video,args=(f_path_video,item[1]))
        #启动线程
        thread.start()

        #如果下载正常则将视频数据存入数据库中
        Video.objects.create(
            video_id=item[2],
            video_url=item[1],
            video_desc=item[0],
        )


# 正式下载视频文件
def save_video(f_path_video,video_url):
    response=get_response(video_url)#调用方法返回MP4文件的二进制流数据
    # 通过文件写入的方式保存成文件
    with open(f_path_video,'wb') as f:
        f.write(response)



#主函数
def main():
    for i in range(1,50):
        print("第" + i + "页")
        url = 'http://www.budejie.com/video/%s' % str(i)
        html = get_response(url)
        urlList=get_content_video(html)
        download(urlList,str(i))

#
# if __name__=="__main__":
#     main()


'''
    ** 由于我们这里仅用于测试，所以我们之抓取一页
    ** 链接最后的数字表示抓取的数据页码，由于首页的1可以不写，也可以写上
    ** 为了大家更好的理解多页的表示，这里我们仅抓取一页，并且链接后面写有页码1
'''
def test():
    url = 'http://www.budejie.com/video/1'
    html = get_response(url)
    urlList = get_content_video(html)
    download(urlList, str(1))