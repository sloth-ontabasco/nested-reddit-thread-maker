import json
import pickle
import csv
import praw
import sys
import argparse

from os.path import exists
from anytree import NodeMixin,RenderTree,PostOrderIter
from anytree.search import findall_by_attr

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--delete", help="Delete all posts from pickle object", action="store_true"
)

if not exists('creds.json'):
    print('Cannot find credentials, please run setup.py and try again')
    sys.exit(1)

if not exists('info.json'):
    print('Cannot find post info, please run setup.py and try again')
    sys.exit(1)

with open('creds.json','r') as f:
    creds = json.load(f)

with open('info.json','r') as f:
    info = json.load(f)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])
 
subreddit = reddit.subreddit(info['subreddit'])


class ThreadPost(NodeMixin):
    def __init__(self,name,parent=None):
        super(ThreadPost,self).__init__()
        self.name = name
        self.parent = parent
        self.link_str = None
        self.post_obj = None
    

def parse_csv() -> ThreadPost:

    root = ThreadPost('Root',parent=None)
    with open(info['csv_file'],'r') as f:
        reader = csv.reader(f)

        curr_parent = root
        curr_heads = []

        next(reader)
        for row in next(reader):
            if row != '':
                post = ThreadPost(row,parent=curr_parent)
                curr_parent = post
                curr_heads.append(post)
            else:
                curr_heads.append(None)

        for row in reader:
            for n,value in enumerate(row):
                if n == 0 and value != '':
                    post = ThreadPost(value,parent=root)
                    curr_heads[n] = post
                elif value != '':
                    post = ThreadPost(value,parent=curr_heads[n-1])
                    curr_heads[n] = post

    for pre, _, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    return root


def generate_link_str(node: ThreadPost) -> str:

    """Create thread children link, if root node is given, 2 consecutive children are linked for visual appeal"""
    link_str = ''
    if node.depth == 0:
        for child in node.children:
            link_str += f"#{child.name}\n"
            for child2 in child.children:
                link_str += f"##[{child2.name}]({child2.post_obj.url})\n"
            link_str+='\n'

    else:
        link_str += f"#{node.name}\n" 
        for child in node.children:
            link_str += f"##[{child.name}]({child.post_obj.url})\n"

    return link_str


def create_post(node: ThreadPost, link_str=None) -> praw.models.Submission:

    """Create reddit post by accepting ThreadPost object and link_str"""

    print(f"Creating {node.name} thread.") 
    if node.is_leaf:
        title = info[str(-1)]['title'].replace('$NAME$',node.name)
        selftext = info[str(-1)]['description'].replace('$NAME$',node.name)
    else:
        title = info[str(node.depth)]['title'].replace('$NAME$',node.name)
        selftext = info[str(node.depth)]['description'].replace('$NAME$',node.name)
        selftext += '\n\n' + link_str
    node.link_str = link_str

    return subreddit.submit(title,selftext=selftext)


def save_object(root):
    """Save root into pickle"""
    print("Saving file..")
    with open('reddit_tree.pickle','wb') as f:
        pickle.dump(root,f)


def bottomup_thread_maker(root):
    """Start making threads from height 0 and up"""
    for node in root.leaves:
        node.post_obj = create_post(node) 

    for i in range(root.height-1,-1,-1):
        for node in findall_by_attr(root,i,name='depth'):
            if i == 1:
                continue
            elif not node.is_leaf:
                node.post_obj = create_post(node,link_str=generate_link_str(node))

def main():

    args = parser.parse_args()
    if args.delete:
        if not exists("reddit_tree.pickle"):
            print("No saved threads found. Run this script without the delete argument first")
            sys.exit(0)
        else:
            with open("reddit_tree.pickle",'rb') as f:
                root = pickle.load(f)
                for node in root.PostOrderIter():
                    node.post_obj.mod.approve()
                    node.post_obj.delete()

    root = parse_csv()
    bottomup_thread_maker(root)
    save_object(root)
    print("Success. Link to master thread: \n")
    print(root.post_obj.url)

if __name__ == '__main__':
    main()
