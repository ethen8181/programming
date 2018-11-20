import os.path

def moveImages(blogText, blogHome):
    import re
    import shutil
    import datetime

    blogImgDir =  "blog/uploads/%s/" % datetime.datetime.now().year

    imgMdRegex = re.compile('!\[(.*)\]\((.*?)\)')
    allImgs = re.findall(imgMdRegex, blogText)
    for img in allImgs:
        pathMatch = img[1]
        copyPath = os.path.join(blogHome, blogImgDir)
        shutil.copy(pathMatch, copyPath)

    blogText = re.sub(imgMdRegex, '![\\1](/' + blogImgDir + '\\2)', blogText)
    return blogText


def parseArgs():
    import argparse
    parser = argparse.ArgumentParser(description='Publish Jupyter Notebook to OSC\'s blog')
    parser.add_argument('--markdown', type=argparse.FileType('r'), nargs=1, required=True)
    parser.add_argument('--bloghome', nargs=1, required=True)
    return parser.parse_args()



if __name__ == "__main__":
    args = parseArgs()
    blogText = args.markdown[0].read()
    blogHome = os.path.realpath(args.bloghome[0])
    moveImages(blogText, blogHome)
